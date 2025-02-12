import logging
import os
import warnings
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from tqdm import tqdm as tqdm_original


class Color:
    """
    用于在终端中显示颜色和样式。

    包含以下功能：
    - 前景：设置颜
    - 背景：设置背景颜
    - 样式：设置样式（如加粗、下划线、反转）
    - RESET：重置所有颜和样式
    """

    # 前景
    BLACK = "\033[30m"
    """前景-黑"""
    RED = "\033[31m"
    """前景-红"""
    GREEN = "\033[32m"
    """前景-绿"""
    YELLOW = "\033[33m"
    """前景-黄"""
    BLUE = "\033[34m"
    """前景-蓝"""
    MAGENTA = "\033[35m"
    """前景-品红"""
    CYAN = "\033[36m"
    """前景-青"""
    WHITE = "\033[37m"
    """前景-白"""
    RESET = "\033[0m"
    """重置所有颜色和样式"""

    # 扩展前景
    LIGHT_GRAY = "\033[90m"
    """前景-亮灰"""
    LIGHT_RED = "\033[91m"
    """前景-亮红"""
    LIGHT_GREEN = "\033[92m"
    """前景-亮绿"""
    LIGHT_YELLOW = "\033[93m"
    """前景-亮黄"""
    LIGHT_BLUE = "\033[94m"
    """前景-亮蓝"""
    LIGHT_MAGENTA = "\033[95m"
    """前景-亮品红"""
    LIGHT_CYAN = "\033[96m"
    """前景-亮青"""
    LIGHT_WHITE = "\033[97m"
    """前景-亮白"""

    # 背景
    BG_BLACK = "\033[40m"
    """背景-黑"""
    BG_RED = "\033[41m"
    """背景-红"""
    BG_GREEN = "\033[42m"
    """背景-绿"""
    BG_YELLOW = "\033[43m"
    """背景-黄"""
    BG_BLUE = "\033[44m"
    """背景-蓝"""
    BG_MAGENTA = "\033[45m"
    """背景-品红"""
    BG_CYAN = "\033[46m"
    """背景-青"""
    BG_WHITE = "\033[47m"
    """背景-白"""

    # 扩展背景
    BG_LIGHT_GRAY = "\033[100m"
    """背景-亮灰"""
    BG_LIGHT_RED = "\033[101m"
    """背景-亮红"""
    BG_LIGHT_GREEN = "\033[102m"
    """背景-亮绿"""
    BG_LIGHT_YELLOW = "\033[103m"
    """背景-亮黄"""
    BG_LIGHT_BLUE = "\033[104m"
    """背景-亮蓝"""
    BG_LIGHT_MAGENTA = "\033[105m"
    """背景-亮品红"""
    BG_LIGHT_CYAN = "\033[106m"
    """背景-亮青"""
    BG_LIGHT_WHITE = "\033[107m"
    """背景-亮白"""

    # 样式
    BOLD = "\033[1m"
    """加粗"""
    UNDERLINE = "\033[4m"
    """下划线"""
    REVERSE = "\033[7m"
    """反转（前景色和背景色互换）"""
    ITALIC = "\033[3m"
    """斜体"""
    BLINK = "\033[5m"
    """闪烁"""
    STRIKE = "\033[9m"
    """删除线"""


