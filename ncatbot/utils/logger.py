# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-12 13:41:02
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-15 16:14:50
# @Description  : 日志类
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
import os
import re
import logging
import warnings
from typing import Optional, Dict, Pattern, Tuple, List, Union
from tqdm import tqdm as tqdm_original
from logging.handlers import TimedRotatingFileHandler

from ncatbot.utils.assets.color import Color



# 分配规则 - 支持输出到控制台和多目标匹配
rules = [
    ('database', 'db.log'),      # 数据库日志输出到文件
    ('network', 'network.log'),  # 同时输出到文件
]

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
        "ERROR": f"{Color.CYAN}[%(asctime)s.%(msecs)03d]{Color.RESET} "
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

# -------------------------------------------------
# 1. 自定义 tqdm
# -------------------------------------------------
class tqdm(tqdm_original):
    _STYLE_MAP = {
        "BLACK": Color.BLACK, "RED": Color.RED, "GREEN": Color.GREEN,
        "YELLOW": Color.YELLOW, "BLUE": Color.BLUE,
        "MAGENTA": Color.MAGENTA, "CYAN": Color.CYAN, "WHITE": Color.WHITE,
    }

    def __init__(self, *args, **kwargs):
        self._custom_colour = kwargs.pop("colour", "GREEN")
        kwargs.setdefault("bar_format",
                          f"{Color.CYAN}{{desc}}{Color.RESET} "
                          f"{Color.WHITE}{{percentage:3.0f}}%{Color.RESET} "
                          f"{Color.GRAY}[{{total}}/{{n_fmt}}]{Color.RESET}"
                          f"{Color.WHITE}|{{bar:20}}|{Color.RESET}"
                          f"{Color.BLUE}[{{elapsed}}]{Color.RESET}")
        kwargs.setdefault("ncols", 80)
        kwargs.setdefault("colour", None)
        super().__init__(*args, **kwargs)
        self.colour = self._custom_colour

    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, color: str):
        color = (color or "GREEN").upper()
        valid_color = self._STYLE_MAP.get(color, Color.GREEN)
        self._colour = color
        if self.desc:
            self.desc = f"{valid_color}{self.desc}{Color.RESET}"

# -------------------------------------------------
# 2. 彩色日志
# -------------------------------------------------
LOG_LEVEL_TO_COLOR = {
    "DEBUG": Color.CYAN,
    "INFO": Color.GREEN,
    "WARNING": Color.YELLOW,
    "ERROR": Color.RED,
    "CRITICAL": Color.MAGENTA,
}

class ColoredFormatter(logging.Formatter):
    use_color = True

    def format(self, record: logging.LogRecord) -> str:
        try:
            if self.use_color:
                record.colored_levelname = (
                    f"{LOG_LEVEL_TO_COLOR.get(record.levelname, Color.RESET)}"
                    f"{record.levelname:8}{Color.RESET}"
                )
                record.colored_name = f"{Color.MAGENTA}{record.name}{Color.RESET}"
                record.colored_time = f"{Color.CYAN}{self.formatTime(record)}{Color.RESET}"
            else:
                record.colored_levelname = record.levelname
                record.colored_name = record.name
                record.colored_time = self.formatTime(record)
            return super().format(record)
        except Exception as e:
            warnings.warn(f"日志格式化错误: {e}")
            return f"[FORMAT ERROR] {record.getMessage()}"

