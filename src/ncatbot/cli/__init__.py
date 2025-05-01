"""NcatBot CLI package."""

import ncatbot.cli.info_commands
import ncatbot.cli.plugin_commands
import ncatbot.cli.system_commands
from ncatbot.cli.registry import registry
from ncatbot.cli.utils import (
    LOG,
    NCATBOT_PATH,
    NUMBER_SAVE,
    PYPI_SOURCE,
    TEST_PLUGIN,
    get_log,
    get_plugin_info_by_name,
    get_qq,
)

__all__ = [
    "registry",
    "PLUGIN_BROKEN_MARK",
    "NCATBOT_PATH",
    "TEST_PLUGIN",
    "NUMBER_SAVE",
    "PYPI_SOURCE",
    "BotClient",
    "LOG",
    "config",
    "get_log",
    "get_proxy_url",
    "get_plugin_info_by_name",
    "get_qq",
    "install_plugin_dependencies",
]
