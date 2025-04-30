"""Utility functions and constants for NcatBot CLI."""

import os

from ncatbot.plugin import PluginLoader
from ncatbot.utils import PLUGINS_DIR, get_log

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


def get_plugin_info(path: str):
    if os.path.exists(path):
        return PluginLoader(None).get_plugin_info(path)
    else:
        raise FileNotFoundError(f"dir not found: {path}")


def get_plugin_info_by_name(name: str):
    """
    Args:
        name (str): 插件名
    Returns:
        Tuple[bool, str]: 是否存在插件, 插件版本
    """
    plugin_path = os.path.join(PLUGINS_DIR, name)
    if os.path.exists(plugin_path):
        return True, get_plugin_info(plugin_path)[1]
    else:
        return False, "0.0.0"
