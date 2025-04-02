# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-03-29 15:36:57
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-30 13:50:40
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, final
from uuid import UUID

from ncatbot.core.message import BaseMessage
from ncatbot.plugin.event import Conf, Event, EventBus, Func, PermissionGroup
from ncatbot.utils.time_task_scheduler import TimeTaskScheduler


class EventHandlerMixin:
    """事件处理混入类，提供事件发布和订阅功能。

    # 描述
    该混入类实现了完整的事件处理系统，包括事件的同步/异步发布以及处理器的管理功能。
    作为一个Mixin类，它需要与具有 `_event_bus` 实例的类配合使用。

    # 属性
    - `_event_bus` (EventBus): 事件总线实例，用于处理事件的发布与订阅
    - `_event_handlers` (List[UUID]): 当前已注册的事件处理器ID列表

    # 使用示例
    ```python
    class MyClass(EventHandlerMixin):
        def __init__(self):
            self._event_bus = EventBus()
            self._event_handlers = []
    ```
    """

    _event_bus: EventBus
    _event_handlers: List[UUID]

    @final
    def publish_sync(self, event: Event) -> List[Any]:
        """同步发布事件。

        Args:
            event (Event): 要发布的事件对象。

        Returns:
            List[Any]: 所有事件处理器的返回值列表。
        """
        return self._event_bus.publish_sync(event)

    @final
    def publish_async(self, event: Event):
        """异步发布事件。

        Args:
            event (Event): 要发布的事件对象。

        Returns:
            None: 这个方法不返回任何值。
        """
        return self._event_bus.publish_async(event)

    @final
    def register_handler(
        self, event_type: str, handler: Callable[[Event], Any], priority: int = 0
    ) -> UUID:
        """注册一个事件处理器。

        Args:
            event_type (str): 事件类型标识符。
            handler (Callable[[Event], Any]): 事件处理器函数。
            priority (int, optional): 处理器优先级，默认为0。优先级越高，越先执行。

        Returns:
            UUID: 处理器的唯一标识符。
        """
        handler_id = self._event_bus.subscribe(event_type, handler, priority)
        self._event_handlers.append(handler_id)
        return handler_id

    @final
    def unregister_handler(self, handler_id: UUID) -> bool:
        """注销一个事件处理器。

        Args:
            handler_id (UUID): 要注销的事件处理器的唯一标识符。

        Returns:
            bool: 如果注销成功返回True，否则返回False。
        """
        if handler_id in self._event_handlers:
            rest = self._event_bus.unsubscribe(handler_id)
            if rest:
                self._event_handlers.remove(handler_id)
                return True
        return False

    @final
    def unregister_handlers(self):
        """注销所有事件处理器。

        Returns:
            None: 这个方法不返回任何值。
        """
        for handler_id in self._event_handlers:
            self._event_bus.unsubscribe(handler_id)


class SchedulerMixin:
    """定时任务调度混入类，提供定时任务的管理功能。

    # 描述
    该混入类提供了定时任务的添加、移除等管理功能。支持灵活的任务调度配置，
    包括固定间隔执行、条件触发、参数动态生成等特性。

    # 属性
    - `_time_task_scheduler` (TimeTaskScheduler): 时间任务调度器实例

    # 特性
    - 支持固定时间间隔的任务调度
    - 支持条件触发机制
    - 支持最大执行次数限制
    - 支持动态参数生成
    """

    _time_task_scheduler: TimeTaskScheduler

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
        """添加一个定时任务。

        Args:
            job_func (Callable): 要执行的任务函数。
            name (str): 任务名称。
            interval (Union[str, int, float]): 任务执行的时间间隔。
            conditions (Optional[List[Callable[[], bool]]], optional): 任务执行的条件列表。默认为None。
            max_runs (Optional[int], optional): 任务的最大执行次数。默认为None。
            args (Optional[Tuple], optional): 任务函数的位置参数。默认为None。
            kwargs (Optional[Dict], optional): 任务函数的关键字参数。默认为None。
            args_provider (Optional[Callable[[], Tuple]], optional): 提供任务函数位置参数的函数。默认为None。
            kwargs_provider (Optional[Callable[[], Dict[str, Any]]], optional): 提供任务函数关键字参数的函数。默认为None。

        Returns:
            bool: 如果任务添加成功返回True，否则返回False。
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
        return self._time_task_scheduler.add_job(**job_info)

    @final
    def remove_scheduled_task(self, task_name: str):
        """移除一个定时任务。

        Args:
            task_name (str): 要移除的任务名称。

        Returns:
            bool: 如果任务移除成功返回True，否则返回False。
        """
        return self._time_task_scheduler.remove_job(name=task_name)


class BuiltinFuncMixin:
    """内置功能混入类, 提供内置功能注册功能.

    # 描述
    该混入类提供了功能和配置项支持, 即注册功能和配置项.
    """

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
        if "funcs" not in self.__dict__:
            self.funcs: list[Func] = []

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
        if "configs" not in self.__dict__:
            self.configs: list[Conf] = []
        self.configs.append(Conf(self, key, rptr, default))
