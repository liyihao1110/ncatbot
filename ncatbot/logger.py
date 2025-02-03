import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler

LOG_COLORS_CONFIG = {
    "DEBUG": "\033[1;34m",
    "INFO": "\033[1;32m",
    "WARNING": "\033[1;33m",
    "ERROR": "\033[1;31m",
    "CRITICAL": "\033[1;31m",
    "RESET": "\033[0m"
}

DEFAULT_LOGGER_NAME = "ncatbot"

DEFAULT_PRINT_FORMAT = "{reset}[{color}{levelname:<8}{reset}] ({filename}:{lineno}) {funcName}: {message}"
DEFAULT_FILE_FORMAT = "%(asctime)s\t[%(levelname)s]\t(%(filename)s:%(lineno)s) %(funcName)s()\t%(message)s"


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_color = LOG_COLORS_CONFIG.get(record.levelname.upper(), "")
        reset = LOG_COLORS_CONFIG["RESET"]
        record.color = log_color
        record.reset = reset
        return super().format(record)


def get_log(name=DEFAULT_LOGGER_NAME):
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter(DEFAULT_PRINT_FORMAT, style="{"))

    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(os.getcwd(), f"{name}.log"),
        when="D",
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(DEFAULT_FILE_FORMAT))

    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger



