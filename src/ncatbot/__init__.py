"""NcatBot - A QQ bot based on NapCat."""

from ncatbot.core import BotClient, install_napcat
from ncatbot.plugin import BasePlugin, PluginLoader, install_plugin_dependencies
from ncatbot.utils import get_log, status

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Core components
    "BotClient",
    "install_napcat",
    # Plugin system
    "BasePlugin",
    "PluginLoader",
    "install_plugin_dependencies",
    # Utils
    "get_log",
    "status",
]
