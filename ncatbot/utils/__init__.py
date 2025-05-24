"""NcatBot 工具包。"""

from ncatbot.utils.config import ncatbot_config
from ncatbot.utils.logger import (
    get_log,
)
from ncatbot.utils.network_io import (
    get_proxy_url,
)
from ncatbot.utils.status import Status, status

from ncatbot.utils.color import Color
from ncatbot.utils.change_dir import ChangeDir
from ncatbot.utils.time_task_scheduler import TimeTaskScheduler
from ncatbot.utils.universal_data_IO import UniversalLoader

# 常量｜移动到 Config.plugin.plugins_dir
# PLUGINS_DIR = "plugins"  # 插件目录

# 工具函数
from ncatbot.utils.visualize_data import visualize_tree


__all__ = [
    # 日志导出
    "get_log",
    # 配置导出
    "ncatbot_config",
    # 状态导出
    "status",
    # 工具
    "get_proxy_url",
    "visualize_tree",
    "Color",
    "ChangeDir",
    "TimeTaskScheduler",
    "UniversalLoader",
]
