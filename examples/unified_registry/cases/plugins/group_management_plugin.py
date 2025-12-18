from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.plugin_system import option, param
from ncatbot.plugin_system import group_filter, admin_filter
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils import get_log


LOG = get_log(__name__)


class GroupManagementPlugin(NcatBotPlugin):
    name = "GroupManagementPlugin"
    version = "1.0.0"
    description = "群聊管理功能"

    async def on_load(self):
        self.muted_users = set()
        self.group_settings = {"g1": {"mute_users": set(), "settings": {}}}

    @group_filter
    @admin_filter
    @command_registry.command("mute", description="禁言用户")
    @param(name="duration", default=60, help="禁言时长（秒）")
    async def mute_cmd(self, event: BaseMessageEvent, user_id: str, duration: int = 60):
        if duration < 1 or duration > 86400:
            await event.reply("❌ 禁言时长必须在1秒到24小时之间")
            return
        self.muted_users.add(user_id)
        LOG.info(f"管理员 {event.user_id} 禁言用户 {user_id} {duration}秒")
        await event.reply(f"🔇 已禁言用户 {user_id}，时长 {duration} 秒")

    @group_filter
    @admin_filter
    @command_registry.command("unmute", description="解除禁言")
    async def unmute_cmd(self, event: BaseMessageEvent, user_id: str):
        if user_id in self.muted_users:
            self.muted_users.remove(user_id)
            LOG.info(f"管理员 {event.user_id} 解除用户 {user_id} 禁言")
            await event.reply(f"🔊 已解除用户 {user_id} 的禁言")
        else:
            await event.reply("❌ 该用户未被禁言")

    @group_filter
    @admin_filter
    @command_registry.command("kick", description="踢出用户")
    @option(short_name="b", long_name="ban", help="同时拉黑用户")
    async def kick_cmd(self, event: BaseMessageEvent, user_id: str, ban: bool = False):
        action = "踢出并拉黑" if ban else "踢出"
        LOG.info(f"管理员 {event.user_id} {action}用户 {user_id}")
        await event.reply(f"👢 已{action}用户 {user_id}")

    @group_filter
    @command_registry.command("group_info", description="查看群信息")
    async def group_info_cmd(self, event: BaseMessageEvent):
        group_id = event.group_id
        settings = self.group_settings.get(group_id, {})
        info = f"📊 群信息 (ID: {group_id})\n"
        info += f"🔇 禁言用户数: {len(self.muted_users)}\n"
        info += f"⚙️ 特殊设置: {len(settings)} 项"
        await event.reply(info)
