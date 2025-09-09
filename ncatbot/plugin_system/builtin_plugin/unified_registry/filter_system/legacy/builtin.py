"""Legacy builtin filters"""

from typing import TYPE_CHECKING
from .base import BaseFilter

if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent
    from ...plugin import UnifiedRegistryPlugin


class GroupFilter(BaseFilter):
    """Legacy group message filter"""
    
    async def check(self, manager: "UnifiedRegistryPlugin", event: "BaseMessageEvent") -> bool:
        """Check if it's a group message"""
        return event.is_group_msg()


class PrivateFilter(BaseFilter):
    """Legacy private message filter"""
    
    async def check(self, manager: "UnifiedRegistryPlugin", event: "BaseMessageEvent") -> bool:
        """Check if it's a private message"""
        return not event.is_group_msg()


class AdminFilter(BaseFilter):
    """Legacy admin permission filter"""
    
    async def check(self, manager: "UnifiedRegistryPlugin", event: "BaseMessageEvent") -> bool:
        """Check if user has admin permission"""
        return (manager.rbac_manager.user_has_role(event.user_id, "admin") or 
                manager.rbac_manager.user_has_role(event.user_id, "root"))


class RootFilter(BaseFilter):
    """Legacy root permission filter"""
    
    async def check(self, manager: "UnifiedRegistryPlugin", event: "BaseMessageEvent") -> bool:
        """Check if user has root permission"""
        return manager.rbac_manager.user_has_role(event.user_id, "root")