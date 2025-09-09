# This module has been moved to legacy/
# Please import from the new filter system instead:
# from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import BaseFilter, GroupFilter, PrivateFilter, AdminFilter, RootFilter

# Temporary compatibility imports - will be removed in future versions
from ..legacy.base import BaseFilter
from ..legacy.builtin import GroupFilter, PrivateFilter, AdminFilter, RootFilter

__all__ = [
    "BaseFilter",
    "GroupFilter", 
    "PrivateFilter",
    "AdminFilter",
    "RootFilter",
]
