# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-11 17:26:43
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-22 17:43:22
# @Description  : 导入好tm长啊
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
import asyncio
import importlib
import os
import re
import sys
import traceback
from collections import defaultdict, deque
from pathlib import Path
from types import MethodType, ModuleType
from typing import Dict, List, Set, Type

from packaging.specifiers import SpecifierSet
from packaging.version import parse as parse_version

from ncatbot.plugin.base_plugin import BasePlugin
from ncatbot.plugin.event import EventBus
from ncatbot.plugin.loader.compatible import CompatibleEnrollment
from ncatbot.plugin.loader.pip_tool import PipTool
from ncatbot.utils import (
    META_CONFIG_PATH,
    PLUGINS_DIR,
    PluginCircularDependencyError,
    PluginDependencyError,
    PluginNotFoundError,
    PluginVersionError,
    TimeTaskScheduler,
    UniversalLoader,
    get_log,
)
from ncatbot.utils.config import config

PM = PipTool()
LOG = get_log("PluginLoader")


def install_plugin_dependencies(plugin_name, confirm=False, print_import_details=True):
    directory_path = os.path.join(PLUGINS_DIR, plugin_name)
    if not os.path.exists(f"{directory_path}/requirements.txt"):
        return

    original_sys_path = sys.path.copy()
    download_new = False
    try:
        directory_path = os.path.abspath(directory_path)
        sys.path.append(os.path.dirname(directory_path))

        if os.path.isfile(os.path.join(directory_path, "requirements.txt")):
            requirements = [
                pack.strip().lower()
                for pack in open(
                    os.path.join(directory_path, "requirements.txt"), encoding="utf-8"
                ).readlines()
                if not pack.strip().startswith("#")
            ]
            # 检查指定版本号的依赖是否需要安装
            for pack in list(requirements):
                # 处理GitHub包（方法待实现）
                if pack.startswith(("git+", "http://", "https://", "git://", "ssh://")):
                    continue
                match = re.match(r"([^<>=~!]+)([<>=~!]=?|)(.+)", pack)
                if match:
                    pack_name = match.group(1).strip()
                    operator = match.group(2)
                    version = match.group(3).strip()

                    pack_info = PM.show_info(pack_name)
                    if pack_info:
                        installed_version = pack_info["version"]
                        LOG.info(
                            f"检查依赖: {pack_name} 已安装版本: {installed_version}, 需求: {operator}{version}"
                        )

                        if PM.compare_versions(
                            installed_version, f"{operator}{version}"
                        ):
                            requirements.remove(pack)

            requirements = set(requirements)
            all_install = {
                pack["name"].strip().lower()
                for pack in PM.list_installed()
                if "name" in pack
            }
            download = requirements - all_install
            if download:
                download_new = True
                LOG.warning(f'即将安装 {plugin_name} 中要求的库: {" ".join(download)}')
                if not confirm or input("是否安装(Y/n):").lower() in ("y", ""):
                    for pack in download:
                        LOG.info(f"开始安装库: {pack}")
                        PM.install(pack)

            try:
                importlib.import_module(plugin_name)
            except ImportError as e:
                if print_import_details:
                    LOG.error(f"导入模块 {plugin_name} 时出错: {e}")
                    LOG.info(traceback.format_exc())

        if download_new:
            LOG.warning("在某些环境中, 动态安装的库可能不会立即生效, 需要重新启动。")
    except Exception as e:
        LOG.error(f"安装插件 {plugin_name} 时出错: {e}")
        LOG.info(traceback.format_exc())
    finally:
        sys.path = original_sys_path


