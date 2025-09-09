"""Legacy filter validator"""

from typing import Callable, List, TYPE_CHECKING
from .base import BaseFilter
from ncatbot.utils import get_log

if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent
    from ...plugin import UnifiedRegistryPlugin

LOG = get_log(__name__)


class FilterValidator:
    """Legacy filter validator"""
    
    def __init__(self):
        self.filters: List[BaseFilter] = []
    
    def add_filter(self, filter_instance: BaseFilter) -> None:
        """Add a filter to the validator"""
        self.filters.append(filter_instance)
    
    async def validate_filters(self, manager: "UnifiedRegistryPlugin", func: Callable, event: "BaseMessageEvent") -> bool:
        """Validate all filters for a function"""
        # Legacy implementation - check function-specific filters
        if hasattr(func, '__filters__'):
            for filter_instance in func.__filters__:
                try:
                    if not await filter_instance.check(manager, event):
                        LOG.debug(f"Function {func.__name__} blocked by filter {filter_instance}")
                        return False
                except Exception as e:
                    LOG.error(f"Filter validation failed: {filter_instance}, error: {e}")
                    return False
        
        # Check global filters
        for filter_instance in self.filters:
            try:
                if not await filter_instance.check(manager, event):
                    LOG.debug(f"Function {func.__name__} blocked by global filter {filter_instance}")
                    return False
            except Exception as e:
                LOG.error(f"Global filter validation failed: {filter_instance}, error: {e}")
                return False
        
        return True