import os
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from tqdm import tqdm as tqdm_original

from .Color import Color

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
        kwargs.setdefault("bar_format", "{desc} {percentage:3.0f}%[{n_fmt}]|{bar:20}|[{elapsed}]")
        kwargs.setdefault("ncols", 60)
        kwargs.setdefault("colour", "green")
        kwargs.setdefault("desc", "Loading")
        kwargs.setdefault("unit", "items")
        kwargs.setdefault("leave", False)
        super().__init__(*args, **kwargs)

# 定义日志级别到颜色的映射
LOG_LEVEL_TO_COLOR = {
    'DEBUG': Color.CYAN,
    'INFO': Color.GREEN,
    'WARNING': Color.YELLOW,
    'ERROR': Color.RED,
    'CRITICAL': Color.MAGENTA
}


# 定义彩色格式化器
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        # 获取日志级别并添加颜色
        levelname = record.levelname
        record.levelname = LOG_LEVEL_TO_COLOR[levelname] + levelname + Color.RESET
        return super().format(record)


# 初始化日志配置
def setup_logging():
    # 从环境变量中读取日志配置，如果环境变量不存在则使用默认值
    log_level = os.getenv('LOG_LEVEL', 'DEBUG').upper()  # 确保日志级别为大写
    log_format = os.getenv('LOG_FORMAT', '[%(levelname)s] (%(filename)s:%(lineno)d) %(funcName)s : %(message)s')
    log_file_format = os.getenv('LOG_FILE_FORMAT', '(%(asctime)s) (%(filename)s:%(lineno)d) %(funcName)s \n %(message)s')
    log_file_path = os.getenv('LOG_FILE_PATH', './logs')
    log_file_name = os.getenv('LOG_FILE_NAME', 'bot_%Y%m%d.log')
    backup_count = int(os.getenv('BACKUP_COUNT', 7))
    
    # export LOG_LEVEL=INFO
    # export LOG_FORMAT='[%(asctime)s] %(levelname)s: %(message)s'
    # export LOG_FILE_PATH=./logs
    # export LOG_FILE_NAME=Ncatbot_%Y%m%d.log
    # export BACKUP_COUNT=7

    # 创建日志文件夹
    os.makedirs(log_file_path, exist_ok=True)

    # 生成日志文件的完整路径
    log_file_full_path = os.path.join(log_file_path, datetime.now().strftime(log_file_name))

    # 创建日志对象
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # 创建控制台处理器并设置格式化器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter(log_format))

    # 创建文件处理器并设置格式化器
    file_handler = TimedRotatingFileHandler(
        filename=log_file_full_path,
        when='midnight',
        interval=1,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(log_file_format))

    # 将处理器添加到日志对象
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


# 初始化日志配置
setup_logging()


def get_logger(name):
    return logging.getLogger(name)


# 示例用法
if __name__ == "__main__":
    from time import sleep
    from tqdm.contrib.logging import logging_redirect_tqdm
    logger = get_logger(__name__)
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
        with tqdm(range(0,100)) as pbar:
            for i in pbar:
                if i % 10 == 0:
                    logger.info(f'now: {i}')
                sleep(0.1)