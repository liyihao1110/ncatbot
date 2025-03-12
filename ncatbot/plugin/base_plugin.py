# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-15 20:08:02
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-09 18:35:25
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, MIT License
# -------------------------
import asyncio
import re
from pathlib import Path
from typing import Any, Awaitable, Callable, List, Union, final
from uuid import UUID

from ncatbot.core.api import BotAPI
from ncatbot.plugin.custom_err import PluginLoadError
from ncatbot.plugin.event import Conf, Event, EventBus, Func, PermissionGroup
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
    """插件基类

    所有插件的基类，提供了插件系统的基本功能支持。

    Attributes:
        name (str): 插件名称
        version (str): 插件版本号
        dependencies (dict): 插件依赖项
        meta_data (dict): 插件元数据
        api (BotAPI): API接口处理器
        event_bus (EventBus): 事件总线实例
        lock (asyncio.Lock): 异步锁对象
        work_path (Path): 插件工作目录路径
        data (UniversalLoader): 插件数据管理器
        work_space (ChangeDir): 插件工作目录上下文管理器
        first_load (bool): 是否首次加载标志
    """

    name: str
    version: str
    dependencies: dict = {}  # 依赖的插件以及版本(不是 PYPI 依赖)
    meta_data: dict
    api: BotAPI
    funcs: list[Func] = []  # 功能
    configs: list[Conf] = []  # 配置项

    @final
    def __init__(self, event_bus: EventBus, **kwd):
        """初始化插件实例

        Args:
            event_bus: 事件总线实例
            **kwd: 额外的关键字参数，将被设置为插件属性

        Raises:
            ValueError: 当缺少插件名称或版本号时抛出
            PluginLoadError: 当工作目录无效时抛出
        """
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
        self._event_handlers = []
        self.data = UniversalLoader(
            self.work_path / f"{self.name}.json"
        )  # 好想改成yaml啊

        if not self.work_path.exists():
            try:
                self.work_path.mkdir(parents=True)
                self.first_load = True  # 表示是第一次启动
            except FileExistsError:
                if not self.work_path.is_dir():
                    raise PluginLoadError(self.name, f"{self.work_path} 不是目录文件夹")
                self.first_load = False

        self.work_space = ChangeDir(self.work_path)

    @final
    async def __unload__(self):
        """卸载插件时的清理操作

        执行插件卸载前的清理工作，保存数据并注销事件处理器

        Raises:
            RuntimeError: 保存持久化数据失败时抛出
        """
        try:
            if isinstance(self.data, dict) and len(self.data) == 0:
                pass
            else:
                self.data.save()
        except (FileTypeUnknownError, SaveError, FileNotFoundError) as e:
            raise RuntimeError(self.name, f"保存持久化数据时出错: {e}")
        self.unregister_handlers()
        await asyncio.to_thread(self._close_)
        await self.on_unload()

    @final
    async def __onload__(self):
        """加载插件时的初始化操作

        执行插件加载时的初始化工作，加载数据

        Raises:
            RuntimeError: 读取持久化数据失败时抛出
        """
        await asyncio.to_thread(self._init_)
        await self.on_load()
        try:
            self.data.load()
        except (FileTypeUnknownError, LoadError, FileNotFoundError):
            open(self.work_path / f"{self.name}.json", "w").write("{}")
            self.data.load()

    @final
    def publish_sync(self, event: Event) -> List[Any]:
        """同步发布事件

        Args:
            event (Event): 要发布的事件对象

        Returns:
            List[Any]: 事件处理器返回的结果列表
        """
        return self.event_bus.publish_sync(event)

    @final
    def publish_async(self, event: Event) -> Awaitable[List[Any]]:
        """异步发布事件

        Args:
            event (Event): 要发布的事件对象

        Returns:
            Awaitable[List[Any]]: 事件处理器返回的结果列表的可等待对象
        """
        return self.event_bus.publish_async(event)

    @final
    def register_handler(
        self, event_type: str, handler: Callable[[Event], Any], priority: int = 0
    ) -> UUID:
        """注册事件处理器

        Args:
            event_type (str): 事件类型
            handler (Callable[[Event], Any]): 事件处理函数
            priority (int, optional): 处理器优先级，默认为0
        """
        handler_id = self.event_bus.subscribe(event_type, handler, priority)
        self._event_handlers.append(handler_id)
        return handler_id

    @final
    def unregister_handler(self, handler_id: UUID):
        """注销事件处理器(此插件注册)

        Args:
            handler_id (UUID): 事件id

        Returns:
            bool: 操作结果
        """
        if handler_id in self._event_handlers:
            self._event_handlers.append(handler_id)
            return True
        return False

    @final
    def unregister_handlers(self):
        """注销所有已注册的事件处理器"""
        for handler_id in self._event_handlers:
            self.event_bus.unsubscribe(handler_id)

    @final
    def _register_func(
        self,
        name: str,
        handler: Callable[[Event], Any],
        filter: Callable = None,
        raw_message_filter: Union[str, re.Pattern] = None,
        permission: PermissionGroup = PermissionGroup.USER,
        permission_raise: bool = False,
    ):
        if all([name != var.name for var in self.funcs]):
            self.funcs.append(
                Func(
                    name,
                    self.name,
                    handler,
                    filter,
                    raw_message_filter,
                    permission,
                    permission_raise,
                )
            )
        else:
            raise ValueError(f"插件 {self.name} 已存在功能 {name}")
        # self.

    def register_user_func(
        self,
        name: str,
        handler: Callable[[Event], Any],
        filter: Callable = None,
        raw_message_filter: Union[str, re.Pattern] = None,
        permission_raise: bool = False,
    ):
        if filter is None and raw_message_filter is None:
            raise ValueError("普通功能至少添加一个过滤器")
        self._register_func(
            name,
            handler,
            filter,
            raw_message_filter,
            PermissionGroup.USER,
            permission_raise,
        )

    def register_admin_func(
        self,
        name: str,
        handler: Callable[[Event], Any],
        filter: Callable = None,
        raw_message_filter: Union[str, re.Pattern] = None,
        permission_raise: bool = False,
    ):
        if filter is None and raw_message_filter is None:
            raise ValueError("普通功能至少添加一个过滤器")
        self._register_func(
            name,
            handler,
            filter,
            raw_message_filter,
            PermissionGroup.ADMIN,
            permission_raise,
        )

    def register_default_func(
        self,
        handler: Callable[[Event], Any],
        permission: PermissionGroup = PermissionGroup.USER,
    ):
        """默认处理功能

        如果没能触发其它功能, 则触发默认功能.
        """
        self._register_func("default", handler, None, None, permission, False)

    def register_config(
        self, key: str, default: Any, rptr: Callable[[str], Any] = None
    ):
        """注册配置项
        Args:
            key (str): 配置项键名
            default (Any): 默认值
            rptr (Callable[[str], Any], optional): 值转换函数. 默认使用直接转换.
        """
        self.data["config"][key] = default
        self.configs.append(Conf(self, key, rptr))

    async def on_load(self):
        """插件初始化时的钩子函数，可被子类重写"""
        pass

    def _init_(self):
        """插件初始化时的子函数，可被子类重写"""
        pass

    async def on_unload(self):
        """插件卸载时的钩子函数，可被子类重写"""
        pass

    def _close_(self):
        """插件卸载时的子函数，可被子类重写"""
        pass
