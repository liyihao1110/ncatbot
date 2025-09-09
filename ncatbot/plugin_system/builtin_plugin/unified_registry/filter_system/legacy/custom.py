"""Legacy custom filters"""

from typing import TYPE_CHECKING, Callable
from .base import BaseFilter

if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent
    from ...plugin import UnifiedRegistryPlugin


class CustomFilter(BaseFilter):
    """Legacy custom filter wrapper"""
    
    def __init__(self, filter_func: Callable, name: str = None):
        super().__init__(name or getattr(filter_func, '__name__', 'custom'))
        self.filter_func = filter_func
    
    async def check(self, manager: "UnifiedRegistryPlugin", event: "BaseMessageEvent") -> bool:
        """Execute custom filter check"""
        return await self.filter_func(manager, event)