"""NcatBot plugin system."""

from ncatbot.plugin.base import BasePlugin
from ncatbot.plugin.loader import PluginLoader, get_plugin_info_by_name
from ncatbot.plugin.utils import install_plugin_dependencies

__all__ = [
    # Base classes
    "BasePlugin",
    # Plugin loading
    "PluginLoader",
    "get_plugin_info_by_name",
    # Utility functions
    "install_plugin_dependencies",
]
