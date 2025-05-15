"""Command-line utilities for NcatBot."""

# Constants
# CLI exceptions
from ncatbot.cli.utils.cli_exceptions import CLIExit

# Color utilities
from ncatbot.cli.utils.colors import (
    Colors,
    ColorScheme,
    alias,
    category,
    colorize,
    command,
    description,
    error,
    get_category_color,
    header,
    info,
    success,
    title,
    usage,
    warning,
)
from ncatbot.cli.utils.constants import (
    PLUGIN_INDEX_URL,
    PYPI_SOURCE,
)

# Package management
from ncatbot.cli.utils.pip_tool import (
    install_pip_dependencies,
)

# Plugin utils
from ncatbot.cli.utils.plugin_utils import (
    download_plugin_file,
    get_plugin_index,
    get_plugin_versions,
)

__all__ = [
    # Constants
    "PYPI_SOURCE",
    "NUMBER_SAVE",
    "PLUGIN_INDEX_URL",
    # Plugin utilities
    "get_plugin_index",
    "download_plugin_file",
    "get_plugin_versions",
    # Package management
    "install_pip_dependencies",
    # CLI exceptions
    "CLIExit",
    # Color utilities
    "Colors",
    "ColorScheme",
    "colorize",
    "command",
    "category",
    "description",
    "usage",
    "alias",
    "error",
    "success",
    "warning",
    "info",
    "header",
    "title",
    "get_category_color",
]
