# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-21 18:23:06
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-02-21 19:43:52
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @message: 喵喵喵?
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
from ncatbot.plugin.base_plugin import BasePlugin
from ncatbot.plugin.event import (
    Conf,
    Event,
    EventBus,
    Func,
    get_global_access_controller,
)
from ncatbot.plugin.loader import (
    CompatibleEnrollment,
    PluginLoader,
    install_plugin_dependecies,
)
from ncatbot.plugin.RBACManager import RBACManager

__all__ = [
    "BasePlugin",
    "EventBus",
    "Event",
    "Func",
    "Conf",
    "get_global_access_controller",
    "CompatibleEnrollment",
    "PluginLoader",
    "install_plugin_dependecies",
    "RBACManager",
]
