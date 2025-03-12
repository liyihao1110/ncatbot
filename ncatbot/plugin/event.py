# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-21 18:23:06
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-06 20:41:46
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @message: 喵喵喵?
# @Copyright (c) 2025 by Fish-LP, MIT License
# -------------------------
import asyncio
import inspect
import re
import uuid
from enum import Enum
from typing import Any, Callable, List, Union

from RBACManager.RBACManager import RBACManager

from ncatbot.core.message import BaseMessage
from ncatbot.utils.literals import (
    OFFICIAL_GROUP_MESSAGE_EVENT,
    OFFICIAL_PRIVATE_MESSAGE_EVENT,
)


class Conf:
    def __init__(self, plugin, key, rptr: Callable[[str], Any] = None):
        self.full_key = f"{plugin.name}.{key}"
        self.key = key
        self.rptr = rptr
        self.hook_config = plugin.data["config"]

    def modify(self, value):
        # try:
        value = self.rptr(value) if self.rptr else value
        self.hook_config[self.full_key] = value
        # except Exception as e:


class PermissionGroup(Enum):
    ROOT = "root"
    ADMIN = "admin"
    USER = "user"


class EventSource:
    def __init__(self, user_id: Union[str, int], group_id: Union[str, int]):
        self.user_id = f"USER-{user_id}"
        self.group_id = f"GROUP-{group_id}"


class EventType:
    def __init__(self, plugin_name: str, event_name: str):
        self.plugin_name = plugin_name
        self.event_name = event_name

    def __str__(self):
        return f"{self.plugin_name}.{self.event_name}"


class EventBusRBACManager(RBACManager):
    def has_user(self, user: str):
        return user in self.users

    def create_user(self, user_name, base_role=PermissionGroup.USER):
        super().create_user(user_name)
        self.assign_role_to_user(user_name, base_role)

    def with_permission(
        self, source: EventSource, type: EventType, permission_raise: bool = False
    ):
        if not self.has_user(source.group_id):
            self.create_user(source.group_id)
        if not self.has_user(source.user_id):
            self.create_user(source.user_id)
        return self.has_user_permission(
            source.user_id, type
        ) and self.has_user_permission(source.group_id, type)


class Event:
    """
    事件类，用于封装事件的类型和数据
    """

    def __init__(self, type: EventType, data: Any, source: EventSource):
        """
        初始化事件

        参数:
            type: str - 事件的类型
            data: Any - 事件携带的数据
        """
        self.type = type
        self.data = data
        self.source = source  # 事件源
        self._results: List[Any] = []
        self._propagation_stopped = False

    def stop_propagation(self):
        """
        停止事件的传播
        当调用此方法后，后续的处理器将不会被执行
        """
        self._propagation_stopped = True

    def add_result(self, result: Any):
        """
        添加事件处理结果

        参数:
            result: Any - 处理器返回的结果
        """
        self._results.append(result)

    def __repr__(self):
        return f'Event(type="{self.type}",data={self.data})'


class Func:
    """功能函数"""

    def __init__(
        self,
        name,
        plugin_name,
        func: Callable,
        filter: Callable[[Event], bool] = None,
        raw_message_filter: str = None,
        permission: PermissionGroup = PermissionGroup.USER,
        permission_raise: bool = False,
    ):
        self.name = name
        self.plugin_name = plugin_name
        self.func = func
        self.filter = filter
        self.raw_message_filter = raw_message_filter
        self.permission = permission
        self.permission_raise = permission_raise

    def activate(self, event: Event) -> bool:
        """激活功能函数"""
        if self.filter and not self.filter(event):
            return False
        elif isinstance(event.data, BaseMessage):
            if self.raw_message_filter and not re.match(
                self.raw_message_filter, event.data.raw_message
            ):
                return False
        return True


