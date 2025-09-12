from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.plugin_system import group_only, private_only, admin_only, root_only, on_message
from ncatbot.core.event import BaseMessageEvent


class BuiltinFiltersPlugin(NcatBotPlugin):
    name = "BuiltinFiltersPlugin"
    version = "1.0.0"
    author = "doc-verify"

    async def on_load(self):
        pass

    def _is_command(self, event: BaseMessageEvent) -> bool:
        raw = getattr(event, "raw_message", None) or ""
        return isinstance(raw, str) and (raw.startswith("/") or raw.startswith("!"))

    # group_only
    @group_only
    async def group_message(self, event: BaseMessageEvent):
        if self._is_command(event):
            return
        await event.reply("收到一条群聊消息")

    # private_only
    @private_only
    async def private_message(self, event: BaseMessageEvent):
        if self._is_command(event):
            return
        await event.reply("收到一条私聊消息")

    # admin_only 命令
    @admin_only
    @command_registry.command("ban")
    async def ban_command(self, event: BaseMessageEvent, user_id: str):
        await event.reply(f"已封禁用户: {user_id}")

    # admin_only 纯过滤函数
    @admin_only
    async def admin_message(self, event: BaseMessageEvent):
        if self._is_command(event):
            return
        await event.reply("收到一条管理员消息")

    # root_only 命令
    @root_only
    @command_registry.command("shutdown")
    async def shutdown_command(self, event: BaseMessageEvent):
        await event.reply("正在关闭机器人...")



