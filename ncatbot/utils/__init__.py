"""NcatBot 工具包。"""

from ncatbot.utils.config import ncatbot_config
from ncatbot.utils.logger import (
    get_log,
)
from ncatbot.utils.network_io import (
    get_proxy_url,
)
from ncatbot.utils.status import Status, status

# 常量
PLUGINS_DIR = "plugins"  # 插件目录

# 工具函数


__all__ = [
    # 日志导出
    "get_log",
    # 配置导出
    "ncatbot_config",
    # 状态导出
    "Status",
    "status",
    # 常量
    "PLUGINS_DIR",
    # 工具函数
    "get_proxy_url",
]
