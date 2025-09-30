"""过滤器装饰器 v2.0"""

from typing import Callable, Union, TYPE_CHECKING
from .builtin import GroupFilter, PrivateFilter, AdminFilter, RootFilter, TrueFilter
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


# 兼容
admin_only = admin_filter
root_only = root_filter
private_only = private_filter
group_only = group_filter
