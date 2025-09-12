from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent


@command_registry.command("status", aliases=["stat", "st"], description="查看状态")
async def external_status_cmd(event: BaseMessageEvent):
    await event.reply("机器人运行正常")


class CmdExternalPlugin(NcatBotPlugin):
    name = "CmdExternalPlugin"
    version = "1.0.0"

    async def on_load(self):
        pass

my_registry = command_registry.get_registry(prefixes=["", "!"]) # 无前缀触发或者 ! 触发
my_group = my_registry.group("my_group", description="无前缀组")

@my_registry.command("non_prefix_hello")
async def non_prefix_hello_cmd(event: BaseMessageEvent):
    await event.reply("Hello, World!")

@my_group.command("my_group_hello")
async def my_group_hello_cmd(event: BaseMessageEvent):
    await event.reply("Hello, Group World!")