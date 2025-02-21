# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-21 18:23:06
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-02-21 19:44:02
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @message: 喵喵喵?
# @Copyright (c) 2025 by Fish-LP, MIT License
# -------------------------
import asyncio
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List

from ncatbot.core import BotAPI
from ncatbot.plugin.custom_err import PluginLoadError
from ncatbot.plugin.event import Event, EventBus
from ncatbot.utils.io import (
    FileTypeUnknownError,
    LoadError,
    SaveError,
    UniversalLoader,
)
from ncatbot.utils.literals import PERSISTENT_DIR


class BasePlugin:
    """插件基类"""

    name: str
    version: str
    dependencies: dict = {}
    meta_data: dict

    def __init__(self, event_bus: EventBus, api: BotAPI, **kwd):
        if not self.name:
            raise ValueError("缺失插件名称")
        if not self.version:
            raise ValueError("缺失插件版本号")
        if not self.dependencies:
            self.dependencies = {}
        self.api = api
        self.event_bus = event_bus
        self.work_path = Path(PERSISTENT_DIR) / self.name
        self.work_path.mkdir(parents=True, exist_ok=True)
        self.data = self._load_persistent_data()
        self.lock = asyncio.Lock()  # 创建一个异步锁对象
        self._event_handlers = []
        if kwd:
            for k, v in kwd.items():
                setattr(self, k, v)

    async def __unload__(self):
        self._close_()
        await self.on_unload()
        self._save_persistent_data()
        self.unregister_handlers()

    def _load_persistent_data(self) -> Dict[str, Any]:
        data_path = self.work_path / f"{self.name}.json"
        try:
            loader = UniversalLoader(data_path)
            return loader.load()
        except (FileTypeUnknownError, LoadError, FileNotFoundError):
            return {}

    def _save_persistent_data(self):
        data_path = self.work_path / f"{self.name}.json"
        try:
            loader = UniversalLoader(data_path)
            loader.data = self.data if isinstance(self.data, dict) else self.data.data
            loader.save()
        except (FileTypeUnknownError, SaveError, FileNotFoundError) as e:
            raise PluginLoadError(self.name, f"保存持久化数据时出错: {e}")

    def publish_sync(self, event: Event) -> List[Any]:
        return self.event_bus.publish_sync(event)

    def publish_async(self, event: Event) -> Awaitable[List[Any]]:
        return self.event_bus.publish_async(event)

    def register_handler(
        self, event_type: str, handler: Callable[[Event], Any], priority: int = 0
    ):
        handler_id = self.event_bus.subscribe(event_type, handler, priority)
        self._event_handlers.append(handler_id)

    def unregister_handlers(self):
        for handler_id in self._event_handlers:
            self.event_bus.unsubscribe(handler_id)

    async def on_load(self):
        pass

    async def on_unload(self):
        pass

    def _init_(self):
        pass

    def _close_(self):
        pass
