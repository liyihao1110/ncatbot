# -*- coding: utf-8 -*-
""" 日志相关, 用于输出日志, 用于输出日志到文件 """
import os
import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# 日志名称
LOGGER_NAME = "Ncatbot"
# 日志级别
LOG_LEVEL = "DEBUG"

# 控制台输出格式
LOG_FORMAT = "[%(levelname)s] (%(asctime)s) (%(filename)s:%(lineno)d) %(funcName)s \n %(message)s"

# 文件输出格式
LOG_FILE_FORMAT = "(%(asctime)s) (%(filename)s:%(lineno)d) %(funcName)s \n %(message)s"

# 颜色映射
COLOR_MAP = {
    'DEBUG': '\033[36m',  # 青色
    'INFO': '\033[32m',   # 绿色
    'WARNING': '\033[33m',  # 黄色
    'ERROR': '\033[31m',  # 红色
    'CRITICAL': '\033[35m'  # 洋红色
}

RESET_COLOR = '\033[0m'

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        record.levelname = COLOR_MAP[levelname] + levelname + RESET_COLOR
        return super().format(record)

def get_logger():
    """
    获取日志对象
    :return: 日志对象
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(LOG_LEVEL)

    # 检查是否已经添加了处理器
    if not logger.hasHandlers():
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter(LOG_FORMAT))  # 颜色输出控制台

        # 创建文件处理器
        log_file_name = os.path.join(os.getcwd(), "Ncatbot_%s.log" % datetime.now().strftime("%Y%m%d"))
        file_handler = TimedRotatingFileHandler(
            filename=log_file_name,
            when='midnight',
            interval=1,
            backupCount=7,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(LOG_FILE_FORMAT))  # 普通文本输出文件日志

        # 将处理器添加到日志对象
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
