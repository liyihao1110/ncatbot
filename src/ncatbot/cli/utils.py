"""Utility functions and constants for NcatBot CLI."""

import os

from ncatbot.utils import get_log

# Constants
PYPI_SOURCE = "https://mirrors.aliyun.com/pypi/simple/"
NCATBOT_PATH = "ncatbot"
TEST_PLUGIN = "TestPlugin"
NUMBER_SAVE = "number.txt"
PLUGIN_INDEX = {}

# Initialize logger
LOG = get_log("CLI")


def get_qq() -> str:
    """Get the QQ number from the saved file."""
    from ncatbot.cli.plugin_commands import install
    from ncatbot.cli.system_commands import set_qq

    if os.path.exists(NUMBER_SAVE):
        with open(NUMBER_SAVE, "r") as f:
            return f.read()
    print("第一次运行, 即将安装测试插件, 若不需要测试插件, 稍后可以删除...")
    install("TestPlugin")
    return set_qq()
