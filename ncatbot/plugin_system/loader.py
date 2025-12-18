# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-03-21 18:06:59
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-08-04 15:49:02
# @Description  : 插件加载器
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
import asyncio
import importlib

# TODO 用 zipimport 实现 zip 格式插件
import sys
import toml
from collections import defaultdict, deque
from pathlib import Path
from types import ModuleType
from typing import Dict, List, Optional, Set, Type, Union, TYPE_CHECKING

from packaging.specifiers import SpecifierSet
from packaging.version import parse as parse_version

from ncatbot.utils import ncatbot_config

from .base_plugin import BasePlugin
from .event import EventBus
from .packhelper import PackageHelper
from .pluginsys_err import (
    PluginCircularDependencyError,
    PluginDependencyError,
    PluginVersionError,
    PluginNameConflictError,
)
from .config import config
from .rbac import RBACManager
from .builtin_plugin import SystemManager, UnifiedRegistryPlugin
from ncatbot.utils import get_log, status

if TYPE_CHECKING:
    import importlib.util

LOG = get_log("PluginLoader")
_AUTO_INSTALL = config.auto_install_pip_pack


# ---------------------------------------------------------------------------
# 工具函数 / 小类
# ---------------------------------------------------------------------------
class _ModuleImporter:
    """把「目录->模块对象」的细节收敛到这里，方便做单元测试。"""

    def __init__(self, directory: str):
        self.directory = Path(directory).resolve()

    def inspect_all(self) -> List[str]:
        """返回 {插件名: 模块对象}。"""
        plugin_folder_names: List[str] = []
        for entry in self.directory.iterdir():
            name = entry.stem
            if entry.is_dir() and (entry / "__init__.py").exists():
                name, path = entry.name, entry
            else:
                LOG.warning("跳过非插件文件/目录: %s", entry)
            plugin_folder_names.append(name)
        return plugin_folder_names

    def unload_module(self, name: str) -> bool:
        """
        卸载指定模块及其所有子模块

        Args:
            name: 模块完整名称，如 'plugins.my_plugin'

        Returns:
            bool: 是否成功卸载（若模块不存在也返回True）
        """
        if not name or not isinstance(name, str):
            LOG.warning("无效的模块名称: %s", name)
            return False

        # 收集目标模块及其所有子模块
        modules_to_remove = [
            module_name
            for module_name in list(sys.modules.keys())
            if module_name == name or module_name.startswith(f"{name}.")
        ]

        if not modules_to_remove:
            LOG.debug("模块 %s 未加载，无需卸载", name)
            return True

        # 执行卸载
        removed_count = 0
        for module_name in modules_to_remove:
            try:
                del sys.modules[module_name]
                removed_count += 1
                LOG.debug("已卸载模块: %s", module_name)
            except KeyError:
                pass  # 可能已被其他线程卸载

        LOG.info("成功卸载模块 %s (共 %d 个模块)", name, removed_count)
        return True

    def load_module(self, name: str, path: Path) -> Optional[ModuleType]:
        """
        加载模块并自动处理依赖

        Args:
            name: 模块名称
            path: 模块路径（文件或目录）

        Returns:
            加载成功的模块对象，失败返回 None
        """
        if not name or not path:
            LOG.error("模块名称或路径无效: name=%s, path=%s", name, path)
            return None

        if not path.exists():
            LOG.error("模块路径不存在: %s", path)
            return None

        try:
            # 清理旧版本，确保干净加载环境
            self.unload_module(name)

            # 自动安装依赖
            LOG.debug("正在检查并安装模块 %s 的依赖", name)
            self._maybe_install_deps(path)

            # 执行导入
            LOG.info("正在加载模块: %s from %s", name, path)
            module = self._import_single(name, path)
            LOG.info("模块 %s 加载成功", name)
            return module

        except Exception as e:
            LOG.error("加载模块 %s 失败: %s", name, e, exc_info=True)
            # 清理残留
            self.unload_module(name)
            return None

    # ------------------------------------------------------------------
    # 私有
    # ------------------------------------------------------------------
    def _import_single(self, name: str, path: Path) -> ModuleType:
        try:
            original_sys_path = sys.path.copy()
            sys.path.insert(0, str(path.parent))
            if path.is_dir():
                return importlib.import_module(name)
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            LOG.info("成功导入插件文件: %s", name)
            return module
        except Exception as e:
            LOG.error("导入模块 %s 时出错: %s", name, e)
            raise
        finally:
            sys.path = original_sys_path

    def _maybe_install_deps(self, plugin_path: Path) -> None:
        if not _AUTO_INSTALL:
            return

        def ensure_req_from_requirements():
            req_file = (
                plugin_path / "requirements.txt"
                if plugin_path.is_dir()
                else plugin_path.with_suffix(".requirements.txt")
            )
            if not req_file.exists():
                return

            for line in req_file.read_text(encoding="utf-8").splitlines():
                req = line.strip()
                if not req or req.startswith("#") or req.startswith("-"):
                    continue
                self._ensure_package(req)

        def ensure_req_from_pyproject():
            pyproject = (
                plugin_path / "pyproject.toml"
                if plugin_path.is_dir()
                else plugin_path.with_suffix(".pyproject.toml")
            )
            if not pyproject.exists():
                return
            data = toml.load(pyproject)
            requires = data.get("project", {}).get("dependencies", [])
            for req in requires:
                self._ensure_package(req)

        ensure_req_from_pyproject()
        ensure_req_from_requirements()

    def _ensure_package(self, req: str) -> None:
        """检查包是否存在，不存在则安装。"""
        PackageHelper.ensure(req)


