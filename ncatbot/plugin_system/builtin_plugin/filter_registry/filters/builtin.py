"""内置过滤器模块"""

from typing import TYPE_CHECKING
from .base import BaseFilter

if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent
    from ..filter_registry import FilterRegistryPlugin


class GroupFilter(BaseFilter):
    """群组消息过滤器
    
    只允许群组消息通过。
    """
    
    def check(self, manager: "FilterRegistryPlugin", event: "BaseMessageEvent") -> bool:
        return event.is_group_msg()


class PrivateFilter(BaseFilter):
    """私聊消息过滤器
    
    只允许私聊消息通过。
    """
    
    def check(self, manager: "FilterRegistryPlugin", event: "BaseMessageEvent") -> bool:
        return not event.is_group_msg()


class AdminFilter(BaseFilter):
    """管理员权限过滤器
    
    只允许具有管理员或root权限的用户通过。
    """
    
    def check(self, manager: "FilterRegistryPlugin", event: "BaseMessageEvent") -> bool:
        return (manager.rbac_manager.user_has_role(event.user_id, "admin") or 
                manager.rbac_manager.user_has_role(event.user_id, "root"))


class RootFilter(BaseFilter):
    """Root权限过滤器
    
    只允许具有root权限的用户通过。
    """
    
    def check(self, manager: "FilterRegistryPlugin", event: "BaseMessageEvent") -> bool:
        return manager.rbac_manager.user_has_role(event.user_id, "root")
