from ncatbot.utils.assets import *
from ncatbot.utils.config import config
from ncatbot.utils.file_io import (
    UniversalLoader,
    convert_uploadable_object,
    read_file,
    unzip_file,
)
from ncatbot.utils.logger import get_log
from ncatbot.utils.network_io import download_file, get_proxy_url
from ncatbot.utils.optional import *

__all__ = [
    "SetConfig",
    "get_log",
    "get_proxy_url",
    "download_file",
    "UniversalLoader",
    "read_file",
    "convert_uploadable_object",
    "unzip_file",
    "config",
    # literals
    "WINDOWS_NAPCAT_DIR",
    "LINUX_NAPCAT_DIR",
    "INSTALL_SCRIPT_URL",
    "NAPCAT_CLI_URL",
    "PYPI_URL",
    "NAPCAT_CLI_PATH",
    "REQUEST_SUCCESS",
    "OFFICIAL_GROUP_MESSAGE_EVENT",
    "OFFICIAL_PRIVATE_MESSAGE_EVENT",
    "OFFICIAL_REQUEST_EVENT",
    "OFFICIAL_NOTICE_EVENT",
    "PLUGIN_BROKEN_MARK",
    "STATUS_ONLINE",
    "STATUS_Q_ME",
    "STATUS_LEAVE",
    "STATUS_BUSY",
    "STATUS_DND",
    "STATUS_HIDDEN",
    "STATUS_LISTENING",
    "STATUS_LOVE_YOU",
    "STATUS_LEARNING",
    "Status",
    "PermissionGroup",
    "DefaultPermission",
    "EVENT_QUEUE_MAX_SIZE",
    "PLUGINS_DIR",
    "META_CONFIG_PATH",
    "PERSISTENT_DIR",
    # custom errors
    "PluginCircularDependencyError",
    "PluginNotFoundError",
    "PluginLoadError",
    "PluginDependencyError",
    "PluginVersionError",
    "PluginUnloadError",
    "InvalidPluginStateError",
]