class _DependencyResolver:
    """把「依赖图 -> 加载顺序」的逻辑独立出来，方便测试。"""

    def __init__(self) -> None:
        self._graph: Dict[str, Set[str]] = {}
        self._constraints: Dict[str, Dict[str, str]] = {}

    def build(self, plugin_classes: Dict[str, Type[BasePlugin]]) -> None:
        self._graph.clear()
        self._constraints.clear()
        for name, cls in plugin_classes.items():
            self._graph[name] = set(cls.dependencies.keys())
            self._constraints[name] = cls.dependencies.copy()

    def resolve(self) -> List[str]:
        """返回按依赖排序后的插件名；出错抛异常。"""
        self._check_duplicate_names()
        in_degree = {k: 0 for k in self._graph}
        adj = defaultdict(list)
        for cur, deps in self._graph.items():
            for d in deps:
                adj[d].append(cur)
                in_degree[cur] += 1

        q = deque([k for k, v in in_degree.items() if v == 0])
        order = []
        while q:
            cur = q.popleft()
            order.append(cur)
            for nxt in adj[cur]:
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    q.append(nxt)

        if len(order) != len(self._graph):
            raise PluginCircularDependencyError(set(self._graph) - set(order))
        return order

    # ------------------------------------------------------------------
    # 私有
    # ------------------------------------------------------------------
    def _check_duplicate_names(self) -> None:
        seen = set()
        for name in self._graph:
            if name in seen:
                raise PluginNameConflictError(name)
            seen.add(name)


