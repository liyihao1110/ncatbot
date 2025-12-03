"""过滤器装饰器 v2.0"""

from typing import Callable, Union, TYPE_CHECKING

from .builtin import (
    GroupFilter,
    PrivateFilter,
    MessageSentFilter,
    NonSelfFilter,
    AdminFilter,
    GroupAdminFilter,
    GroupOwnerFilter,
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
    """BOT 管理员专用装饰器"""
    deco = filter(AdminFilter())
    return deco(func)


def group_admin_filter(func: Callable) -> Callable:
    """群管理员专用装饰器"""
    deco = filter(GroupAdminFilter())
    return deco(func)


def group_owner_filter(func: Callable) -> Callable:
    """群主专用装饰器"""
    deco = filter(GroupOwnerFilter())
    return deco(func)


def root_filter(func: Callable) -> Callable:
    """Root专用装饰器"""
    deco = filter(RootFilter())
    return deco(func)


def on_message(func: Callable) -> Callable:
    """消息专用装饰器"""
    deco = filter(NonSelfFilter())
    return deco(func)

def on_message_sent(func: Callable) -> Callable:
    """自身上报消息专用装饰器"""
    deco = filter(MessageSentFilter())
    return deco(func)


# 组合装饰器
def admin_group_filter(func: Callable) -> Callable:
    """BOT 管理员且群聊消息专用装饰器"""
    deco = filter(GroupFilter(), AdminFilter())
    return deco(func)


def admin_private_filter(func: Callable) -> Callable:
    """BOT 管理员且私聊消息专用装饰器"""
    deco = filter(PrivateFilter(), AdminFilter())
    return deco(func)


# 专用事件过滤器
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


def on_group_increase(func: Callable) -> Callable:
    """群聊人数增加专用装饰器"""

    def group_increase_filter(event) -> bool:
        """检查是否是群聊人数增加事件"""
        from ncatbot.core.event.notice import NoticeEvent

        return isinstance(event, NoticeEvent) and event.notice_type == "group_increase"

    decorated_func = filter(
        GroupFilter(), CustomFilter(group_increase_filter, "group_increase_filter")
    )(func)
    return on_notice(decorated_func)


def on_group_decrease(func: Callable) -> Callable:
    """群聊人数减少专用装饰器"""

    def group_decrease_filter(event) -> bool:
        """检查是否是群聊人数减少事件"""
        from ncatbot.core.event.notice import NoticeEvent

        return isinstance(event, NoticeEvent) and event.notice_type == "group_decrease"

    decorated_func = filter(
        GroupFilter(), CustomFilter(group_decrease_filter, "group_decrease_filter")
    )(func)
    return on_notice(decorated_func)


def on_group_request(func: Callable) -> Callable:
    """群聊请求专用装饰器"""

    def group_request_filter(event) -> bool:
        """检查是否是群聊请求事件"""
        from ncatbot.core.event.request import RequestEvent

        return isinstance(event, RequestEvent)

    decorated_func = filter(
        GroupFilter(), CustomFilter(group_request_filter, "group_request_filter")
    )(func)
    return on_request(decorated_func)


# 兼容
admin_only = admin_filter
root_only = root_filter
private_only = private_filter
group_only = group_filter
