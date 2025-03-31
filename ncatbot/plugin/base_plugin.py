# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-15 20:08:02
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-22 17:44:14
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
import asyncio
import re
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple, Union, final
from uuid import UUID

from ncatbot.core.api import BotAPI
from ncatbot.core.message import BaseMessage
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
from ncatbot.utils.time_task_scheduler import TimeTaskScheduler

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

    @final
    def __init__(
        self,
        event_bus: EventBus,
        time_task_scheduler: TimeTaskScheduler,
        debug: bool = False,
        **kwd,
    ):
        """初始化插件实例

        Args:
            event_bus: 事件总线实例
            time_task_scheduler: 定时任务调度器
            debug: 是否启用调试模式
            **kwd: 额外的关键字参数,将被设置为插件属性

        Raises:
            ValueError: 当缺少插件名称或版本号时抛出
            PluginLoadError: 当工作目录无效时抛出
        """
        # 插件信息检查
        if not self.name:
            raise ValueError("缺失插件名称")
        if not self.version:
            raise ValueError("缺失插件版本号")

        # 添加额外属性
        if kwd:
            for k, v in kwd.items():
                setattr(self, k, v)
        if not self.dependencies:
            self.dependencies = {}

        if not self.dependencies:
            self.dependencies = {}

        # 隐藏属性
        self._debug = debug
        self._event_handlers = []
        self._event_bus = event_bus
        self._time_task_scheduler = time_task_scheduler
        self._work_path = Path(PERSISTENT_DIR) / self.name
        self._data_path = self._work_path / f"{self.name}.json"

        # 暴露的属性
        self.lock = asyncio.Lock()  # 创建一个异步锁对象
        self.data = UniversalLoader(self._work_path / f"{self.name}.json")
        self.funcs: list[Func] = []  # 功能
        self.configs: list[Conf] = []  # 配置项

        # 检查是否为第一次启动
        self.first_load = False
        if not self._work_path.exists():
            self._work_path.mkdir(parents=True)
            self.first_load = True
        elif not self._data_path.exists():
            self.first_load = True

        if not self._work_path.is_dir():
            raise PluginLoadError(self.name, f"{self._work_path} 不是目录文件夹")

        self.work_space = ChangeDir(self._work_path)

    @final
    async def __unload__(self, *arg, **kwd):
        """卸载插件时的清理操作

        执行插件卸载前的清理工作,保存数据并注销事件处理器

        Raises:
            RuntimeError: 保存持久化数据失败时抛出
        """
        self.unregister_handlers()
        await asyncio.to_thread(self._close_, *arg, **kwd)
        await self.on_close(*arg, **kwd)
        try:
            if isinstance(self.data, dict) and len(self.data) == 0:
                pass
            else:
                self.data.save()
        except (FileTypeUnknownError, SaveError, FileNotFoundError) as e:
            raise RuntimeError(self.name, f"保存持久化数据时出错: {e}")

    @final
    async def __onload__(self):
        """加载插件时的初始化操作

        执行插件加载时的初始化工作,加载数据

        Raises:
            RuntimeError: 读取持久化数据失败时抛出
        """
        # load时传入的参数作为属性被保存在self中
        try:
            if isinstance(self.data, dict):
                data = UniversalLoader()
                data.data = self.data
                self.data = data
            self.data.load()
        except (FileTypeUnknownError, LoadError, FileNotFoundError):
            open(self._work_path / f"{self.name}.json", "w").write("{}")
            self.data.load()
        await asyncio.to_thread(self._init_)
        await self.on_load()

    @final
    def add_scheduled_task(
        self,
        job_func: Callable,
        name: str,
        interval: Union[str, int, float],
        conditions: Optional[List[Callable[[], bool]]] = None,
        max_runs: Optional[int] = None,
        args: Optional[Tuple] = None,
        kwargs: Optional[Dict] = None,
        args_provider: Optional[Callable[[], Tuple]] = None,
        kwargs_provider: Optional[Callable[[], Dict[str, Any]]] = None,
    ) -> bool:
        """
        添加定时任务

        Args:
            job_func (Callable): 要执行的任务函数
            name (str): 任务唯一标识名称
            interval (Union[str, int, float]): 调度时间参数
            conditions (Optional[List[Callable]]): 执行条件列表
            max_runs (Optional[int]): 最大执行次数
            args (Optional[Tuple]): 静态位置参数
            kwargs (Optional[Dict]): 静态关键字参数
            args_provider (Optional[Callable]): 动态位置参数生成函数
            kwargs_provider (Optional[Callable]): 动态关键字参数生成函数

        Returns:
            bool: 是否添加成功

        Raises:
            ValueError: 当参数冲突或时间格式无效时
        """

        job_info = {
            "name": name,
            "job_func": job_func,
            "interval": interval,
            "max_runs": max_runs,
            "conditions": conditions or [],
            "args": args,
            "kwargs": kwargs or {},
            "args_provider": args_provider,
            "kwargs_provider": kwargs_provider,
        }
        if not isinstance(job_info["args"], tuple) and args is not None:
            _log.warning(
                f"args 必须为 tuple 类型, {job_info['args']} 不是 tuple 类型, 而是 {type(job_info['args'])}, 注册定时任务失败"
            )
            return
        if not isinstance(job_info["kwargs"], dict):
            _log.warning(
                f"kwargs 必须为 dict 类型, {job_info['kwargs']} 不是 dict 类型, 而是 {type(job_info['kwargs'])}, 注册定时任务失败"
            )
            return
        return self._time_task_scheduler.add_job(**job_info)

    @final
    def remove_scheduled_task(self, task_name: str):
        """
        移除指定名称的定时任务

        Args:
            name (str): 要移除的任务名称

        Returns:
            bool: 是否成功找到并移除任务
        """
        return self._time_task_scheduler.remove_job(name=task_name)

    @final
    def publish_sync(self, event: Event) -> List[Any]:
        """同步发布事件

        Args:
            event (Event): 要发布的事件对象

        Returns:
            List[Any]: 事件处理器返回的结果列表
        """
        return self._event_bus.publish_sync(event)

    @final
    def publish_async(self, event: Event) -> Awaitable[List[Any]]:
        """异步发布事件

        Args:
            event (Event): 要发布的事件对象

        Returns:
            List[Any]: 事件处理器返回的结果列表
        """
        return self._event_bus.publish_async(event)

    @final
    def register_handler(
        self, event_type: str, handler: Callable[[BaseMessage], Any], priority: int = 0
    ) -> UUID:
        """注册事件处理器

        Args:
            event_type (str): 事件类型
            handler (Callable[[BaseMessage], Any]): 事件处理函数
            priority (int, optional): 处理器优先级,默认为0

        Returns:
            处理器的唯一标识UUID
        """
        handler_id = self._event_bus.subscribe(event_type, handler, priority)
        self._event_handlers.append(handler_id)
        return handler_id

    @final
    def unregister_handler(self, handler_id: UUID) -> bool:
        """注销指定的事件处理器

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
            self._event_bus.unsubscribe(handler_id)

    @final
    def _register_func(
        self,
        name: str,
        handler: Callable[[BaseMessage], Any],
        filter: Callable = None,
        raw_message_filter: Union[str, re.Pattern] = None,
        permission: PermissionGroup = PermissionGroup.USER.value,
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
        handler: Callable[[BaseMessage], Any],
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
            PermissionGroup.USER.value,
            permission_raise,
        )

    def register_admin_func(
        self,
        name: str,
        handler: Callable[[BaseMessage], Any],
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
            PermissionGroup.ADMIN.value,
            permission_raise,
        )

    def register_default_func(
        self,
        handler: Callable[[BaseMessage], Any],
        permission: PermissionGroup = PermissionGroup.USER.value,
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
        self.configs.append(Conf(self, key, rptr, default))

    async def on_load(self):
        """插件初始化时的钩子函数，可被子类重写"""
        pass

    @final
    async def on_close(self):
        """插件卸载时的子函数，暂时存在问题"""
        pass

    def _init_(self):
        """插件初始化时的子函数，可被子类重写"""
        pass

    def _close_(self):
        """插件卸载时的子函数，可被子类重写"""
        pass
