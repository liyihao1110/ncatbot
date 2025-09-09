"""Legacy filter system (moved from original filters)

This module contains the original filter system implementation.
It will be gradually deprecated in favor of the new filter system v2.0.
"""

# Re-export original implementations for backward compatibility
from .base import BaseFilter as LegacyBaseFilter
from .builtin import GroupFilter as LegacyGroupFilter, PrivateFilter as LegacyPrivateFilter
from .custom import CustomFilter as LegacyCustomFilter
from .validator import FilterValidator as LegacyFilterValidator

__all__ = [
    "LegacyBaseFilter",
    "LegacyGroupFilter", 
    "LegacyPrivateFilter",
    "LegacyCustomFilter",
    "LegacyFilterValidator",
]