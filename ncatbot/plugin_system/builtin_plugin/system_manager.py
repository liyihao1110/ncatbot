from ..builtin_mixin import NcatBotPlugin
from .unified_registry import command_registry, filter_registry, admin_only, root_only
from .unified_registry.command_system.registry import option_group
from ncatbot.core.event import BaseMessageEvent, At
from typing import List
import psutil
import ncatbot
from ncatbot.utils import get_log, PermissionGroup

LOG = get_log("SystemManager")

class SystemManager(NcatBotPlugin):
    version = "4.0.0"
    name = "SystemManager"
    author = "huan-yp"
    description = "ncatbot 系统管理插件"

    async def on_load(self) -> None:
        pass

    @command_registry.command("ncatbot_status", aliases=["ncs"])
    @admin_only
    async def get_status(self, event: BaseMessageEvent) -> None:
        text = f"ncatbot 状态:\n"
        text += f"插件数量: {len(self._loader.plugins)}\n"
        text += f"插件列表: {', '.join([plugin.name for plugin in self._loader.plugins.values()])}\n"
        text += f"CPU 使用率: {psutil.cpu_percent()}%\n"
        text += f"内存使用率: {psutil.virtual_memory().percent}%\n"
        text += f"NcatBot 版本: {ncatbot.__version__}\n"
        text += f"Star NcatBot Meow~: https://github.com/liyihao1110/ncatbot\n"
        await event.reply(text)

    @command_registry.command("ncatbot_help", aliases=["nch"])
    async def get_help(self, event: BaseMessageEvent) -> None:
        text = f"ncatbot 帮助:\n"
        text += f"/ncs 查看ncatbot状态\n"
        text += f"/nch 查看ncatbot帮助\n"
        text += f"开发中... 敬请期待\n"
        await event.reply(text)

    @command_registry.command("set_admin", aliases=["sa"])
    @option_group(choices=["add", "remove"], name="set", default="add", help="设置管理员")
    @root_only
    async def set_admin(self, event: BaseMessageEvent, user_id: str, set: str = "add") -> None:
        if user_id.startswith('At'):
            user_id = user_id.split('=')[1].split('"')[1]
        
        if set == "add":
            self.rbac_manager.assign_role_to_user(user_id, PermissionGroup.ADMIN.value)
            await event.reply(f"添加管理员 {user_id}", at=False)
        elif set == "remove":
            self.rbac_manager.unassign_role_to_user(user_id, PermissionGroup.ADMIN.value)
            await event.reply(f"删除管理员 {user_id}", at=False)
