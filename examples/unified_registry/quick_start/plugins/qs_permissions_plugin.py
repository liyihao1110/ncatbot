from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.plugin_system import group_filter, private_filter, admin_filter
from ncatbot.core.event import BaseMessageEvent


class QSPermissionsPlugin(NcatBotPlugin):
    name = "QSPermissionsPlugin"
    version = "1.0.0"
    author = "doc-verify"
    description = "快速开始-权限控制示例"

    async def on_load(self):
        pass

    # 仅群聊可用
    @group_filter
    @command_registry.command("groupinfo")
    async def group_info_cmd(self, event: BaseMessageEvent):
        await event.reply(f"当前群聊ID: {event.group_id}")

    # 仅私聊可用
    @private_filter
    @command_registry.command("private")
    async def private_cmd(self, event: BaseMessageEvent):
        await event.reply("这是一个私聊命令")

    # 仅 Bot 管理员可用
    @admin_filter
    @command_registry.command("admin")
    async def admin_cmd(self, event: BaseMessageEvent):
        await event.reply("你是管理员！")
