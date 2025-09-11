from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry import command_registry
from ncatbot.core.event import BaseMessageEvent


@command_registry.command("status", aliases=["stat", "st"], description="查看状态")
async def external_status_cmd(event: BaseMessageEvent):
    await event.reply("机器人运行正常")


class CmdExternalPlugin(NcatBotPlugin):
    name = "CmdExternalPlugin"
    version = "1.0.0"

    async def on_load(self):
        pass


