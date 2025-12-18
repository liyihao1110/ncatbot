from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.plugin_system import (
    admin_group_filter,
    admin_private_filter,
    group_filter,
    admin_filter,
)
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import (
    filter_registry,
)
from ncatbot.core.event import BaseMessageEvent


class ComboFiltersPlugin(NcatBotPlugin):
    name = "ComboFiltersPlugin"
    version = "1.0.0"

    async def on_load(self):
        pass

    def _is_command(self, event: BaseMessageEvent) -> bool:
        raw = getattr(event, "raw_message", None) or ""
        return isinstance(raw, str) and (raw.startswith("/") or raw.startswith("!"))

    # 组合装饰器：管理员 + 群聊
    @admin_group_filter
    @command_registry.command("grouppromote")
    async def group_promote_command(self, event: BaseMessageEvent, user_id: str):
        await event.reply(f"在群聊中提升用户权限: {user_id}")

    # 组合装饰器：管理员 + 私聊
    @admin_private_filter
    @command_registry.command("adminpanel")
    async def admin_panel_command(self, event: BaseMessageEvent):
        await event.reply("管理员私聊面板")

    # 手动组合多个过滤器（演示顺序无特殊输出，这里只要通过即可）
    @admin_filter
    @group_filter
    async def group_admin_message(self, event: BaseMessageEvent):
        if self._is_command(event):
            return
        await event.reply("收到一条管理员发送的群聊消息")

    # 一次性注册多个过滤器
    @filter_registry.filters("admin_filter", "group_filter")
    @command_registry.command("order")
    async def order_command(self, event: BaseMessageEvent):
        await event.reply("多重过滤器命令")
