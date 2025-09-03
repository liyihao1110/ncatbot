"""内置过滤器实现"""

from typing import TYPE_CHECKING
from .base import BaseFilter

if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent
    from ...plugin import UnifiedRegistryPlugin

class GroupFilter(BaseFilter):
    """群聊消息过滤器"""
    
    def check(self, manager: "UnifiedRegistryPlugin", event: "BaseMessageEvent") -> bool:
        """检查是否为群聊消息"""
        return event.is_group_msg()

class PrivateFilter(BaseFilter):
    """私聊消息过滤器"""
    
    def check(self, manager: "UnifiedRegistryPlugin", event: "BaseMessageEvent") -> bool:
        """检查是否为私聊消息"""
        return not event.is_group_msg()

class AdminFilter(BaseFilter):
    """管理员权限过滤器"""
    
    def check(self, manager: "UnifiedRegistryPlugin", event: "BaseMessageEvent") -> bool:
        """检查用户是否有管理员或root权限"""
        return (manager.rbac_manager.user_has_role(event.user_id, "admin") or 
                manager.rbac_manager.user_has_role(event.user_id, "root"))

class RootFilter(BaseFilter):
    """Root权限过滤器"""
    
    def check(self, manager: "UnifiedRegistryPlugin", event: "BaseMessageEvent") -> bool:
        """检查用户是否有root权限"""
        return manager.rbac_manager.user_has_role(event.user_id, "root")
