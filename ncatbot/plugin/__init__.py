# 3xx 兼容层

from ..plugin_system import NcatBotEvent as Event
from ..plugin_system import NcatBotPlugin as BasePlugin
from .compatible_enrollment import CompatibleEnrollment


__all__ = [
    "Event",
    "BasePlugin",
    "CompatibleEnrollment",
]