class EventBus:
    """
    事件总线类，用于管理和分发事件
    """

    def __init__(self):
        """
        初始化事件总线
        """
        self._exact_handlers = {}
        self._regex_handlers = []
        self.RBAC = EventBusRBACManager()
        self.funcs: List[Func] = []
        self._create_basic_roles()
        self._assign_root_permission()
        self.subscribe(OFFICIAL_GROUP_MESSAGE_EVENT, self._func_activator, 100)
        self.subscribe(OFFICIAL_PRIVATE_MESSAGE_EVENT, self._func_activator, 100)

    def _cfg(self):
        pass

    def _sam(self):
        pass

    def _acs(self):
        pass

    def _func_activator(self, event: Event):
        # message:BaseMessage = event.data
        for func in self.funcs:
            if func.activate(event):
                if self.RBAC.with_permission(
                    event.source, event.type, func.permission_raise
                ):
                    func.func(event)

    def _assign_root_permission(self):
        self.RBAC.create_user("root")
        self.RBAC.assign_role_to_user("root", "root")
        self.RBAC.assign_permission("root", "**")

    def _create_basic_roles(self):
        self.RBAC.create_role("root")
        self.RBAC.create_role("admin")
        self.RBAC.create_role("user")
        self.RBAC.create_role("blacklist")
        self.RBAC.add_role_parent("root", "admin")
        self.RBAC.add_role_parent("admin", "user")

    def set_plugin_funcs(self, plugin):
        from ncatbot.plugin.base_plugin import BasePlugin

        assert isinstance(plugin, BasePlugin)
        for func in plugin.funcs:
            self.RBAC.assign_permission(
                func.permission, f"{func.plugin_name}.{func.name}"
            )

    def subscribe(
        self, event_type: EventType, handler: Callable[[Event], Any], priority: int = 0
    ) -> uuid.UUID:
        """
        订阅事件处理器，并返回处理器的唯一 ID
        权限路径为: plugin_name.hander_id

        参数:
            event_type: str - 事件类型或正则模式（以 're:' 开头表示正则匹配）
            handler: Callable[[Event], Any] - 事件处理器函数
            priority: int - 处理器的优先级（数字越大，优先级越高）

        返回:
            str - 处理器的唯一 ID
        """
        handler_id = f"{event_type.plugin_name}.{str(uuid.uuid4())}"
        pattern = None
        if event_type.startswith("re:"):
            pattern = re.compile(event_type[3:])
            self._regex_handlers.append((pattern, priority, handler, handler_id))
        else:
            self._exact_handlers.setdefault(event_type, []).append(
                (pattern, priority, handler, handler_id)
            )
        return handler_id

    def unsubscribe(self, handler_id: uuid.UUID) -> bool:
        """
        取消订阅事件处理器

        参数:
            handler_id: UUID - 处理器的唯一 ID

        返回:
            bool - 是否成功取消订阅
        """
        # 取消精确匹配处理器
        for event_type in list(self._exact_handlers.keys()):
            self._exact_handlers[event_type] = [
                (patt, pr, h, hid)
                for (patt, pr, h, hid) in self._exact_handlers[event_type]
                if hid != handler_id
            ]
            if not self._exact_handlers[event_type]:
                del self._exact_handlers[event_type]
        # 取消正则匹配处理器
        self._regex_handlers = [
            (patt, pr, h, hid)
            for (patt, pr, h, hid) in self._regex_handlers
            if hid != handler_id
        ]
        return True

    async def publish_async(self, event: Event) -> List[Any]:
        """
        异步发布事件

        参数:
            event: Event - 要发布的事件

        返回值:
            List[Any] - 所有处理器返回的结果的列表(通常是空列表)
        """
        handlers = []
        if event.type in self._exact_handlers:
            # 处理精确匹配处理器
            for pattern, priority, handler, handler_id in self._exact_handlers[
                event.type
            ]:
                handlers.append((handler, priority, handler_id))
        else:
            # 处理正则匹配处理器
            for pattern, priority, handler, handler_id in self._regex_handlers:
                if pattern and pattern.match(event.type):
                    handlers.append((handler, priority, handler_id))

        # 按优先级排序
        sorted_handlers = sorted(handlers, key=lambda x: (-x[1], x[0].__name__))

        results = []
        # 按优先级顺序调用处理器
        for handler, priority, handler_id in sorted_handlers:
            if event._propagation_stopped:
                break

            if not self.RBAC.with_permission(
                event.source, handler_id
            ):  # 检查事件发起者权限
                continue

            if inspect.iscoroutinefunction(handler):
                await handler(event)
            else:
                asyncio.create_task(handler(event))

            # 收集结果
            results.extend(event._results)

        return results

    def publish_sync(self, event: Event) -> List[Any]:
        """
        同步发布事件

        参数:
            event: Event - 要发布的事件

        返回值:
            List[Any] - 所有处理器返回的结果的列表
        """
        loop = asyncio.new_event_loop()  # 创建新的事件循环
        try:
            asyncio.set_event_loop(loop)  # 设置为当前事件循环
            return loop.run_until_complete(self.publish_async(event))
        finally:
            loop.close()  # 关闭事件循环
