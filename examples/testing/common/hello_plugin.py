"""
HelloPlugin - 用于测试文档验证的简单插件
"""
from ncatbot.plugin_system.builtin_mixin.ncatbot_plugin import NcatBotPlugin
from ncatbot.core.event import BaseMessageEvent
from ncatbot.plugin_system import command_registry, param, option


class HelloPlugin(NcatBotPlugin):
    """用于演示的简单插件"""
    name = "HelloPlugin"
    version = "1.0.0"
    description = "用于演示测试的简单插件"
        
    async def on_load(self):
        pass

    @command_registry.command("hello", aliases=["hi"], description="问候")
    async def hello_command(self, event: BaseMessageEvent):
        await event.reply("你好！这是来自 HelloPlugin 的问候。")

    @command_registry.command("echo", description="回显文本")
    @param(name="lang", default="zh", help="语言", choices=["zh","en"])
    @option(short_name="v", long_name="verbose", help="详细输出")
    async def echo_command(self, event: BaseMessageEvent, text: str, lang: str = "zh", verbose: bool = False):
        await event.reply(f"[{lang}] 你说的是：{text}" + (" (verbose)" if verbose else ""))
