import asyncio
import pkgutil
import importlib
from typing import Union, Callable, Any, List, Dict, Optional, Tuple
from collections.abc import Iterable
from .Logger import get_logger, logging_redirect_tqdm,tqdm, Color
from packaging import version

_LOG = get_logger("Plugin Loader")


class EventBus:
    """
    事件总线，用于管理事件的订阅和发布。
    """
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event_type: str, listener: Callable):
        """
        订阅事件。
        :param event_type: 事件类型
        :param listener: 监听器函数
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)

    async def publish(self, event_type: str, *args, **kwargs):
        """
        发布事件，通知所有订阅了该事件的监听器。
        :param event_type: 事件类型
        :param args: 位置参数
        :param kwargs: 关键字参数
        """
        if event_type in self.listeners:
            tasks = [listener(*args, **kwargs) for listener in self.listeners[event_type]]
            await asyncio.gather(*tasks, return_exceptions=True)  # 等待所有任务完成，捕获异常


class PluginInterfaceBase:
    """
    插件基类，定义了插件的基本接口和属性。
    实际使用推荐继承 AsyncPluginInterface
    """
    __name__: str = "PluginInterfaceBase"
    __version__: str = "1.0.0"
    __author__: str = "Fish-lp"
    __dependencies__: List[str] = []  # 格式：插件名==版本号或版本范围(pip freeze)
    __config__: Optional[Dict[str, Any]] = None

    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._state = "initialized"

    def on_event(self, event_type: str, func: Callable):
        """
        订阅事件。
        :param event_type: 事件类型
        :param func: 监听器函数
        """
        self._event_bus.subscribe(event_type, func)

    def publish(self, event_type: str, *args, **kwargs):
        """
        发布事件。
        :param event_type: 事件类型
        :param args: 位置参数
        :param kwargs: 关键字参数
        """
        asyncio.create_task(self._event_bus.publish(event_type, *args, **kwargs))

    @property
    def name(self) -> str:
        return self.__name__

    @property
    def version(self) -> str:
        return self.__version__

    @property
    def author(self) -> str:
        return self.__author__

    @property
    def dependencies(self) -> List[str]:
        return self.__dependencies__

    @property
    def __config__(self) -> Optional[Dict[str, Any]]:
        return self.__config__

    @__config__.setter
    def __config__(self, new_config: Dict[str, Any]):
        self.__config__ = new_config
        asyncio.create_task(self.on_config_update())

    @property
    def state(self) -> str:
        return self._state

    async def on_load(self):
        """
        插件加载时的回调方法。
        """
        pass

    async def on_unload(self):
        """
        插件卸载时的回调方法。
        """
        pass

    async def on_error(self, error: Exception):
        """
        插件发生错误时的回调方法。
        """
        pass

    async def on_config_update(self):
        """
        插件配置更新时的回调方法。
        """
        pass


class AsyncPluginInterface(PluginInterfaceBase):
    """
    异步插件接口，继承自 PluginInterfaceBase。
    提供了异步初始化和关闭的方法。
    建议自行查看 PluginInterfaceBase 的实现
    """
    async def _init_(self, *args, **kwargs):
        """
        插件初始化方法，由子类实现。
        """
        raise NotImplementedError("插件必须实现 _init_ 方法")

    async def _close_(self):
        """
        插件关闭方法，由子类实现。
        """
        raise NotImplementedError("插件必须实现 _close_ 方法")


class AsyncPluginLoader:
    """
    异步插件加载器，负责动态加载插件模块，并初始化和关闭插件。
    """
    def __init__(self, package_name: str, event_bus: EventBus):
        self.package_name = package_name
        self.event_bus = event_bus
        self.plugins = {}
        self.loaded_plugin_names = set()
        self.plugin_versions = {}
        self.plugin_groups = {}  # 插件分组管理

    def _check_version_range(self, current_version: str, required_version: str) -> bool:
        """
        检查版本是否满足范围要求。
        """
        if required_version.startswith("=="):
            return current_version == required_version[2:]
        elif required_version.startswith(">="):
            return version.parse(current_version) >= version.parse(required_version[2:])
        elif required_version.startswith("<="):
            return version.parse(current_version) <= version.parse(required_version[2:])
        return False

    def _check_dependency_conflicts(self, plugins: Dict[str, type]) -> bool:
        """
        检查依赖冲突，并递归检查所有依赖的依赖。
        """
        def check_dependencies(plugin_name: str) -> bool:
            for dependency in plugins[plugin_name].__dependencies__:
                dep_name, dep_version = dependency.split("==")
                if dep_name not in self.plugin_versions:
                    if dep_name in plugins:
                        self.add_plugin(dep_name)  # 自动加载依赖插件
                    else:
                        _LOG.error(f"依赖插件 {dep_name} 未找到")
                        return False
                if not self._check_version_range(self.plugin_versions[dep_name], dep_version):
                    _LOG.error(f"插件 {plugin_name} 依赖的插件 {dep_name} 版本冲突")
                    return False
                if dep_name in plugins:
                    if not check_dependencies(dep_name):
                        return False
            return True

        for plugin_name in plugins:
            if not check_dependencies(plugin_name):
                return False
        return True

    async def load_plugins(self, group: Optional[str] = None, *args, **kwargs):
        """
        加载指定包中的插件模块。
        """
        package = importlib.import_module(self.package_name)
        _LOG.info(f'###################### 开始载入插件 ######################')
        plugin_num = 0
        total_plugins = 0

        # 收集所有插件
        all_plugins = {}
        for _, name, _ in pkgutil.iter_modules(package.__path__):
            if name.startswith('_'):
                continue
            module = importlib.import_module(f"{self.package_name}.{name}")
            for item in dir(module):
                obj = getattr(module, item)
                if (isinstance(obj, type) and 
                    issubclass(obj, AsyncPluginInterface) and 
                    obj is not AsyncPluginInterface):
                    all_plugins[obj.__name__] = obj  # 使用插件类的 __name__ 作为键
                    total_plugins += 1

        # 检查依赖冲突
        if not self._check_dependency_conflicts(all_plugins):
            _LOG.error("存在依赖冲突，无法加载插件")
            return

        # 按依赖关系排序插件
        sorted_plugins = self._sort_plugins_by_dependencies(all_plugins)

        # 加载插件
        with logging_redirect_tqdm():
            with tqdm(enumerate(sorted_plugins.items()),leave=False) as pbar:
                for idx, (name, plugin_class) in pbar:
                    if group and name not in self.plugin_groups.get(group, []):
                        continue

                    if name in self.loaded_plugin_names:
                        _LOG.warning(f"插件 {name} 已经加载过，跳过重复加载")
                        continue

                    plugin = plugin_class(self.event_bus)
                    plugin._state = "loading"
                    try:
                        await plugin._init_(*args, **kwargs)
                        await plugin.on_load()
                        self.plugins[plugin.name] = plugin  # 使用插件的 name 属性
                        self.loaded_plugin_names.add(plugin.name)  # 使用插件的 name 属性
                        self.plugin_versions[plugin.name] = plugin.version
                        plugin._state = "loaded"
                        plugin_num += 1
                        _LOG.info(f"[{Color.GREEN}{idx + 1}{Color.RESET}/{total_plugins}] 载入插件: {Color.YELLOW}{plugin.name}{Color.RESET}[{plugin.version}]")
                    except Exception as e:
                        plugin._state = "error"
                        await plugin.on_error(e)
                        _LOG.error(f"加载插件 {Color.YELLOW}{name}{Color.RESET} 时发生错误: {Color.RED}{e}{Color.RESET}", exc_info=True)

        _LOG.info(f'###################### 插件加载完成 #### [共载入 {plugin_num} 个插件]')

    def _sort_plugins_by_dependencies(self, plugins: Dict[str, type]) -> Dict[str, type]:
        """
        根据插件的依赖关系对插件进行排序。
        """
        sorted_plugins = {}
        while plugins:
            for name, plugin_class in list(plugins.items()):
                dependencies = plugin_class.__dependencies__
                if all(dep.split("==")[0] in sorted_plugins for dep in dependencies):
                    sorted_plugins[name] = plugin_class
                    del plugins[name]
        return sorted_plugins

    async def shutdown_plugins(self, group: Optional[str] = None):
        """
        关闭所有已加载的插件。
        """
        for plugin_name, plugin in list(self.plugins.items()):
            if group and plugin_name not in self.plugin_groups.get(group, []):
                continue
            plugin._state = "unloading"
            try:
                await plugin.on_unload()
                await plugin._close_()
                plugin._state = "unloaded"
                _LOG.info(f"插件 {plugin.name} 已关闭")
                if plugin_name in self.loaded_plugin_names:
                    self.loaded_plugin_names.remove(plugin_name)
                else:
                    _LOG.warning(f"插件 {plugin_name} 不在已加载列表中")
            except Exception as e:
                plugin._state = "error"
                await plugin.on_error(e)
                _LOG.error(f"关闭插件 {plugin.name} 时发生错误: {e}", exc_info=True)

    async def add_plugin(self, plugin_name: str, *args, **kwargs):
        """
        动态添加插件。
        """
        if plugin_name in self.loaded_plugin_names:
            _LOG.warning(f"插件 {plugin_name} 已经加载过，跳过重复加载")
            return

        module = importlib.import_module(f"{self.package_name}.{plugin_name}")
        for item in dir(module):
            obj = getattr(module, item)
            if (isinstance(obj, type) and 
                issubclass(obj, AsyncPluginInterface) and 
                obj is not AsyncPluginInterface):
                plugin = obj(self.event_bus)
                plugin._state = "loading"
                try:
                    await plugin._init_(*args, **kwargs)
                    await plugin.on_load()
                    self.plugins[plugin.name] = plugin
                    self.loaded_plugin_names.add(plugin_name)
                    self.plugin_versions[plugin.name] = plugin.version
                    plugin._state = "loaded"
                    _LOG.info(f'载入插件: {plugin.name}[{plugin.version}]')
                except Exception as e:
                    plugin._state = "error"
                    await plugin.on_error(e)
                    _LOG.error(f"加载插件 {plugin_name} 时发生错误: {e}", exc_info=True)

    async def reload_plugin(self, plugin_name: str, *args, **kwargs):
        """
        动态重新加载插件。
        """
        if plugin_name not in self.loaded_plugin_names:
            _LOG.warning(f"插件 {plugin_name} 未加载，无法重新加载")
            return

        plugin = self.plugins[plugin_name]
        plugin._state = "reloading"
        try:
            module = importlib.import_module(f"{self.package_name}.{plugin_name}")
            importlib.reload(module)
            _LOG.info(f"重新加载模块: {plugin_name}")
        except Exception as e:
            plugin._state = "error"
            _LOG.error(f"重新加载模块 {plugin_name} 时发生错误: {e}", exc_info=True)
            return

        for item in dir(module):
            obj = getattr(module, item)
            if (isinstance(obj, type) and 
                issubclass(obj, AsyncPluginInterface) and 
                obj is not AsyncPluginInterface):
                new_plugin_class = obj
                break
        else:
            plugin._state = "error"
            _LOG.error(f"重新加载后未找到插件类: {plugin_name}")
            return

        if new_plugin_class.__version__ != plugin.version:
            _LOG.warning(f"插件 {plugin_name} 的版本号已更改，可能需要重新初始化")

        new_plugin = new_plugin_class(self.event_bus)
        new_plugin._state = plugin._state
        new_plugin.__config__ = plugin.config
        self.plugins[plugin_name] = new_plugin
        plugin._state = "loaded"
        _LOG.info(f"插件 {plugin_name} 已重新加载")

    async def hot_reload_plugin(self, plugin_name: str, *args, **kwargs):
        """
        动态热更新插件。
        """
        if plugin_name not in self.plugins:
            _LOG.warning(f"插件 {plugin_name} 未加载，无法热更新")
            return

        plugin = self.plugins[plugin_name]
        plugin._state = "reloading"
        try:
            module = importlib.import_module(f"{self.package_name}.{plugin_name}")
            importlib.reload(module)
            _LOG.info(f"热更新模块: {plugin_name}")
        except Exception as e:
            plugin._state = "error"
            _LOG.error(f"热更新模块 {plugin_name} 时发生错误: {e}", exc_info=True)
            return

        for item in dir(module):
            obj = getattr(module, item)
            if (isinstance(obj, type) and 
                issubclass(obj, AsyncPluginInterface) and 
                obj is not AsyncPluginInterface):
                new_plugin_class = obj
                break
        else:
            plugin._state = "error"
            _LOG.error(f"热更新后未找到插件类: {plugin_name}")
            return

        # 替换插件实例
        new_plugin = new_plugin_class(self.event_bus)
        new_plugin._state = plugin._state
        new_plugin.__config__ = plugin.config
        self.plugins[plugin_name] = new_plugin
        _LOG.info(f"插件 {plugin_name} 已热更新")

    def create_plugin_group(self, group_name: str):
        """
        创建一个新的插件分组。
        """
        if group_name in self.plugin_groups:
            _LOG.warning(f"分组 {group_name} 已存在")
            return
        self.plugin_groups[group_name] = []
        _LOG.info(f"创建插件分组: {group_name}")

    def move_plugin_to_group(self, plugin_name: str, from_group: str, to_group: str):
        """
        将插件从一个分组移动到另一个分组。
        """
        if plugin_name not in self.plugin_groups.get(from_group, []):
            _LOG.warning(f"插件 {plugin_name} 不在分组 {from_group} 中")
            return
        if to_group not in self.plugin_groups:
            _LOG.warning(f"目标分组 {to_group} 不存在")
            return
        self.plugin_groups[from_group].remove(plugin_name)
        self.plugin_groups[to_group].append(plugin_name)
        _LOG.info(f"插件 {plugin_name} 已从分组 {from_group} 移动到 {to_group}")