# ---------------------------------------------------------------------------
# 主加载器
# ---------------------------------------------------------------------------
class PluginLoader:
    """插件加载器：负责插件的加载、卸载、重载、生命周期管理。"""

    """对于没有被任何插件依赖的插件，可以进行动态的加载和卸载"""

    def __init__(self, event_bus: EventBus, *, debug: bool = False) -> None:
        self.plugins: Dict[str, BasePlugin] = {}
        self.event_bus = event_bus or EventBus()
        self.rbac_manager = RBACManager(config.rbac_path)
        self._debug = debug
        self._importer = _ModuleImporter(str(ncatbot_config.plugin.plugins_dir))
        self._resolver = _DependencyResolver()

        # 将rbac_manager注册到全局状态
        status.global_access_manager = self.rbac_manager

        if debug:
            LOG.warning("插件系统已切换为调试模式")

    # -------------------- 对外 API --------------------
    async def _init_plugin_in_thread(self, plugin: BasePlugin) -> None:
        """在插件的线程中初始化"""

        def _run_init():
            # 在线程中创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # 运行初始化
                loop.run_until_complete(plugin.__onload__())
            finally:
                loop.close()

        # 在插件的线程池中执行初始化
        await asyncio.get_event_loop().run_in_executor(plugin.thread_pool, _run_init)

    async def load_plugin_by_class(
        self, plugin_class: Type[BasePlugin], name: str, **kwargs
    ) -> BasePlugin:
        plugin = plugin_class(
            event_bus=self.event_bus,
            debug=self._debug,
            rbac_manager=self.rbac_manager,
            plugin_loader=self,
        )
        plugin.name = name
        self.plugins[name] = plugin
        await self._init_plugin_in_thread(plugin)
        return plugin

    async def load_all_plugins_by_class(
        self, plugin_classes: Dict[str, Type[BasePlugin]], **kwargs
    ) -> None:
        """从「插件类对象」加载。"""
        print(plugin_classes)
        valid_classes = {
            name: cls for name, cls in plugin_classes.items() if self._is_valid(cls)
        }
        self._resolver.build(valid_classes)

        load_order = self._resolver.resolve()
        init_tasks = []

        for name in load_order:
            cls = valid_classes[name]
            LOG.info("加载插件「%s」", name)
            # 收集初始化任务
            init_tasks.append(self.load_plugin_by_class(cls, name, **kwargs))

        self._validate_versions()
        # 并发执行所有插件的初始化
        await asyncio.gather(*init_tasks)

    async def load_builtin_plugins(self) -> None:
        """加载内置插件。"""
        # 内置插件要在这里声明
        plugins = {
            "system_manager": SystemManager,
            "unified_registry": UnifiedRegistryPlugin,
        }
        for name, plg in plugins.items():
            await self.load_plugin_by_class(plg, name)
        LOG.info("已加载内置插件数 [%d]", len(self.plugins))

    async def load_plugins(self, **kwargs) -> None:
        """从目录批量加载。"""
        path = Path(ncatbot_config.plugin.plugins_dir).resolve()
        await self.load_builtin_plugins()
        if not path.exists():
            LOG.info("插件目录: %s 不存在……跳过加载插件", path)
            return

        if ncatbot_config.plugin.skip_plugin_load:
            LOG.info("跳过外部插件加载")
            return

        LOG.info("从 %s 导入插件", path)
        plugin_folder_names = self._importer.inspect_all()
        plugin_classes: Dict[str, Type[BasePlugin]] = {}
        importer = self._importer
        for name in plugin_folder_names:
            if (
                ncatbot_config.plugin.plugin_whitelist
                and name not in ncatbot_config.plugin.plugin_whitelist
            ):
                LOG.info("插件 '%s' 不在白名单中，跳过加载", name)
                continue
            if name in ncatbot_config.plugin.plugin_blacklist:
                LOG.info("插件 '%s' 在黑名单中，跳过加载", name)
                continue
            module = importer.load_module(name, path / name)
            if not module:
                continue
            cls = self._find_plugin_class_in_module(module)
            if not cls:
                # TODO: 支持多插件类/无插件类
                LOG.warning("在模块中未找到插件类 '%s'", name)
                continue
            plugin_classes[name] = cls

        await self.load_all_plugins_by_class(plugin_classes, **kwargs)
        LOG.info("已加载插件数 [%d]", len(self.plugins))
        # self._load_compatible_data()

    async def load_plugin(self, name) -> BasePlugin:
        try:
            module = self._importer.load_module(
                name, Path(ncatbot_config.plugin.plugins_dir) / name
            )
            return await self.load_plugin_by_class(
                self._find_plugin_class_in_module(module), name
            )
        except Exception as e:
            LOG.error(f"尝试加载失败的插件 {name}: {e}")

    async def unload_plugin(self, name: str, **kwargs) -> bool:
        """卸载单个插件。"""
        plugin = self.plugins.get(name)
        if not plugin:
            LOG.warning("插件 '%s' 未加载，无法卸载", name)
            return False
        try:
            await plugin.__unload__(**kwargs)
            self._importer.unload_module(name)
            del self.plugins[name]
            return True
        except Exception as e:
            LOG.error("卸载插件 '%s' 时发生错误: %s", name, e)
            return False

    async def reload_plugin(self, name: str, **kwargs) -> bool:
        """重载单个插件。"""
        try:
            await self.unload_plugin(name, **kwargs)
            await self.load_plugin(name)
            LOG.info("插件 '%s' 重载成功", name)
            return True
        except Exception as e:
            LOG.error("重载插件 '%s' 失败: %s", name, e)
            return False

    async def unload_all(self, **kwargs) -> None:
        """一键异步卸载全部插件。"""
        self.rbac_manager.save(config.rbac_path)
        await asyncio.gather(
            *(self.unload_plugin(name, **kwargs) for name in list(self.plugins))
        )

    # -------------------- 查询 API --------------------
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """根据插件名称获取插件实例。

        Args:
            name: 插件名称。

        Returns:
            插件实例；若不存在则返回 None。
        """
        return self.plugins.get(name, None)

    def get_metadata(self, name: str) -> dict:
        return self.plugins[name].meta_data

    def list_plugins(self, *, obj: bool = False) -> List[Union[str, BasePlugin]]:
        """插件列表

        Args:
            obj: 实例模式

        Returns:
            插件实例/插件名称列表
        """
        return list(self.plugins.values()) if obj else list(self.plugins.keys())

    # -------------------- 私有辅助 --------------------
    @staticmethod
    def _is_valid(cls: Type[BasePlugin]) -> bool:
        return all(hasattr(cls, attr) for attr in ("version", "dependencies"))

    def _validate_versions(self) -> None:
        """检查已加载插件的版本约束。"""
        for plugin_name, constraints in self._resolver._constraints.items():
            for dep_name, constraint in constraints.items():
                dep = self.plugins.get(dep_name)
                if not dep:
                    raise PluginDependencyError(plugin_name, dep_name, constraint)
                if not SpecifierSet(constraint).contains(parse_version(dep.version)):
                    raise PluginVersionError(
                        plugin_name, dep_name, constraint, dep.version
                    )

    def _find_plugin_class_in_module(
        self, module: ModuleType
    ) -> Optional[Type[BasePlugin]]:
        for obj in vars(module).values():
            if isinstance(obj, type) and issubclass(obj, BasePlugin):
                return obj
        return None
