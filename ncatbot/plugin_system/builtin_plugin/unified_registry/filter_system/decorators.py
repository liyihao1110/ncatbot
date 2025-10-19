"""过滤器装饰器 v2.0"""

from typing import Callable, Union, TYPE_CHECKING
from .builtin import (
    GroupFilter,
    PrivateFilter,
    AdminFilter,
    RootFilter,
    TrueFilter,
    CustomFilter,
)
from .base import BaseFilter

if TYPE_CHECKING:
    from .base import BaseFilter


def filter(*filters: Union[str, "BaseFilter"]):
    from .registry import filter_registry

    """为函数添加过滤器的装饰器

    Usage:
        @filter("my_filter")
        @filter(GroupFilter())
        @filter(GroupFilter(), AdminFilter())
        def my_command(event):
            pass
    """

    def decorator(func: Callable) -> Callable:
        filter_registry.add_filter_to_function(func, *filters)
        return func

    return decorator


def group_filter(func: Callable) -> Callable:
    """群聊专用装饰器"""
    deco = filter(GroupFilter())
    return deco(func)


def private_filter(func: Callable) -> Callable:
    """私聊专用装饰器"""
    deco = filter(PrivateFilter())
    return deco(func)


def admin_filter(func: Callable) -> Callable:
    """管理员专用装饰器"""
    deco = filter(AdminFilter())
    return deco(func)


def root_filter(func: Callable) -> Callable:
    """Root专用装饰器"""
    deco = filter(RootFilter())
    return deco(func)


def on_message(func: Callable) -> Callable:
    """消息专用装饰器"""
    deco = filter(TrueFilter())
    return deco(func)


# 组合装饰器
def admin_group_filter(func: Callable) -> Callable:
    """管理员群聊专用装饰器"""
    deco = filter(GroupFilter(), AdminFilter())
    return deco(func)


def admin_private_filter(func: Callable) -> Callable:
    """管理员私聊专用装饰器"""
    deco = filter(PrivateFilter(), AdminFilter())
    return deco(func)


def on_request(func: Callable) -> Callable:
    """请求专用装饰器"""
    from ..legacy_registry import legacy_registry

    legacy_registry._request_event.append(func)
    return func


def on_notice(func: Callable) -> Callable:
    """通知专用装饰器"""
    from ..legacy_registry import legacy_registry

    legacy_registry._notice_event.append(func)
    return func


def on_group_poke(func: Callable) -> Callable:
    """群聊戳一戳专用装饰器"""
    from ncatbot.core.event.notice import NoticeEvent

    def poke_filter(event) -> bool:
        """检查是否是戳一戳事件"""
        return isinstance(event, NoticeEvent) and event.sub_type == "poke"

    decorated_func = filter(GroupFilter(), CustomFilter(poke_filter, "poke_filter"))(
        func
    )
    return on_notice(decorated_func)


def on_group_at(func: Callable) -> Callable:
    """群聊艾特专用装饰器"""
    from ncatbot.core.event.message import GroupMessageEvent

    def at_filter(event) -> bool:
        """检查是否艾特了机器人"""
        if not isinstance(event, GroupMessageEvent):
            return False
        bot_id = event.self_id
        for message_spiece in event.message.messages:
            if (
                message_spiece.msg_seg_type == "at"
                and getattr(message_spiece, "qq", None) == bot_id
            ):
                return True
        return False

    decorated_func = filter(GroupFilter(), CustomFilter(at_filter, "at_filter"))(func)
    return on_message(decorated_func)


# 兼容
admin_only = admin_filter
root_only = root_filter
private_only = private_filter
group_only = group_filter
