import asyncio
import inspect
import os
from collections import defaultdict
from dataclasses import field
from pathlib import Path
from types import MappingProxyType
from typing import (
    Any,
    Callable,
    Dict,
    List,
)
from weakref import WeakMethod, ref

from ncatbot.core.api import BotAPI
from ncatbot.plugin.config import META_CONFIG_PATH, PERSISTENT_DIR
from ncatbot.plugin.custom_err import PluginSystemError
from ncatbot.plugin.event import Event, EventBus
from ncatbot.utils.io import UniversalLoader


# region ----------------- 插件基类 -----------------
class BasePlugin:
    """
    插件基类，所有插件应继承此类
    目前使用插件名称区分插件
    @todo 考虑使用插件id

    没有非常严格的限制，请开发者注意
    事件_发布_为防止冲突格式为f"{self.name}.{event_type}"
    """

    name: str = field(default_factory=str)
    version: str = field(default_factory=str)
    dependencies: Dict[str, str] = {}  # 插件名: 版本需求
    meta_data: Dict[str, Any]  # 只读字典(非强制)
    data: Dict[str, Any] = field(default_factory=dict)  # 插件系统维护: 每个插件独立
    lock = (
        asyncio.Lock()
    )  # 资源保护: 使用 with self.lock: 来确保对共享资源的访问是线程安全的

    def __init__(self, event_bus: EventBus, api: BotAPI, **kwargs):
        """
        初始化插件,绑定事件总线
        """
        self.api = api
        self.work_path = Path(os.path.abspath(PERSISTENT_DIR)) / self.name
        try:
            self.work_path.mkdir(parents=True, exist_ok=True)
            self.fist_load = True
        except FileExistsError:
            self.fist_load = False
        self.data = self._load_persistent_data()
        self.event_bus = event_bus
        if META_CONFIG_PATH:
            self.meta_data: Dict[str, Any] = MappingProxyType(
                UniversalLoader(META_CONFIG_PATH).load().data
            )  # 只读字典
        else:
            self.meta_data: Dict = MappingProxyType({})
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        if kwargs:
            for key, var in kwargs:
                setattr(self, key, var)
        os.chdir(self.work_path)

    def _load_persistent_data(self) -> Dict:
        """
        加载插件的私有数据
        """
        data_dir = self.work_path
        file_path = data_dir / f"{self.name.title()}.json"

        if not file_path.exists():
            return {}

        try:
            return UniversalLoader(file_path)
        except Exception as e:
            PluginSystemError(f"加载数据时出错（{self.name}）: {e}")
            return {}

    def _save_persistent_data(self):
        """
        保存插件的私有数据
        """
        data_dir = Path(PERSISTENT_DIR)
        data_dir.mkdir(parents=True, exist_ok=True)
        file_path = data_dir / f"{self.name.title()}.yaml"

        try:
            with UniversalLoader(file_path) as f:
                f: UniversalLoader
                f.data = self.data
                f.save()
        except Exception as e:
            PluginSystemError(f"保存数据时出错（{self.name}）: {str(e)}")

    async def publish_sync(self, event: Event) -> List[Any]:
        """
        发布事件,等待事件处理完成
        :param event: 要发布的事件对象
        :return: 事件处理结果列表
        """
        return self.event_bus.publish_sync(event)

    async def publish_async(self, event: Event) -> None:
        """
        发布事件,不等待事件处理完成
        :param event: 要发布的事件对象
        """
        return self.event_bus.publish_async(event)

    def register_handler(self, event_type: str, handler: Callable, priority: int = 0):
        """
        [用户接口]注册事件处理器到事件总线
        :param event_type: 事件类型
        :param handler: 事件处理器
        :param priority: 事件处理器优先级
        """
        event_type = event_type
        self.event_bus.subscribe(event_type, handler, priority)
        self._event_handlers[event_type].append(handler)

    async def on_load(self):
        """
        [用户接口]插件加载时调用的生命周期方法
        """
        pass

    async def on_unload(self):
        """
        [用户接口]插件卸载时调用的生命周期方法
        """
        pass

    async def _close_(self):
        """
        注销插件自动调用
        """
        self._save_persistent_data()
        self._unregister_handlers()

    def _unregister_handlers(self):
        """
        注销插件注册的所有事件处理器
        """
        for event_type, handlers in self._event_handlers.items():
            for handler in handlers:
                # 转换为原始处理器的弱引用形式
                if inspect.ismethod(handler):
                    weak_ref = WeakMethod(handler)
                elif inspect.isfunction(handler):
                    weak_ref = ref(handler)
                else:
                    weak_ref = handler

                # 从事件总线移除
                self.event_bus._exact_handlers[event_type] = [
                    (p, h)
                    for (p, h) in self.event_bus._exact_handlers[event_type]
                    if h != weak_ref
                ]
                # 更新正则处理器
                self.event_bus._regex_handlers = [
                    (p, pri, h)
                    for (p, pri, h) in self.event_bus._regex_handlers
                    if h != weak_ref
                ]
        self._event_handlers.clear()


# endregion
