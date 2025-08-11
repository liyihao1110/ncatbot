"""NcatBot 工具包。"""

from ncatbot.utils.config import ncatbot_config
from ncatbot.utils.config import ncatbot_config as config
from ncatbot.utils.logger import get_log
from ncatbot.utils.status import Status, status
from ncatbot.utils.network_io import get_proxy_url
from ncatbot.utils.error import NcatBotError, NcatBotValueError
from ncatbot.utils.thread_pool import ThreadPool

# Re-export assets
from ncatbot.utils.assets import (
    Color,
    NAPCAT_WEBUI_SALT,
    WINDOWS_NAPCAT_DIR,
    LINUX_NAPCAT_DIR,
    INSTALL_SCRIPT_URL,
    NAPCAT_CLI_URL,
    PYPI_URL,
    NAPCAT_CLI_PATH,
    REQUEST_SUCCESS,
    OFFICIAL_GROUP_MESSAGE_EVENT,
    OFFICIAL_PRIVATE_MESSAGE_EVENT,
    OFFICIAL_REQUEST_EVENT,
    OFFICIAL_NOTICE_EVENT,
    OFFICIAL_STARTUP_EVENT,
    OFFICIAL_SHUTDOWN_EVENT,
    OFFICIAL_HEARTBEAT_EVENT,
    PLUGIN_BROKEN_MARK,
    STATUS_ONLINE,
    STATUS_Q_ME,
    STATUS_LEAVE,
    STATUS_BUSY,
    STATUS_DND,
    STATUS_HIDDEN,
    STATUS_LISTENING,
    STATUS_LOVE_YOU,
    STATUS_LEARNING,
    Status as StatusConstants,
    PermissionGroup,
    DefaultPermission,
    EVENT_QUEUE_MAX_SIZE,
    PLUGINS_DIR,
    META_CONFIG_PATH,
    PERSISTENT_DIR
)

__all__ = [
    # 配置导出
    "ncatbot_config",
    "config",
    
    # 日志导出
    "get_log",
    
    # 状态导出
    "status",
    "Status",
    
    # 网络工具
    "get_proxy_url",
    
    # 错误处理
    "NcatBotError",
    "NcatBotValueError"
    
    # 线程池
    "ThreadPool",
    
    # 资源/常量
    "Color",
    "NAPCAT_WEBUI_SALT",
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
    "OFFICIAL_STARTUP_EVENT",
    "OFFICIAL_SHUTDOWN_EVENT",
    "OFFICIAL_HEARTBEAT_EVENT",
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
    "StatusConstants",
    "PermissionGroup",
    "DefaultPermission",
    "EVENT_QUEUE_MAX_SIZE",
    "PLUGINS_DIR",
    "META_CONFIG_PATH",
    "PERSISTENT_DIR"
]