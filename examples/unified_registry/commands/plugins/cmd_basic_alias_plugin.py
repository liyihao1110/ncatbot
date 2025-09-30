from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent


class CmdBasicAliasPlugin(NcatBotPlugin):
    name = "CmdBasicAliasPlugin"
    version = "1.0.0"

    async def on_load(self):
        pass

    @command_registry.command("hello")
    async def hello_cmd(self, event: BaseMessageEvent):
        await event.reply("Hello, World!")

    @command_registry.command("ping")
    async def ping_cmd(self, event: BaseMessageEvent):
        await event.reply("pong!")

    @command_registry.command("status", aliases=["stat", "st"], description="查看状态")
    async def status_cmd(self, event: BaseMessageEvent):
        await event.reply("机器人运行正常")
