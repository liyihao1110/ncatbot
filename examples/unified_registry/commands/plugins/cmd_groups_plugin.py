from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent


class CmdGroupsPlugin(NcatBotPlugin):
    name = "CmdGroupsPlugin"
    version = "1.0.0"

    async def on_load(self):
        pass

    # 顶层组：user
    user_group = command_registry.group("user", description="用户管理命令")

    @user_group.command("list", aliases=["ul"], description="列出所有用户")
    async def user_list_cmd(self, event: BaseMessageEvent):
        await event.reply("用户列表: user1, user2, user3")

    @user_group.command("info", aliases=["ui"], description="查看用户信息")
    async def user_info_cmd(self, event: BaseMessageEvent, user_id: str):
        await event.reply(f"用户 {user_id} 的信息")

    # 嵌套组：admin -> user
    admin_group = command_registry.group("admin", description="管理功能")
    user_admin = admin_group.group("user", description="用户管理")

    @user_admin.command("ban", aliases=["aub"], description="封禁用户")
    async def ban_user_cmd(self, event: BaseMessageEvent, user_id: str):
        await event.reply(f"已封禁用户: {user_id}")

    @user_admin.command("unban", aliases=["aun"], description="解封用户")
    async def unban_user_cmd(self, event: BaseMessageEvent, user_id: str):
        await event.reply(f"已解封用户: {user_id}")
