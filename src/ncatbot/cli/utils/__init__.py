"""Command-line utilities for NcatBot."""

# Constants
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
]
