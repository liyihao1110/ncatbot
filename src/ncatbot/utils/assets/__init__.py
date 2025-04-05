# 静态资源


from ncatbot.utils.assets.color import Color
from ncatbot.utils.assets.literals import *
from ncatbot.utils.assets.plugin_custom_err import *

__all__ = [
    "PluginCircularDependencyError",
    "PluginDependencyError",
    "PluginNotFoundError",
    "PluginVersionError",
    "Color",
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
