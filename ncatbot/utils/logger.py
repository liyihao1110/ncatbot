# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-12 13:41:02
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-15 16:14:50
# @Description  : 日志类
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
import logging
import os
import warnings
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import Optional

from tqdm import tqdm as tqdm_original

from ncatbot.utils.assets.color import Color
from ncatbot.utils.status import status


# 定义自定义的 tqdm 类,继承自原生的 tqdm 类
class tqdm(tqdm_original):
    """
    自定义 tqdm 类的初始化方法。
    通过设置默认参数,确保每次创建 tqdm 进度条时都能应用统一的风格。

    参数说明:
    :param args: 原生 tqdm 支持的非关键字参数（如可迭代对象等）。
    :param kwargs: 原生 tqdm 支持的关键字参数,用于自定义进度条的行为和外观。
        - bar_format (str): 进度条的格式化字符串。
        - ncols (int): 进度条的宽度（以字符为单位）。
        - colour (str): 进度条的颜色。
        - desc (str): 进度条的描述信息。
        - unit (str): 进度条的单位。
        - leave (bool): 进度条完成后是否保留显示。
    """

    _STYLE_MAP = {
        "BLACK,": Color.BLACK,
        "RED": Color.RED,
        "GREEN": Color.GREEN,
        "YELLOW": Color.YELLOW,
        "BLUE": Color.BLUE,
        "MAGENTA": Color.MAGENTA,
        "CYAN": Color.CYAN,
        "WHITE": Color.WHITE,
    }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "bar_format",
            f"{Color.CYAN}{{desc}}{Color.RESET} "
            f"{Color.WHITE}{{percentage:3.0f}}%{Color.RESET}"
            f"{Color.GRAY}[{{n_fmt}}]{Color.RESET}"
            f"{Color.WHITE}|{{bar:20}}|{Color.RESET}"
            f"{Color.BLUE}[{{elapsed}}]{Color.RESET}",
        )
        kwargs.setdefault("ncols", 80)
        kwargs.setdefault("colour", "green")
        super().__init__(*args, **kwargs)

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, color):
        # 确保颜色值有效
        valid_color = self._STYLE_MAP.get(color, "GREEN")  # 如果无效,回退到 GREEN
        self._colour = valid_color
        self.desc = f"{getattr(Color, valid_color)}{self.desc}{Color.RESET}"


# 日志级别颜色映射
LOG_LEVEL_TO_COLOR = {
    "DEBUG": Color.CYAN,
    "INFO": Color.GREEN,
    "WARNING": Color.YELLOW,
    "ERROR": Color.RED,
    "CRITICAL": Color.MAGENTA,
}


# 定义彩色格式化器
class ColoredFormatter(logging.Formatter):
    use_color = True

    def format(self, record):
        try:
            # 动态颜色处理
            if self.use_color:
                record.colored_levelname = (
                    f"{LOG_LEVEL_TO_COLOR.get(record.levelname, Color.RESET)}"
                    f"{record.levelname:8}"
                    f"{Color.RESET}"
                )
                # 添加统一颜色字段
                record.colored_name = f"{Color.MAGENTA}{record.name}{Color.RESET}"
                record.colored_time = (
                    f"{Color.CYAN}{self.formatTime(record)}{Color.RESET}"
                )
            else:
                record.colored_levelname = record.levelname
                record.colored_name = record.name
                record.colored_time = self.formatTime(record)

            return super().format(record)
        except Exception as e:
            warnings.warn(f"日志格式化错误: {str(e)}")
            return f"[FORMAT ERROR] {record.getMessage()}"


def _get_valid_log_level(level_name: str, default: str):
    """验证并获取有效的日志级别"""
    level = getattr(logging, level_name.upper(), None)
    if not isinstance(level, int):
        warnings.warn(f"Invalid log level: {level_name}, using {default} instead.")
        return getattr(logging, default)
    return level


# 创建用于区分 get_log 创建的日志和其他日志的过滤器
class LoggerOriginFilter(logging.Filter):
    """过滤器，根据日志记录器的来源进行过滤。

    可以过滤出通过 get_log 创建的记录器或未通过 get_log 创建的记录器。
    """

    def __init__(self, from_get_log: bool = True):
        """初始化过滤器。

        Args:
            from_get_log: 如果为 True，只保留通过 get_log 创建的记录器的日志；
                         如果为 False，只保留未通过 get_log 创建的记录器的日志
        """
        super().__init__()
        self.from_get_log = from_get_log

    def filter(self, record: logging.LogRecord) -> bool:
        """过滤日志记录。

        Args:
            record: 日志记录

        Returns:
            bool: 如果应该保留日志记录则为 True，否则为 False
        """
        # 确定日志记录器是否是通过 get_log 创建的
        is_registered = status.is_registered_logger(record.name)

        # 根据我们想要过滤的内容返回 True 或 False
        return is_registered if self.from_get_log else not is_registered


