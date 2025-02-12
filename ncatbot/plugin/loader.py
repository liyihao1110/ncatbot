"""
具有事件处理能力的插件系统

Raises:
    ValueError：未提供插件名称或版本时引发。
    PluginDependencyError：缺少插件依赖项时引发。
    PluginVersionError：当插件版本不符合所需版本时引发。
    PluginCircularDependencyError：当插件之间存在循环依赖关系时引发。
"""

import functools
import importlib
import os
import sys
from collections import defaultdict, deque
from types import ModuleType
from typing import (
    Dict,
    List,
    Set,
    Type,
)

from packaging.specifiers import SpecifierSet
from packaging.version import parse as parse_version

from ncatbot.core.api import BotAPI
from ncatbot.plugin.base_plugin import BasePlugin
from ncatbot.plugin.config import PLUGINS_DIR
from ncatbot.plugin.custom_err import (
    PluginCircularDependencyError,
    PluginDependencyError,
    PluginVersionError,
)
from ncatbot.plugin.event import CompatibleEnrollment, Event, EventBus
from ncatbot.utils.logger import get_log

_log = get_log()


# region ----------------- 插件加载器 -----------------
class PluginLoader:
    """
    插件加载器,用于加载、卸载和管理插件
    """

    def __init__(self):
        """
        初始化插件加载器
        """
        self.plugins: Dict[str, BasePlugin] = {}
        self.event_bus = EventBus()
        self._dependency_graph: Dict[str, Set[str]] = {}
        self._version_constraints: Dict[str, Dict[str, str]] = {}

    def _validate_plugin(self, plugin_cls: Type[BasePlugin]) -> bool:
        """
        验证插件类是否符合规范
        """
        return all(
            hasattr(plugin_cls, attr) for attr in ("name", "version", "dependencies")
        )

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
        # 遍历所有插件及其版本约束
        for plugin_name, deps in self._version_constraints.items():
            # 遍历当前插件的所有依赖项及其版本约束
            for dep_name, constraint in deps.items():
                # 检查依赖项是否存在于已安装的插件中
                if dep_name not in self.plugins:
                    raise PluginDependencyError(plugin_name, dep_name)

                # 获取已安装依赖项的版本
                installed_ver = parse_version(self.plugins[dep_name].version)
                # 检查已安装版本是否满足版本约束
                if not SpecifierSet(constraint).contains(installed_ver):
                    raise PluginVersionError(
                        dep_name, plugin_name, constraint, installed_ver
                    )

    def _resolve_load_order(self) -> List[str]:
        """
        解析插件加载顺序,确保依赖关系正确
        """
        in_degree = {k: 0 for k in self._dependency_graph}
        adj_list = defaultdict(list)

        # 遍历依赖图,构建入度表和邻接表
        for dependent, dependencies in self._dependency_graph.items():
            # dependent 是当前插件,dependencies 是它依赖的插件列表
            for dep in dependencies:
                adj_list[dep].append(dependent)
                in_degree[dependent] += 1

        queue = deque([k for k, v in in_degree.items() if v == 0])
        load_order = []

        # 拓扑排序
        while queue:
            node = queue.popleft()
            load_order.append(node)
            # 遍历该插件的所有依赖者
            for neighbor in adj_list[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # 检测是否存在循环依赖
        for plugin_name, dependency in self._dependency_graph.items():
            if not dependency.issubset(self._dependency_graph.keys()):
                raise PluginDependencyError(plugin_name, dependency)

        if len(load_order) != len(self._dependency_graph):
            missing = set(self._dependency_graph.keys()) - set(load_order)
            # 抛出异常,提示循环依赖的插件
            raise PluginCircularDependencyError(missing)

        # 返回最终的加载顺序
        return load_order

    async def from_class_load_plugins(
        self, plugins: List[Type[BasePlugin]], api: BotAPI
    ):
        """
        加载插件
        :param plugins: 插件类列表
        """
        valid_plugins = [p for p in plugins if self._validate_plugin(p)]
        self._build_dependency_graph(valid_plugins)
        load_order = self._resolve_load_order()

        # 实例化所有插件
        temp_plugins = {}
        for name in load_order:
            plugin_cls = next(p for p in valid_plugins if p.name == name)
            temp_plugins[name] = plugin_cls(self.event_bus, api)
        # 验证依赖版本
        self.plugins = temp_plugins
        self._validate_dependencies()

        # 初始化插件
        for name in load_order:
            await self.plugins[name].on_load()

    async def load_plugin(self, api: BotAPI):
        if not os.path.exists(PLUGINS_DIR):
            _log.info("插件目录不存在, 跳过插件加载")
            return
        models: Dict = self._load_modules_from_directory(directory_path=PLUGINS_DIR)
        plugins = []
        for plugin in models.values():
            for plugin_class_name in plugin.__all__:
                plugins.append(getattr(plugin, plugin_class_name))
        await self.from_class_load_plugins(plugins, api)
        self.load_compatible_data(self.plugins.values())
        return self.plugins.values()

    def load_compatible_data(self, plugins):
        def find_instance(func):
            plugin_name = func.__qualname__.split(".")[0]
            for plugin in plugins:
                if plugin.__class__.__name__ == plugin_name:
                    return plugin

        """加载兼容注册事件"""
        _log.debug("加载兼容注册事件")
        compatible = CompatibleEnrollment.events
        for event_type, funcs in compatible.items():
            for func in funcs:
                instance = find_instance(func)
                _log.debug(f"为 {instance.__class__.__name__} 订阅事件 {event_type}")
                self.event_bus.subscribe(event_type, functools.partial(func, instance))

    async def unload_plugin(self, plugin_name: str):
        """
        卸载插件
        :param plugin_name: 插件名称
        """
        if plugin_name not in self.plugins:
            return

        await self.plugins[plugin_name]._close_()
        await self.plugins[plugin_name].on_unload()
        del self.plugins[plugin_name]

    async def reload_plugin(self, plugin_name: str):
        """
        重新加载插件
        :param plugin_name: 插件名称
        """
        if plugin_name not in self.plugins:
            # 有点想报个错
            pass

        old = self.plugins[plugin_name]
        await old._close_()

        module = importlib.import_module(old.__class__.__module__)
        importlib.reload(module)

        new_cls = getattr(module, old.__class__.name)
        new_plugin = new_cls(old.event_bus)
        await new_plugin.on_load()
        self.plugins[plugin_name] = new_plugin

    def get_plugin_info(self, plugin_path):

        original_sys_path = sys.path.copy()
        try:
            # 临时插入目录到 sys.path，用于加载模块
            directory_path = os.path.abspath(plugin_path)
            sys.path.append(os.path.dirname(directory_path))
            filename = plugin_path.split("/")[-1]
            try:
                # 动态导入模块
                module = importlib.import_module(filename)
                if len(module.__all__) != 1:
                    raise ValueError("Plugin __init__.py wrong format")
                for plugin_class_name in module.__all__:
                    plugin_class = getattr(module, plugin_class_name)
                    if not self._validate_plugin(plugin_class):
                        raise TypeError("Plugin Class is invalid")
                    name, version = plugin_class.name, plugin_class.version
                    break
            except BaseException as e:
                _log.error(f"查找模块 {filename} 时出错: {e}")

        finally:
            sys.path = original_sys_path

        return name, version

    def _load_modules_from_directory(
        self, directory_path: str
    ) -> Dict[str, ModuleType]:
        """
        从指定文件夹动态加载模块，返回模块名到模块的字典。
        不修改 `sys.path`，仅在必要时临时添加路径。
        """
        # 存储模块的字典
        modules = {}

        # 避免重复添加目录到 sys.path
        original_sys_path = sys.path.copy()

        try:
            # 临时插入目录到 sys.path，用于加载模块
            directory_path = os.path.abspath(directory_path)
            sys.path.append(directory_path)

            # 遍历文件夹中的所有文件
            for filename in os.listdir(directory_path):
                # 忽略非文件夹
                if not os.path.isdir(os.path.join(directory_path, filename)):
                    continue
                # 异常捕获，防止导入失败导致程序崩溃
                try:
                    # 动态导入模块
                    module = importlib.import_module(filename)
                    modules[filename] = module
                except ImportError as e:
                    _log.error(f"导入模块 {filename} 时出错: {e}")
                    continue

        finally:
            # 恢复原 sys.path，移除临时路径
            sys.path = original_sys_path

        # 返回所有加载成功的模块字典
        return modules


# endregion

__all__ = ["PluginLoader", "Event"]
