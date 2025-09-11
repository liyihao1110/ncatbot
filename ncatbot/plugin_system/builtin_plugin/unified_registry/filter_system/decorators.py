"""过滤器装饰器 v2.0"""

from typing import Callable, Union, TYPE_CHECKING
from .registry import filter_registry, FilterRegistry
from .builtin import GroupFilter, PrivateFilter, AdminFilter, RootFilter, TrueFilter
from functools import wraps
from .base import BaseFilter

if TYPE_CHECKING:
    from .base import BaseFilter

def filter(*filters: Union[str, 'BaseFilter']):
    """为函数添加过滤器的装饰器
    
    Usage:
        @filter("my_filter")
        @filter(GroupFilter())
        @filter(GroupFilter(), AdminFilter())
        def my_command(event):
            pass
    """
    def decorator(func: Callable) -> Callable:
        return filter_registry.add_filter_to_function(func, *filters)
    return decorator

def group_only(func: Callable) -> Callable:
    """群聊专用装饰器"""
    return filter_registry.add_filter_to_function(func, GroupFilter())

def private_only(func: Callable) -> Callable:
    """私聊专用装饰器"""
    return filter_registry.add_filter_to_function(func, PrivateFilter())

def admin_only(func: Callable) -> Callable:
    """管理员专用装饰器"""
    return filter_registry.add_filter_to_function(func, AdminFilter())

def root_only(func: Callable) -> Callable:
    """Root专用装饰器"""
    return filter_registry.add_filter_to_function(func, RootFilter())

def on_message(func: Callable) -> Callable:
    """消息专用装饰器"""
    return filter_registry.add_filter_to_function(func, TrueFilter())

# 组合装饰器
def admin_group_only(func: Callable) -> Callable:
    """管理员群聊专用装饰器"""
    return filter_registry.add_filter_to_function(func, GroupFilter(), AdminFilter())

def admin_private_only(func: Callable) -> Callable:
    """管理员私聊专用装饰器"""
    return filter_registry.add_filter_to_function(func, PrivateFilter(), AdminFilter())