# 定义自定义的 tqdm 类，继承自原生的 tqdm 类
class tqdm(tqdm_original):
    def __init__(self, *args, **kwargs):
        """
        自定义 tqdm 类的初始化方法。
        通过设置默认参数，确保每次创建 tqdm 进度条时都能应用统一的风格。

        参数说明：
        :param args: 原生 tqdm 支持的非关键字参数（如可迭代对象等）。
        :param kwargs: 原生 tqdm 支持的关键字参数，用于自定义进度条的行为和外观。
            - bar_format (str): 进度条的格式化字符串。
            - ncols (int): 进度条的宽度（以字符为单位）。
            - colour (str): 进度条的颜色。
            - desc (str): 进度条的描述信息。
            - unit (str): 进度条的单位。
            - leave (bool): 进度条完成后是否保留显示。
        """
        kwargs.setdefault(
            "bar_format", "{desc} {percentage:3.0f}%[{n_fmt}]|{bar:20}|[{elapsed}]"
        )
        kwargs.setdefault("ncols", 60)
        kwargs.setdefault("colour", "green")
        kwargs.setdefault("desc", "Loading")
        kwargs.setdefault("unit", "items")
        kwargs.setdefault("leave", False)
        super().__init__(*args, **kwargs)


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
    def format(self, record):
        # 获取日志级别并添加颜色
        levelname = record.levelname
        colored_level = LOG_LEVEL_TO_COLOR[levelname] + levelname + Color.RESET
        # 替换 record.levelname 为带颜色的版本
        record.colored_levelname = colored_level
        return super().format(record)


def _get_valid_log_level(level_name, default):
    """验证并获取有效的日志级别"""
    level = getattr(logging, level_name.upper(), None)
    if not isinstance(level, int):
        warnings.warn(f"Invalid log level: {level_name}, using {default} instead.")
        return getattr(logging, default)
    return level


def setup_logging():
    """设置日志"""
    # 环境变量读取
    console_level = os.getenv("LOG_LEVEL", "INFO")
    file_level = os.getenv("FILE_LOG_LEVEL", "DEBUG")

    # 验证并转换日志级别
    console_log_level = _get_valid_log_level(console_level, "INFO")
    file_log_level = _get_valid_log_level(file_level, "DEBUG")

    # 日志格式配置
    log_format = os.getenv(
        "LOG_FORMAT",
        "[%(colored_levelname)s] (%(filename)s:%(lineno)d) %(funcName)s : %(message)s",
    )
    file_format = os.getenv(
        "LOG_FILE_FORMAT",
        "[%(levelname)s] (%(asctime)s) (%(filename)s:%(lineno)d) %(funcName)s %(message)s",
    )

    # 文件路径配置
    log_dir = os.getenv("LOG_FILE_PATH", "./logs")
    file_name = os.getenv("LOG_FILE_NAME", "bot_%Y%m%d.log")

    # 备份数量验证
    try:
        backup_count = int(os.getenv("BACKUP_COUNT", "7"))
    except ValueError:
        backup_count = 7
        warnings.warn("Invalid BACKUP_COUNT value, using default 7")

    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, datetime.now().strftime(file_name))

    # 配置根日志器
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # 全局最低级别设为DEBUG

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_log_level)
    console_handler.setFormatter(ColoredFormatter(log_format))

    # 文件处理器
    file_handler = TimedRotatingFileHandler(
        filename=file_path,
        when="midnight",
        interval=1,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(file_log_level)
    file_handler.setFormatter(logging.Formatter(file_format))

    # 初始化并添加处理器
    logger.handlers = []
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(min([handler.level for handler in logger.handlers]))


# 初始化日志配置
setup_logging()


def get_log(name="ncatbot"):
    """获取日志记录器"""
    return logging.getLogger(name)


# 示例用法
if __name__ == "__main__":
    from time import sleep

    from tqdm.contrib.logging import logging_redirect_tqdm

    logger = get_log()
    logger.debug("这是一个调试信息")
    logger.info("这是一个普通信息")
    logger.warning("这是一个警告信息")
    logger.error("这是一个错误信息")
    logger.critical("这是一个严重错误信息")
    # 常见参数
    # total：总进度数。
    # desc：进度条描述。
    # ncols：进度条宽度。
    # unit：进度单位。
    # leave：是否在完成后保留进度条。

    with logging_redirect_tqdm():
        with tqdm(range(0, 100)) as pbar:
            for i in pbar:
                if i % 10 == 0:
                    logger.info(f"now: {i}")
                sleep(0.1)
