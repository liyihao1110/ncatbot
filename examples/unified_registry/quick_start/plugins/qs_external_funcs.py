from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.plugin_system import admin_filter
from ncatbot.core.event import BaseMessageEvent


@command_registry.command("outside")
async def outside_command(event: BaseMessageEvent):
    await event.reply("这是在插件类外定义的命令")


@admin_filter
@command_registry.command("external_admin")
async def external_admin_cmd(event: BaseMessageEvent, action: str):
    await event.reply(f"执行管理员操作: {action}")


class QSExternalFuncsPlugin(NcatBotPlugin):
    name = "QSExternalFuncsPlugin"
    version = "1.0.0"
    author = "doc-verify"
    description = "快速开始-额外示例：普通函数注册"

    async def on_load(self):
        pass

    @command_registry.command("inside")
    async def inside_cmd(self, event: BaseMessageEvent):
        await event.reply("这是类内的命令")


