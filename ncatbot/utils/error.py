from .config import ncatbot_config
from .logger import get_log
import traceback

class NcatBotError(Exception):
    logger = get_log("NcatBotError")
    def __init__(self, info, log: bool = True):
        if log:
            self.logger.error(f"{info}")
            if ncatbot_config.debug:
                self.logger.info(f"stacktrace:\n{traceback.format_exc()}")
        super().__init__(info)

class NcatBotValueError(NcatBotError):
    def __init__(self, var_name, val_name, must_be: bool = False):
        super().__init__(f"{var_name} 的值{'必须' if must_be else '不能'}为 {val_name}")
        
class NcatBotConnectionError(Exception):
    def __init__(self, info):
        super().__init__(f"网络连接错误: {info}")