class PluginLoader:
    """
    插件加载器,用于加载、卸载和管理插件
    """

    def __init__(self, event_bus: EventBus):
        """
        初始化插件加载器
        """
        self.plugins: Dict[str, BasePlugin] = {}  # 存储已加载的插件
        self.event_bus = event_bus  # 事件总线
        self._dependency_graph: Dict[str, Set[str]] = {}  # 插件依赖关系图
        self._version_constraints: Dict[str, Dict[str, str]] = {}  # 插件版本约束
        self._debug = False  # 调试模式标记
        self.time_task_scheduler: TimeTaskScheduler = TimeTaskScheduler()
        if META_CONFIG_PATH:
            self.meta_data = UniversalLoader(META_CONFIG_PATH).load().data
        else:
            self.meta_data = {}

    def set_debug(self, debug: bool = False):
        """设置调试模式

        Args:
            debug: 是否启用调试模式
        """
        self._debug = debug
        LOG.warning("插件系统已切换为调试模式") if debug else None

    def _validate_plugin(
        self, plugin_cls: Type[BasePlugin], with_dependencies: bool = True
    ) -> bool:
        """
        验证插件类是否符合规范
        """
        # 检查基本属性
        if not all(hasattr(plugin_cls, attr) for attr in ["name", "version"]):
            return False

        # 检查依赖项属性
        if with_dependencies:
            if not hasattr(plugin_cls, "dependencies"):
                # 向后兼容：如果没有 dependencies 属性，添加一个空字典
                plugin_cls.dependencies = {}
            elif hasattr(plugin_cls, "requirements"):
                # 向后兼容：如果有 requirements 属性，将其复制到 dependencies
                plugin_cls.dependencies = plugin_cls.requirements

        return True

    def _build_dependency_graph(self, plugins: List[Type[BasePlugin]]):
        """
        构建插件依赖关系图
        """
        self._dependency_graph.clear()
        self._version_constraints.clear()

        for plugin in plugins:
            self._dependency_graph[plugin.name] = set(plugin.dependencies.keys())
            self._version_constraints[plugin.name] = plugin.dependencies.copy()

    def _validate_dependencies(self):
        """
        验证插件依赖关系是否满足
        """
        for plugin_name, deps in self._version_constraints.items():
            for dep_name, constraint in deps.items():
                if dep_name not in self.plugins:
                    raise PluginDependencyError(plugin_name, dep_name, constraint)

                installed_ver = parse_version(self.plugins[dep_name].version)
                if not SpecifierSet(constraint).contains(installed_ver):
                    raise PluginVersionError(
                        plugin_name, dep_name, constraint, installed_ver
                    )

    def _resolve_load_order(self) -> List[str]:
        """
        解析插件加载顺序,确保依赖关系正确
        """
        in_degree = {k: 0 for k in self._dependency_graph}
        adj_list = defaultdict(list)

        for dependent, dependencies in self._dependency_graph.items():
            for dep in dependencies:
                adj_list[dep].append(dependent)
                if dep not in self._dependency_graph.items():
                    LOG.error(f"插件 {dependent} 的依赖项 {dep} 不存在")
                    raise PluginNotFoundError(dep)
                in_degree[dependent] += 1

        queue = deque([k for k, v in in_degree.items() if v == 0])
        load_order = []

        while queue:
            node = queue.popleft()
            load_order.append(node)
            for neighbor in adj_list[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(load_order) != len(self._dependency_graph):
            missing = set(self._dependency_graph.keys()) - set(load_order)
            raise PluginCircularDependencyError(missing)

        return load_order

    def get_plugin_info(self, plugin_path):
        """获取插件的元信息

        Args:
            plugin_path: 插件路径

        Returns:
            tuple: (plugin_name, plugin_version, plugin_meta)
            plugin_meta 包含以下字段:
            - name: 插件名称
            - version: 插件版本
            - plugin_dependencies: 插件依赖的其他插件
            - description: 插件描述
            - author: 插件作者
            - info: 插件详细信息
            - funcs: 插件命令列表
            - configs: 插件配置项列表
        """
        import logging

        original_sys_path = sys.path.copy()
        logging.getLogger().setLevel(logging.WARNING)
        try:
            # 临时插入目录到 sys.path，用于加载模块
            directory_path = os.path.abspath(plugin_path)
            sys.path.append(os.path.dirname(directory_path))
            filename = Path(plugin_path).stem

            try:
                # 动态导入模块
                install_plugin_dependencies(filename)
                module = importlib.import_module(filename)

                if len(module.__all__) != 1:
                    raise ValueError("Plugin __init__.py wrong format")

                for plugin_class_name in module.__all__:
                    plugin_class = getattr(module, plugin_class_name)
                    if not self._validate_plugin(plugin_class, with_dependencies=False):
                        raise TypeError("Plugin Class is invalid")

                    # 获取基本信息
                    name = plugin_class.name
                    version = plugin_class.version

                    # 构建元信息
                    meta = {
                        "name": name,
                        "version": version,
                        "plugin_dependencies": (
                            plugin_class.dependencies
                            if hasattr(plugin_class, "dependencies")
                            else {}
                        ),
                        "description": getattr(
                            plugin_class,
                            "description",
                            "这个作者很懒且神秘,没有写一点点描述,真是一个神秘的插件",
                        ),
                        "author": getattr(plugin_class, "author", "Unknown"),
                        "info": getattr(plugin_class, "info", ""),
                        "funcs": [],
                        "configs": [],
                    }

                    # 尝试实例化插件以获取更多信息
                    try:
                        # 创建一个简单的事件总线模拟对象
                        class DummyEventBus:
                            def add_plugin(self, plugin):
                                pass

                            def subscribe(self, event_type, handler, priority=0):
                                pass

                            def access_controller(self):
                                pass

                            def unsubscribe(self, handler_id):
                                pass

                        # 创建一个简单的调度器模拟对象
                        class DummyScheduler:
                            def add_job(self, *args, **kwargs):
                                pass

                        # 实例化插件
                        plugin = plugin_class(
                            event_bus=DummyEventBus(),
                            time_task_scheduler=DummyScheduler(),
                            debug=False,
                            meta_data={},
                        )

                        # 执行 on_load
                        asyncio.run(plugin.__onload__())

                        # 获取功能列表
                        if hasattr(plugin, "_funcs"):
                            meta["funcs"] = [
                                {
                                    "name": func.name,
                                    "plugin_name": func.plugin_name,
                                    "description": getattr(func, "description", ""),
                                    "usage": getattr(
                                        func, "usage", f"/{func.name}" or ""
                                    ),
                                    "examples": getattr(func, "examples", []),
                                    "tags": getattr(func, "tags", []),
                                    "permission": func.permission,
                                    "permission_raise": func.permission_raise,
                                    "reply": func.reply,
                                    "metadata": getattr(func, "metadata", {}),
                                }
                                for func in plugin._funcs
                            ]

                        # 获取配置项列表
                        if hasattr(plugin, "_configs"):
                            meta["configs"] = [
                                {
                                    "name": conf.key,
                                    "full_key": conf.full_key,
                                    "default": conf.default,
                                    "type": (
                                        type(conf.default).__name__
                                        if conf.default is not None
                                        else "Any"
                                    ),
                                }
                                for conf in plugin._configs
                            ]

                        # 清理插件
                        asyncio.run(plugin.__unload__())

                    except Exception as e:
                        LOG.warning(f"无法加载插件 {name} 的完整信息: {e}")
                        LOG.warning("将只返回基本信息")

                    break

                if plugin_class_name != name or plugin_class_name != filename:
                    raise ValueError(
                        f"插件文件夹名 {filename}, 插件类名 {plugin_class_name}, 插件名 {name} 不匹配."
                    )

            except BaseException as e:
                LOG.error(f"查找模块 {filename} 时出错: {e}")
                return None, None, None

        finally:
            sys.path = original_sys_path
            logging.getLogger().setLevel(logging.DEBUG)

        return name, version, meta

    async def from_class_load_plugins(self, plugins: List[Type[BasePlugin]], **kwargs):
        """
        从插件类加载插件
        :param plugins: 插件类列表
        """

        def fix_plugin_dependencies():
            LOG.debug("正在修复插件依赖关系")
            for p in plugins:
                if not hasattr(p, "dependencies"):
                    LOG.debug(f"插件 {p.__name__} 缺少 dependencies 属性")
                    p.dependencies = {}

        try:
            fix_plugin_dependencies()
            LOG.debug("正在检查插件合法性")
            valid_plugins = [p for p in plugins if self._validate_plugin(p)]

            # 过滤掉不在白名单或黑名单中的插件
            filtered_plugins = []
            for plugin in valid_plugins:
                if config.is_plugin_enabled(plugin.name):
                    filtered_plugins.append(plugin)
                else:
                    LOG.info(f"插件 {plugin.name} 被白名单/黑名单过滤，跳过加载")

            valid_plugins = filtered_plugins

            LOG.debug("正在构建插件依赖图")
            self._build_dependency_graph(valid_plugins)
            load_order = self._resolve_load_order()
        except Exception as e:
            LOG.error(f"构造插件依赖图时出错: {e}")
            raise e

        temp_plugins = {}
        for name in load_order:
            try:
                LOG.debug(f"正在初始化插件 {name}")
                plugin_cls = next(p for p in valid_plugins if p.name == name)
                plugin = plugin_cls(
                    event_bus=self.event_bus,
                    time_task_scheduler=self.time_task_scheduler,
                    debug=self._debug,  # 传递调试模式标记
                    meta_data=self.meta_data.copy(),
                    **kwargs,
                )
                temp_plugins[name] = plugin

            except Exception as e:
                LOG.error(f"加载插件 {name} 时出错: {e}")
                LOG.info(traceback.format_exc())

        self.plugins = temp_plugins
        self._validate_dependencies()

        for name in load_order:
            await self.plugins[name].__onload__()
            self.event_bus.add_plugin(self.plugins[name])

    async def load_plugins(self, plugins_path: str = PLUGINS_DIR, **kwargs):
        """
        从指定目录加载插件
        :param plugins_path: 插件目录路径
        """
        if "api" not in kwargs:
            raise ValueError("缺少参数: api")
        self.event_bus.api = kwargs["api"]

        if not plugins_path:
            plugins_path = PLUGINS_DIR
        if os.path.exists(plugins_path):
            try:
                LOG.info(f"插件加载目录: {os.path.abspath(plugins_path)}")
                modules = self._load_modules_from_directory(plugins_path)
                plugins = []
                for plugin in modules.values():
                    for plugin_class_name in getattr(plugin, "__all__", []):
                        try:
                            plugins.append(getattr(plugin, plugin_class_name))
                        except Exception as e:
                            LOG.error(f"获取插件 {plugin.__name__} 时出错 {e}")
                LOG.info(f"准备加载插件 [{len(plugins)}]......")
                await self.from_class_load_plugins(plugins, **kwargs)
                LOG.info(f"已加载插件数 [{len(self.plugins)}]")
                LOG.debug("准备加载兼容内容......")
                self.load_compatible_data()
                LOG.debug("兼容内容加载成功")
            except Exception as e:
                LOG.error(f"加载插件 {plugin.__name__} 时出错: {e}")
                LOG.error(traceback.format_exc())
        else:
            LOG.info(
                f"插件目录: {os.path.abspath(plugins_path)} 不存在......跳过加载插件"
            )

    def load_compatible_data(self):
        """
        加载兼容注册事件
        """
        compatible = CompatibleEnrollment.events
        for event_type, packs in compatible.items():
            for func, priority, in_class in packs:
                if in_class:
                    for plugin_name, plugin in self.plugins.items():
                        if (
                            plugin.__class__.__qualname__
                            == func.__qualname__.split(".")[0]
                        ):
                            func = MethodType(func, plugin)
                            plugin.register_handler(event_type, func, priority)
                            break
                else:
                    LOG.warning("该方法即将弃用...")
                    self.event_bus.subscribe(event_type, func, priority)

    async def unload_plugin(self, plugin_name: str, *arg, **kwd):
        """
        卸载插件
        :param plugin_name: 插件名称
        """
        if plugin_name not in self.plugins:
            return

        self.event_bus.remove_plugin(self.plugins[plugin_name])
        await self.plugins[plugin_name].__unload__(*arg, **kwd)
        del self.plugins[plugin_name]

    async def reload_plugin(self, plugin_name: str):
        """
        重新加载插件
        :param plugin_name: 插件名称
        """
        if plugin_name not in self.plugins:
            raise ValueError(f"插件 '{plugin_name}' 未加载")

        LOG.info(f"开始重载插件: {plugin_name}")

        # 保存旧插件实例
        old_plugin = self.plugins[plugin_name]

        # 获取插件模块路径
        module_path = old_plugin.__class__.__module__

        try:
            # 卸载插件
            LOG.debug(f"卸载插件: {plugin_name}")
            await self.unload_plugin(plugin_name)

            # 导入模块
            LOG.debug(f"导入模块: {module_path}")
            module = importlib.import_module(module_path)

            # 强制重新加载
            LOG.debug(f"重新加载模块: {module_path}")
            importlib.reload(module)

            # 获取插件类
            plugin_class = None
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (
                    isinstance(item, type)
                    and issubclass(item, BasePlugin)
                    and hasattr(item, "name")
                    and item.name == plugin_name
                ):
                    plugin_class = item
                    break

            if not plugin_class:
                raise ValueError(f"无法在模块中找到插件类 '{plugin_name}'")

            # 验证插件类
            if not self._validate_plugin(plugin_class):
                raise ValueError(f"插件类 '{plugin_name}' 验证失败")

            # 创建新的插件实例
            LOG.debug(f"创建新插件实例: {plugin_name}")
            new_plugin = plugin_class(
                event_bus=self.event_bus,
                time_task_scheduler=self.time_task_scheduler,
                debug=self._debug,
                meta_data=self.meta_data.copy(),
                api=old_plugin.api,
            )

            # 加载插件
            LOG.debug(f"加载插件: {plugin_name}")
            await new_plugin.__onload__()

            # 添加到插件列表
            self.plugins[plugin_name] = new_plugin
            self.event_bus.add_plugin(new_plugin)

            LOG.info(f"插件 {plugin_name} 重载成功")
            return True

        except Exception as e:
            LOG.error(f"重载插件 {plugin_name} 时出错: {e}")
            LOG.error(traceback.format_exc())

            # 尝试恢复旧插件
            try:
                if plugin_name not in self.plugins:
                    self.plugins[plugin_name] = old_plugin
                    self.event_bus.add_plugin(old_plugin)
                    LOG.info(f"已恢复旧插件: {plugin_name}")
            except Exception as recovery_error:
                LOG.error(f"恢复旧插件 {plugin_name} 时出错: {recovery_error}")

            raise

    def _load_modules_from_directory(
        self, directory_path: str
    ) -> Dict[str, ModuleType]:
        """
        从指定文件夹动态加载模块,返回模块名到模块的字典。
        不修改 `sys.path`,仅在必要时临时添加路径。

        Args:
            directory_path: 插件加载路径, 一般就是插件名
        """
        modules = {}
        directory_path = os.path.abspath(directory_path)
        sys.path.append(directory_path)

        for filename in os.listdir(directory_path):
            if not os.path.isdir(os.path.join(directory_path, filename)):
                continue

            # 检查插件是否应该被加载
            if not config.is_plugin_enabled(filename):
                LOG.info(f"插件 {filename} 被白名单/黑名单过滤，跳过加载")
                continue
            if config.check_plugin_dependecies:
                install_plugin_dependencies(filename, print_import_details=False)
            try:
                module = importlib.import_module(filename)
                modules[filename] = module
            except Exception as e:
                LOG.error(f"加载插件 {filename} 时出错: {e}")
                LOG.error(traceback.format_exc())
                continue

        return modules

    def unload_all(self, *arg, **kwd):
        # 创建一个新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)  # 设置当前线程的事件循环

        try:
            # 创建任务列表
            self.event_bus.access_controller._save_access()
            tasks = [
                self.unload_plugin(plugin, *arg, **kwd)
                for plugin in self.plugins.keys()
            ]

            # 聚合任务并运行
            gathered = asyncio.gather(*tasks)
            loop.run_until_complete(gathered)
        except Exception as e:
            LOG.error(f"在卸载某个插件时产生了错误: {e}")
        finally:
            loop.close()
            # 关闭事件循环
