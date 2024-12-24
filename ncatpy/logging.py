# encoding: utf-8

import os
import sys
import json
import yaml
import logging
import logging.config
from typing import List, Dict, Union
from logging.handlers import TimedRotatingFileHandler

LOG_COLORS_CONFIG = {
    "DEBUG": "blue",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "purple",
}

DEFAULT_LOGGER_NAME = "ncatpy"

DEFAULT_PRINT_FORMAT = "\033[1;33m[%(levelname)s]\t(%(filename)s:%(lineno)s)%(funcName)s\t\033[0m%(message)s"
DEFAULT_FILE_FORMAT = "%(asctime)s\t[%(levelname)s]\t(%(filename)s:%(lineno)s)%(funcName)s\t%(message)s"
logging.basicConfig(format=DEFAULT_PRINT_FORMAT)

DEFAULT_FILE_HANDLER = {
    "handler": TimedRotatingFileHandler,
    "format": "%(asctime)s\t[%(levelname)s]\t(%(filename)s:%(lineno)s)%(funcName)s\t%(message)s",
    "level": logging.DEBUG,
    "when": "D",
    "backupCount": 7,
    "encoding": "utf-8",
    "filename": os.path.join(os.getcwd(), "%(name)s.log"),
}

logs: Dict[str, logging.Logger] = {}

_ext_handlers: List[dict] = []

os.system("")

def get_handler(handler, name=DEFAULT_LOGGER_NAME):
    handler = handler.copy()
    if "filename" in handler:
        handler["filename"] = handler["filename"] % {"name": name}

    lever = handler.get("level") or logging.DEBUG
    _format = handler.get("format") or DEFAULT_FILE_FORMAT

    for k in ["level", "format"]:
        if k in handler:
            handler.pop(k)

    handler = handler.pop("handler")(**handler)
    handler.setLevel(lever)
    handler.setFormatter(logging.Formatter(_format))
    return handler

def get_logger(name=None):
    global logs

    if not name:
        name = DEFAULT_LOGGER_NAME
    if name in logs:
        return logs[name]

    logger = logging.getLogger(name)
    argv = sys.argv
    if "-d" in argv or "--debug" in argv:
        logger.setLevel(level=logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    if _ext_handlers:
        for handler in _ext_handlers:
            logger.addHandler(get_handler(handler, name))

    logs[name] = logger
    return logger

def configure_logging(
        config: Union[str, dict] = None,
        _format: str = None,
        level: int = None,
        bot_log: Union[bool, None] = True,
        ext_handlers: Union[dict, List, bool] = None,
        force: bool = False
) -> None:
    global _ext_handlers

    if config is not None:
        if isinstance(config, dict):
            logging.config.dictConfig(config)
        elif config.endswith(".json"):
            with open(config) as file:
                loaded_config = json.load(file)
                logging.config.dictConfig(loaded_config)
        elif config.endswith((".yaml", ".yml")):
            with open(config) as file:
                loaded_config = yaml.safe_load(file)
                logging.config.dictConfig(loaded_config)
        else:
            logging.config.fileConfig(
                config, disable_existing_loggers=False
            )

    if _format is not None:
        logging.basicConfig(format=_format)

    if level is not None:
        for name, logger in logs.items():
            logger.setLevel(level)

    if not bot_log:
        logger = logging.getLogger(DEFAULT_LOGGER_NAME)
        if bot_log is False:
            logger.propagate = False
        if DEFAULT_LOGGER_NAME in logs:
            logs.pop(DEFAULT_LOGGER_NAME)

        logger.handlers = []

    if ext_handlers and (not _ext_handlers or force):
        if ext_handlers is True:
            ext_handlers = [DEFAULT_FILE_HANDLER]
        elif not isinstance(ext_handlers, list):
            ext_handlers = [ext_handlers]

        _ext_handlers.extend(ext_handlers)

        for name, logger in logs.items():
            for handler in ext_handlers:
                logger.addHandler(get_handler(handler, name))
