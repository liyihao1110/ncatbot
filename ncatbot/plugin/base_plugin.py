# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-21 18:23:06
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-02 20:22:51
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @message: 喵喵喵?
# @Copyright (c) 2025 by Fish-LP, MIT License
# -------------------------
import asyncio
from pathlib import Path
from typing import Any, Awaitable, Callable, List

from ncatbot.core.api import BotAPI
from ncatbot.plugin.event import Event, EventBus
from ncatbot.utils.change_dir import ChangeDir
from ncatbot.utils.io import (
    FileTypeUnknownError,
    LoadError,
    SaveError,
    UniversalLoader,
)
from ncatbot.utils.literals import PERSISTENT_DIR
from ncatbot.utils.logger import get_log

_log = get_log()


class BasePlugin:
    """插件基类"""

    name: str
    version: str
    dependencies: dict = {}  # 依赖的插件以及版本(不是 PYPI 依赖)
    meta_data: dict
    api: BotAPI

    def __init__(self, event_bus: EventBus, **kwd):
        # 如果需要传入内容，不需要特殊表明，使用 key = var 传入即可(在上方标注数据类型)
        # kwd会自动作为属性添加到类中
        if not self.name:
            raise ValueError("缺失插件名称")
        if not self.version:
            raise ValueError("缺失插件版本号")
        if kwd:
            for k, v in kwd.items():
                setattr(self, k, v)

        if not self.dependencies:
            self.dependencies = {}

        self.event_bus = event_bus
        self.lock = asyncio.Lock()  # 创建一个异步锁对象
        self.work_path = Path(PERSISTENT_DIR) / self.name
        self._data_file = UniversalLoader(self.work_path / f"{self.name}.json")
        self._event_handlers = []

        try:  # 加载持久化数据
            self.data = self._data_file.load()
        except FileNotFoundError:
            _log.debug(f"持久化数据文件不存在: {self.name}.json, 数据将被重置")
            self.data = {}
        except LoadError:
            self.data = self._data_file
        except Exception as e:
            _log.error(f"加载持久化数据时出错: {e}")
            raise RuntimeError(self.name, "加载持久化数据时出错")

        try:
            self.work_path.mkdir(parents=True)
            self.first_load = True
        except FileExistsError:
            self.first_load = False

        self.work_space = ChangeDir(self.work_path, create_missing=True)
        # 由于支持注册非类函数，且os.chdir管理混乱所以不强制切换路径
        # 使用以下代码进入私有目录
        # with self.work_space:
        #     pass

    async def __unload__(self):
        self._close_()
        await self.on_unload()
        try:
            if isinstance(self.data, dict) and len(self.data) == 0:
                pass
            else:
                self.data.save()
        except (FileTypeUnknownError, SaveError, FileNotFoundError) as e:
            raise RuntimeError(self.name, f"保存持久化数据时出错: {e}")
        self.unregister_handlers()

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
