# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-03-21 18:06:59
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-05-23 20:12:17
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议 
# -------------------------
import asyncio
import importlib
import os
import sys

from collections import defaultdict, deque
from types import ModuleType
from typing import Dict, List, Set, Type
from packaging.specifiers import SpecifierSet
from packaging.version import parse as parse_version
from logging import getLogger

from .base_plugin import BasePlugin
from .event import EventBus
from .pip_tool import PipTool

from .pluginsys_err import (
    PluginCircularDependencyError,
    PluginDependencyError,
    PluginVersionError,
)
from .api import (
    PluginInfoMixin,
    COMPATIBLE_HANDLERS,
    PLUGINS_DIR,
    PluginSysApi
)

EPM = PipTool()
LOG = getLogger('PluginLoader')


class PluginLoader(PluginInfoMixin):
    """插件加载器,用于加载、卸载和管理插件。
    
    该类负责处理插件的完整生命周期管理，包括:
    - 插件的加载和初始化
    - 插件依赖关系的管理
    - 插件的版本控制
    - 插件的热重载
    - 插件的卸载清理
    
    Attributes:
        plugins (Dict[str, BasePlugin]): 存储已加载的插件实例
        event_bus (EventBus): 用于处理插件间事件通信的事件总线
    """

    def __init__(self, event_bus: EventBus):
        """初始化插件加载器。

        Args:
            event_bus (EventBus): 事件总线实例，用于处理插件间的事件通信
        """
        self.plugins: Dict[str, BasePlugin] = {}  # 存储已加载的插件
        self.event_bus = event_bus or EventBus()  # 事件总线
        self.sys_api = PluginSysApi(self)   # 系统级接口
        self._dependency_graph: Dict[str, Set[str]] = {}  # 插件依赖关系图
        self._version_constraints: Dict[str, Dict[str, str]] = {}  # 插件版本约束
        self._debug = False  # 调试模式标记

    def set_debug(self, debug: bool = False):
        """设置插件系统的调试模式。

        Args:
            debug (bool, optional): 是否启用调试模式。默认为 False

        Note:
            启用调试模式后会输出更详细的日志信息。
        """
        self._debug = debug
        LOG.warning("插件系统已切换为调试模式") if debug else None

    def _validate_plugin(self, plugin_cls: Type[BasePlugin]) -> bool:
        """验证插件类是否符合规范要求。

        Args:
            plugin_cls (Type[BasePlugin]): 待验证的插件类

        Returns:
            bool: 如果插件符合规范返回 True，否则返回 False
        """
        return all(
            hasattr(plugin_cls, attr) for attr in ("name", "version", "dependencies")
        )

    def _build_dependency_graph(self, plugins: List[Type[BasePlugin]]):
        """构建插件之间的依赖关系图。

        Args:
            plugins (List[Type[BasePlugin]]): 插件类列表

        Note:
            会同时更新依赖图(_dependency_graph)和版本约束(_version_constraints)
        """
        self._dependency_graph.clear()
        self._version_constraints.clear()

        for plugin in plugins:
            self._dependency_graph[plugin.name] = set(plugin.dependencies.keys())
            self._version_constraints[plugin.name] = plugin.dependencies.copy()

    def _validate_dependencies(self):
        """验证所有插件的依赖关系是否满足要求。

        Raises:
            PluginDependencyError: 当缺少某个依赖插件时抛出
            PluginVersionError: 当依赖插件的版本不满足要求时抛出
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
        """解析插件的加载顺序，确保依赖关系正确。

        Returns:
            List[str]: 按正确顺序排列的插件名称列表

        Raises:
            PluginCircularDependencyError: 当发现循环依赖时抛出
        """
        in_degree = {k: 0 for k in self._dependency_graph}
        adj_list = defaultdict(list)

        for dependent, dependencies in self._dependency_graph.items():
            for dep in dependencies:
                adj_list[dep].append(dependent)
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

    async def from_class_load_plugins(self, plugins: List[Type[BasePlugin]], **kwargs):
        """从插件类列表加载插件。

        Args:
            plugins (List[Type[BasePlugin]]): 待加载的插件类列表
            **kwargs: 传递给插件实例化的额外参数

        Raises:
            PluginDependencyError: 依赖检查失败时抛出
            PluginVersionError: 版本检查失败时抛出
        """
        valid_plugins = [p for p in plugins if self._validate_plugin(p)]
        self._build_dependency_graph(valid_plugins)
        load_order = self._resolve_load_order()

        temp_plugins = {}
        for name in load_order:
            plugin_cls = next(p for p in valid_plugins if p.name == name)
            temp_plugins[name] = plugin_cls(
                event_bus = self.event_bus,
                debug = self._debug,  # 传递调试模式标记 
                sys_api = self.sys_api,
                **kwargs
            )

        self.plugins = temp_plugins
        self._validate_dependencies()

        for name in load_order:
            await self.plugins[name].__onload__()

    async def load_plugins(self, plugins_path: str = PLUGINS_DIR, **kwargs):
        """从指定目录加载所有插件。

        Args:
            plugins_path (str, optional): 插件目录路径。默认为 PLUGINS_DIR
            **kwargs: 传递给插件实例化的额外参数
        """
        if not plugins_path: plugins_path = PLUGINS_DIR
        if os.path.exists(plugins_path):
            LOG.info(f"从 {os.path.abspath(plugins_path)} 导入插件")
            modules = self._load_modules_from_directory(plugins_path)
            plugins = []
            for plugin in modules.values():
                for plugin_class_name in getattr(plugin, "__all__", []):
                    plugins.append(getattr(plugin, plugin_class_name))
            LOG.info(f"准备加载插件 [{len(plugins)}]......")
            await self.from_class_load_plugins(plugins, **kwargs)
            LOG.info(f"已加载插件数 [{len(self.plugins)}]")
            LOG.info(f"准备加载兼容内容......")
            self.load_compatible_data()
            LOG.info(f"兼容内容加载成功")
        else:
            LOG.info(f"插件目录: {os.path.abspath(plugins_path)} 不存在......跳过加载插件")


    def load_compatible_data(self):
        """执行兼容性的自动行为，使用外部定义的兼容性处理器"""
        event_bus = self.event_bus
        for plugin_name, plugin in self.plugins.items():
            for attr_name in dir(plugin):
                func = getattr(plugin, attr_name)
                if not callable(func):
                    continue
                    
                # 遍历所有兼容性处理器
                for handler in COMPATIBLE_HANDLERS:
                    if handler.check(func):
                        handler.handle(plugin, func, event_bus)


    async def unload_plugin(self, plugin_name: str, **kwargs):
        """卸载指定的插件。

        Args:
            plugin_name (str): 要卸载的插件名称
            *arg: 传递给插件卸载方法的位置参数
            **kwd: 传递给插件卸载方法的关键字参数
        """
        if plugin_name not in self.plugins:
            LOG.warning(f"插件 '{plugin_name}' 未加载，无法卸载")
            return False
        
        try:
            await self.plugins[plugin_name].__unload__(**kwargs)
            del self.plugins[plugin_name]
            return True
        except Exception as e:
            LOG.error(f"卸载插件 '{plugin_name}' 时发生错误: {e}")
            return False

    async def reload_plugin(self, plugin_name: str, **kwargs):
        """重新加载指定的插件。

        Args:
            plugin_name (str): 要重新加载的插件名称
            
        Returns:
            bool: 重载是否成功
        
        Note:
            如果重载失败不会恢复插件
        """
        try:
            # 如果插件已加载，先卸载
            if plugin_name in self.plugins:
                old_plugin = self.plugins[plugin_name]
                if not await self.unload_plugin(plugin_name):
                    return False
                module_path = old_plugin.__class__.__module__
            else:
                # 搜索插件目录查找插件
                for dir_name in os.listdir(PLUGINS_DIR):
                    if os.path.isdir(os.path.join(PLUGINS_DIR, dir_name)):
                        module_path = dir_name

            try:
                module = importlib.import_module(module_path)
                importlib.reload(module)
            except ImportError as e:
                LOG.error(f"加载插件模块 '{module_path}' 失败: {e}")
                return False

            # 获取插件类
            plugin_class = None
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (isinstance(item, type)  
                    and issubclass(item, BasePlugin)  
                    and hasattr(item, 'name')  
                    and item.name == plugin_name):
                    plugin_class = item
                    break

            if not plugin_class:
                LOG.error(f"在模块中未找到插件 '{plugin_name}'")
                return False

            # 创建新的插件实例
            try:
                new_plugin = plugin_class(
                    event_bus = self.event_bus,
                    debug = self._debug,  # 传递调试模式标记 
                    sys_api = self.sys_api,
                    **kwargs
                )
                await new_plugin.__onload__()
                self.plugins[plugin_name] = new_plugin
                LOG.info(f"插件 '{plugin_name}' {'重载' if plugin_name in self.plugins else '加载'}成功")
                return True
            except Exception as e:
                LOG.error(f"初始化插件 '{plugin_name}' 失败: {e}")
                return False

        except Exception as e:
            LOG.error(f"{'重载' if plugin_name in self.plugins else '加载'}插件 '{plugin_name}' 时发生未知错误: {e}")
            return False

    def _load_modules_from_directory(
        self, directory_path: str
    ) -> Dict[str, ModuleType]:
        """从指定目录动态加载Python模块。

        Args:
            directory_path (str): 模块所在的目录路径

        Returns:
            Dict[str, ModuleType]: 模块名称到模块对象的映射字典

        Note:
            支持插件为包目录或单文件，自动处理依赖安装和导入路径
        """

        modules = {}
        original_sys_path = sys.path.copy()
        installed_packages = {pack['name'].strip().lower(): pack['version'] for pack in EPM.list_installed() if 'name' in pack}
        download_new = False

        try:
            directory_path = os.path.abspath(directory_path)
            sys.path.insert(0, directory_path)  # 插件目录优先

            for entry in os.listdir(directory_path):
                entry_path = os.path.join(directory_path, entry)
                # 只处理包目录或.py文件
                if os.path.isdir(entry_path) and os.path.isfile(os.path.join(entry_path, "__init__.py")):
                    plugin_name = entry
                    plugin_path = entry_path
                elif entry.endswith(".py") and os.path.isfile(entry_path):
                    plugin_name = entry[:-3]
                    plugin_path = entry_path
                else:
                    continue

                # 处理 requirements.txt
                req_file = os.path.join(plugin_path, "requirements.txt") if os.path.isdir(plugin_path) else plugin_path.replace(".py", ".requirements.txt")
                if os.path.isfile(req_file):
                    with open(req_file) as f:
                        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    for req in requirements:
                        if req.startswith('-'):
                            continue
                        # 处理git/url安装
                        if any(req.startswith(prefix) for prefix in ['git+', 'http:', 'https:']):
                            if input(f'发现特殊安装要求 {req}, 是否安装(Y/n):').lower() in ('y', ''):
                                LOG.info(f'开始安装: {req}')
                                EPM.install(req)
                            continue
                        # 解析包名和版本约束
                        if '==' in req:
                            pkg_name, version_constraint = req.split('==', 1)
                        elif '>=' in req:
                            pkg_name, version_constraint = req.split('>=', 1)
                        else:
                            pkg_name, version_constraint = req, None
                        pkg_name = pkg_name.lower()
                        if pkg_name in installed_packages:
                            if version_constraint:
                                current_ver = parse_version(installed_packages[pkg_name])
                                required_ver = parse_version(version_constraint)
                                if current_ver < required_ver:
                                    if input(f'包 {pkg_name} 当前版本 {current_ver} 低于要求的 {required_ver}, 是否更新(Y/n):').lower() in ('y', ''):
                                        LOG.info(f'更新包: {req}')
                                        EPM.install(req)
                                        download_new = True
                        else:
                            download_new = True
                            if input(f'发现未安装的依赖 {req}, 是否安装(Y/n):').lower() in ('y', ''):
                                LOG.info(f'开始安装: {req}')
                                EPM.install(req)

                # 动态导入模块
                try:
                    if os.path.isdir(plugin_path):
                        module = importlib.import_module(plugin_name)
                    else:
                        # 单文件插件
                        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[plugin_name] = module
                        spec.loader.exec_module(module)
                    modules[plugin_name] = module
                    LOG.info(f"成功导入插件模块: {plugin_name}")
                except Exception as e:
                    LOG.error(f"导入模块 {plugin_name} 时出错: {e}")
                    continue

            if download_new:
                LOG.warning('在某些环境中, 动态安装的库可能不会立即生效, 需要重新启动。')

        finally:
            sys.path = original_sys_path

        return modules

    def unload_all(self, *arg, **kwd):
        """卸载所有已加载的插件。

        Args:
            *arg: 传递给插件卸载方法的位置参数
            **kwd: 传递给插件卸载方法的关键字参数

        Note:
            会创建新的事件循环来处理异步卸载操作
        """
        # 创建一个新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)  # 设置当前线程的事件循环

        try:
            # 创建任务列表
            tasks = [self.unload_plugin(plugin, *arg, **kwd) for plugin in self.plugins.keys()]
            
            # 聚合任务并运行
            gathered = asyncio.gather(*tasks)
            loop.run_until_complete(gathered)
        except Exception as e:
            LOG.error(f"在卸载某个插件时产生了错误: {e}")
        finally:
            # 关闭事件循环
            loop.close()
