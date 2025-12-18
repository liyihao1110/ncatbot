# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-03-21 18:06:59
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-08-04 14:24:40
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
from .base_plugin import BasePlugin
from .event import NcatBotEvent, EventBus
from .loader import PluginLoader
from .builtin_mixin import NcatBotPlugin
from .builtin_plugin.unified_registry import filter_registry, command_registry
from .decorator import CompatibleHandler
from .builtin_plugin.unified_registry import (
    on_message,
    on_message_sent,
    option,
    param,
    option_group,
    admin_only,
    root_only,
    private_only,
    group_only,
    on_request,
    on_notice,
    on_group_at,
    on_group_poke,
    on_group_increase,
    on_group_decrease,
    on_group_request,
)
from .builtin_plugin.unified_registry import (
    admin_filter,
    group_admin_filter,
    group_owner_filter,
    root_filter,
    private_filter,
    group_filter,
    admin_private_filter,
    admin_group_filter,
)

__all__ = [
    "BasePlugin",
    "NcatBotEvent",
    "EventBus",
    "PluginLoader",
    "NcatBotPlugin",
    "CompatibleHandler",
    "filter_registry",
    "command_registry",
    "on_message",
    "on_message_sent",
    "option",
    "param",
    "option_group",
    "on_request",
    "on_notice",
    "on_group_at",
    "on_group_increase",
    "on_group_decrease",
    "on_group_poke",
    "on_group_request",
    "admin_only",
    "root_only",
    "private_only",
    "group_only",
    "admin_filter",
    "group_admin_filter",
    "group_owner_filter",
    "root_filter",
    "private_filter",
    "group_filter",
    "admin_group_filter",
    "admin_private_filter",
]
