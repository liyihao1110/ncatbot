"""Utility functions and constants for NcatBot CLI."""

import os

try:
    from ncatbot.adapter.nc.install import install_napcat
    from ncatbot.core import BotClient
    from ncatbot.plugin import install_plugin_dependecies
    from ncatbot.scripts import get_pulgin_info_by_name as get_plugin_info_by_name
    from ncatbot.utils import PLUGIN_BROKEN_MARK, config, get_log, get_proxy_url
except ImportError:
    # For development without ncatbot installed
    print("警告: ncatbot 模块未安装，部分功能可能无法使用")
    install_napcat = lambda *args: None
    BotClient = object
    install_plugin_dependecies = lambda *args: None
    get_plugin_info_by_name = lambda *args: (True, "0.0.1")
    PLUGIN_BROKEN_MARK = "BROKEN"
    config = type("Config", (), {"set_bot_uin": lambda *args: None})()
    get_log = lambda *args: type("Logger", (), {"error": print})()
    get_proxy_url = lambda: "https://ghproxy.com"

# Constants
GITHUB_PROXY = get_proxy_url()
PYPI_SOURCE = "https://mirrors.aliyun.com/pypi/simple/"
NCATBOT_PATH = "ncatbot"
TEST_PLUGIN = "TestPlugin"
NUMBER_SAVE = "number.txt"
PLUGIN_DOWNLOAD_REPO = (
    "https://raw.githubusercontent.com/ncatbot/NcatBot-Plugins/refs/heads/main/plugins"
)

# Initialize logger
LOG = get_log("CLI")


def get_qq() -> str:
    """Get the QQ number from the saved file."""
    from .plugin_commands import install
    from .system_commands import set_qq

    if os.path.exists(NUMBER_SAVE):
        with open(NUMBER_SAVE, "r") as f:
            return f.read()
    print("第一次运行, 即将安装测试插件, 若不需要测试插件, 稍后可以删除...")
    install("TestPlugin")
    return set_qq()