def setup_logging():
    """设置日志"""
    # 环境变量读取
    console_level = os.getenv("LOG_LEVEL", "INFO").upper()
    file_level = os.getenv("FILE_LOG_LEVEL", "DEBUG").upper()

    # 为了保证有效日志信息仅支持控制台
    console_log_format = os.getenv("LOG_FORMAT", None)

    # 验证并转换日志级别
    console_log_level = _get_valid_log_level(console_level, "INFO")
    file_log_level = _get_valid_log_level(file_level, "DEBUG")

    # 日志格式配置
    default_log_format = {
        "console": {
            "DEBUG": f"{Color.CYAN}[%(asctime)s.%(msecs)03d]{Color.RESET} "
            f"{Color.BLUE}%(colored_levelname)-8s{Color.RESET} "
            f"{Color.GRAY}[%(threadName)s|%(processName)s]{Color.RESET} "
            f"{Color.MAGENTA}%(name)s{Color.RESET} "
            f"{Color.YELLOW}%(filename)s:%(funcName)s:%(lineno)d{Color.RESET} "
            "| %(message)s",
            "INFO": f"{Color.CYAN}[%(asctime)s.%(msecs)03d]{Color.RESET} "
            f"{Color.GREEN}%(colored_levelname)-8s{Color.RESET} "
            f"{Color.MAGENTA}%(name)s{Color.RESET} ➜ "
            f"{Color.WHITE}%(message)s{Color.RESET}",
            "WARNING": f"{Color.CYAN}[%(asctime)s.%(msecs)03d]{Color.RESET} "
            f"{Color.YELLOW}%(colored_levelname)-8s{Color.RESET} "
            f"{Color.MAGENTA}%(name)s{Color.RESET} "
            f"{Color.RED}➜{Color.RESET} "
            f"{Color.YELLOW}%(message)s{Color.RESET}",
            "ERROR": f"{Color.CYAN}[%(asctime)s.%(mctime)s.%(msecs)03d]{Color.RESET} "
            f"{Color.RED}%(colored_levelname)-8s{Color.RESET} "
            f"{Color.GRAY}[%(filename)s]{Color.RESET}"
            f"{Color.MAGENTA}%(name)s:%(lineno)d{Color.RESET} "
            f"{Color.RED}➜{Color.RESET} "
            f"{Color.RED}%(message)s{Color.RESET}",
            "CRITICAL": f"{Color.CYAN}[%(asctime)s.%(msecs)03d]{Color.RESET} "
            f"{Color.BG_RED}{Color.WHITE}%(colored_levelname)-8s{Color.RESET} "
            f"{Color.GRAY}{{%(module)s}}{Color.RESET}"
            f"{Color.MAGENTA}[%(filename)s]{Color.RESET}"
            f"{Color.MAGENTA}%(name)s:%(lineno)d{Color.RESET} "
            f"{Color.BG_RED}➜{Color.RESET} "
            f"{Color.BOLD}%(message)s{Color.RESET}",
        },
        "file": {
            "DEBUG": "[%(asctime)s.%(msecs)03d] %(levelname)-8s [%(threadName)s|%(processName)s] %(name)s (%(filename)s:%(funcName)s:%(lineno)d) | %(message)s",
            "INFO": "[%(asctime)s.%(msecs)03d] %(levelname)-8s %(name)s ➜ %(message)s",
            "WARNING": "[%(asctime)s.%(msecs)03d] %(levelname)-8s %(name)s ➜ %(message)s",
            "ERROR": "[%(asctime)s.%(msecs)03d] %(levelname)-8s [%(filename)s]%(name)s:%(lineno)d ➜ %(message)s",
            "CRITICAL": "[%(asctime)s.%(msecs)03d] %(levelname)-8s {%(module)s}[%(filename)s]%(name)s:%(lineno)d ➜ %(message)s",
        },
    }

    # 日志格式配置
    log_format = os.getenv(
        "LOG_FORMAT", console_log_format or default_log_format["console"][console_level]
    )
    file_format = os.getenv("LOG_FILE_FORMAT", default_log_format["file"][file_level])

    # 文件路径配置
    log_dir = os.getenv("LOG_FILE_PATH", "./logs")
    core_file_name = os.getenv("LOG_FILE_NAME", "bot_%Y_%m_%d.log")
    full_file_name = os.getenv("FULL_LOG_FILE_NAME", "full_bot_%Y_%m_%d.log")

    # 备份数量验证
    try:
        backup_count = int(os.getenv("BACKUP_COUNT", "7"))
    except ValueError:
        backup_count = 7
        warnings.warn("BACKUP_COUNT 为无效值,使用默认值 7")
        os.environ["BACKUP_COUNT"] = 7

    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    core_file_path = os.path.join(log_dir, datetime.now().strftime(core_file_name))
    full_file_path = os.path.join(log_dir, datetime.now().strftime(full_file_name))

    # 配置根日志器
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # 全局最低级别设为DEBUG

    # 移除所有现有的处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(ColoredFormatter(log_format))
    console_handler.addFilter(LoggerOriginFilter(from_get_log=True))

    # 核心日志文件处理器（只包含通过 get_log 获取的日志记录器产生的日志）
    core_file_handler = TimedRotatingFileHandler(
        filename=core_file_path,
        when="midnight",
        interval=1,
        backupCount=backup_count,
        encoding="utf-8",
    )
    core_file_handler.setLevel(logging.DEBUG)
    core_file_handler.setFormatter(logging.Formatter(file_format))
    # 添加过滤器，只记录通过 get_log 创建的日志记录器产生的日志
    core_file_handler.addFilter(LoggerOriginFilter(from_get_log=True))

    # 全量日志文件处理器（包含所有日志）
    full_file_handler = TimedRotatingFileHandler(
        filename=full_file_path,
        when="midnight",
        interval=1,
        backupCount=backup_count,
        encoding="utf-8",
    )
    full_file_handler.setLevel(logging.DEBUG)
    full_file_handler.setFormatter(logging.Formatter(file_format))

    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(core_file_handler)
    logger.addHandler(full_file_handler)

    # 记录日志设置信息
    logging.getLogger("logger_setup").debug(
        f"日志配置完成: 控制台级别={console_level}, "
        f"文件级别={file_level}, "
        f"核心日志文件={core_file_path}, "
        f"全量日志文件={full_file_path}"
    )


# 初始化日志配置
setup_logging()


def get_log(name: Optional[str] = None) -> logging.Logger:
    """获取日志记录器。

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 注册到状态管理器
    if name is not None:
        status.register_logger(name)

    # 如果已经有处理器，说明已经配置过，直接返回
    return logger