# -------------------------------------------------
# 3. 自定义过滤器
# -------------------------------------------------
class RegisteredLoggerFilter(logging.Filter):
    """过滤器：只允许通过 get_log() 注册的 logger 的 DEBUG 信息通过控制台"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        # 非 DEBUG 级别的日志都通过
        if record.levelno != logging.DEBUG:
            return True
        
        # 根 logger 的 DEBUG 信息总是通过
        if not record.name or record.name == "root":
            return True
        
        # DEBUG 级别的日志只有注册过的 logger 才通过
        try:
            from ncatbot.utils.status import status
            return status.is_registered_logger(record.name)
        except ImportError:
            # 如果状态模块未初始化，则默认通过
            return True

# -------------------------------------------------
# 4. 工具函数
# -------------------------------------------------
def _get_valid_log_level(level_name: str, default: str) -> str:
    level_name = level_name.upper()
    if hasattr(logging, level_name) and isinstance(getattr(logging, level_name), int):
        return level_name
    warnings.warn(f"Invalid log level: {level_name}, fallback to {default.upper()}")
    return default.upper()

def _compile_rules(raw_rules: List[Tuple[str, str]]) -> List[Tuple[Pattern, str]]:
    """
    编译规则列表，支持特殊值"console"
    :param raw_rules: 原始规则列表 [(pattern_str, target)]
    :return: 编译后的规则列表 [(compiled_regex, target)]
    """
    compiled_rules = []
    for pattern_str, target in raw_rules:
        try:
            compiled = re.compile(pattern_str)
            compiled_rules.append((compiled, target))
        except re.error as e:
            warnings.warn(f"Invalid regex pattern '{pattern_str}': {e}")
    return compiled_rules

# -------------------------------------------------
# 5. 全局初始化
# -------------------------------------------------
def setup_logging():
    """初始化全局日志系统"""
    # ---- 5.1 读取环境变量 ----
    console_level = _get_valid_log_level(os.getenv("LOG_LEVEL", "DEBUG"), "DEBUG")
    file_level = _get_valid_log_level(os.getenv("FILE_LOG_LEVEL", "DEBUG"), "DEBUG")
    log_dir = os.getenv("LOG_FILE_PATH", "./logs")
    backup_count = int(os.getenv("BACKUP_COUNT", "7"))
    os.makedirs(log_dir, exist_ok=True)

    # ---- 5.2 通用格式 ----
    console_fmt = os.getenv("LOG_FORMAT") or default_log_format["console"][console_level]
    file_fmt = os.getenv("LOG_FILE_FORMAT") or default_log_format["file"][file_level]

    # ---- 5.3 根记录器（控制台 + 主文件） ----
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers.clear()

    # 控制台处理器
    ch = logging.StreamHandler()
    ch.setLevel(console_level)
    ch.setFormatter(ColoredFormatter(console_fmt, datefmt="%H:%M:%S"))
    # 添加注册 logger 过滤器到控制台处理器
    ch.addFilter(RegisteredLoggerFilter())

    # 主文件处理器
    main_file = os.path.join(log_dir, "bot.log")
    fh_main = TimedRotatingFileHandler(
        main_file,
        when="midnight",
        interval=1,
        backupCount=backup_count,
        encoding="utf-8",
    )
    fh_main.suffix = "%Y_%m_%d"
    fh_main.extMatch = re.compile(r"^\d{4}_\d{2}_\d{2}$")
    fh_main.setLevel(file_level)
    fh_main.setFormatter(logging.Formatter(file_fmt))

    root.addHandler(ch)
    root.addHandler(fh_main)

    # ---- 5.4 重定向记录器 ----
    compiled_rules: List[Tuple[Pattern, str]] = _compile_rules(rules)
    
    # 创建过滤器类
    class RegexFilter(logging.Filter):
        def __init__(self, pattern: Pattern):
            super().__init__()
            self.pattern = pattern

        def filter(self, record: logging.LogRecord) -> bool:
            return bool(self.pattern.match(record.name))
    
    # 处理所有规则
    for pattern, target in compiled_rules:
        # 处理文件输出规则
        file_path = os.path.join(log_dir, target)
        file_handler = TimedRotatingFileHandler(
            file_path,
            when="midnight",
            interval=1,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.suffix = "%Y_%m_%d"
        file_handler.extMatch = re.compile(r"^\d{4}_\d{2}_\d{2}$")
        file_handler.setLevel(file_level)
        file_handler.setFormatter(logging.Formatter(file_fmt))
        file_handler.addFilter(RegexFilter(pattern))
        # 添加到根记录器
        root.addHandler(file_handler)

    logging.getLogger("logger").debug("日志系统初始化")

# -------------------------------------------------
# 6. 获取 logger 的快捷函数
# -------------------------------------------------
def get_log(name: Optional[str] = None) -> logging.Logger:
    """返回一个logger；若name为空则返回root logger"""
    logger = logging.getLogger(name)
    
    # 注册非根 logger
    if name is not None:
        try:
            from ncatbot.utils.status import status
            status.register_logger(name)
        except ImportError:
            # 如果状态模块未初始化，则忽略注册
            pass
    
    return logger

# -------------------------------------------------
# 7. 启动时初始化一次
# -------------------------------------------------
setup_logging()

# -------------------------------------------------
# 8. 自测示例
# -------------------------------------------------
if __name__ == "__main__":
    import time
    from tqdm.contrib.logging import logging_redirect_tqdm

    root = get_log()
    db = get_log("database")
    net = get_log("network")
    test = get_log("test.module")

    root.info("启动测试")
    db.warning("数据库连接池 90% - 这条日志应该出现在db.log和bot.log")
    net.info("网络初始化 - 这条日志应该出现在控制台和network.log")
    net.error("连接超时 - 这条日志应该出现在控制台和network.log")
    test.info("测试模块日志 - 这条日志应该出现在bot.log")

    with logging_redirect_tqdm():
        for i in tqdm(range(50), desc="Task"):
            if i % 10 == 0:
                root.info(f"step {i}")
            time.sleep(0.05)

    root.info("测试完成")
    db.info("数据库关闭")
    net.info("网络关闭")
    
    # 打印所有处理器的信息用于调试
    print("\n日志处理器调试信息:")
    print(f"根记录器处理器数量: {len(root.handlers)}")
    for i, handler in enumerate(root.handlers):
        handler_type = type(handler).__name__
        if isinstance(handler, TimedRotatingFileHandler):
            print(f" 处理器 {i+1}: {handler_type} (文件: {handler.baseFilename})")
        elif isinstance(handler, logging.StreamHandler):
            print(f" 处理器 {i+1}: {handler_type} (控制台)")
        else:
            print(f" 处理器 {i+1}: {handler_type}")