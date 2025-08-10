from ..builtin_mixin import NcatBotPlugin
from ncatbot.core.event import BaseMessageEvent
from typing import List
import psutil
import ncatbot
from ncatbot.utils import get_log

LOG = get_log("SystemManager")

class SystemManager(NcatBotPlugin):
    version = "4.0.0"
    name = "SystemManager"
    author = "huan-yp"
    description = "ncatbot 系统管理插件"

    async def on_load(self) -> None:
        LOG.debug("SystemManager 加载")
        # self.register_user_func("ncs", self.get_status, prefix="/ncs")
        # self.register_user_func("nch", self.get_help, prefix="/nch")
        self.register_admin_command("ncatbot_status", self.get_status, aliases=["ncs"])
        self.register_admin_command("ncatbot_help", self.get_help, aliases=["nch"])

    async def get_status(self, event: BaseMessageEvent, *args) -> None:
        text = f"ncatbot 状态:\n"
        text += f"插件数量: {len(self._loader.plugins)}\n"
        text += f"插件列表: {', '.join([plugin.name for plugin in self._loader.plugins.values()])}\n"
        text += f"CPU 使用率: {psutil.cpu_percent()}%\n"
        text += f"内存使用率: {psutil.virtual_memory().percent}%\n"
        text += f"NcatBot 版本: {ncatbot.__version__}\n"
        text += f"Star NcatBot Meow~: https://github.com/liyihao1110/ncatbot\n"
        await event.reply(text)

    async def get_help(self, event: BaseMessageEvent, *args) -> None:
        text = f"ncatbot 帮助:\n"
        text += f"/ncs 查看ncatbot状态\n"
        text += f"/nch 查看ncatbot帮助\n"
        text += f"开发中... 敬请期待\n"
        await event.reply(text)

    