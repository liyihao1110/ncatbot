from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import (
    filter_registry,
)
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent


# 自定义过滤器函数
@filter_registry.register("time_filter")
def time_filter(event: BaseMessageEvent) -> bool:
    import datetime

    current_hour = datetime.datetime.now().hour
    return 9 <= current_hour <= 22


@filter_registry.register("keyword_filter")
def keyword_filter(event: BaseMessageEvent) -> bool:
    raw = getattr(event, "raw_message", None) or ""
    return "机器人" in raw


class CustomFiltersPlugin(NcatBotPlugin):
    name = "CustomFiltersPlugin"
    version = "1.0.0"

    async def on_load(self):
        pass

    # 使用名称添加过滤器的命令
    @command_registry.command("vip")
    async def vip_command(self, event: BaseMessageEvent):
        await event.reply("VIP专属功能")

    # 启动后通过名称添加过滤器（模拟文档中的 add_filter_to_function）
    def add_filters(self):
        filter_registry.add_filter_to_function(self.vip_command, "time_filter")


# 额外的函数式过滤器注册示例
def bind_custom_filter_to_function(func):
    filter_registry.add_filter_to_function(func, "keyword_filter")
    return func
