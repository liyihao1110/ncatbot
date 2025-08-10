from ..builtin_mixin import NcatBotPlugin
from ncatbot.core.event import BaseMessageEvent
from typing import List
import psutil
import ncatbot

class SystemManager(NcatBotPlugin):
    
    async def on_load(self) -> None:
        self.register_admin_command("ncatbot_status", self.get_status, aliases=["ncs"])
        self.register_admin_command("ncatbot_help", self.get_help, aliases=["nch"])

    async def get_status(self, event: BaseMessageEvent, args: List[str]) -> None:
        text = f"ncatbot 状态:\n"
        text += f"插件数量: {len(self.plugin_loader.plugins)}\n"
        text += f"插件列表: {', '.join([plugin.name for plugin in self.plugin_loader.plugins])}\n"
        text += f"CPU 使用率: {psutil.cpu_percent()}%\n"
        text += f"内存使用率: {psutil.virtual_memory().percent}%\n"
        text += f"NcatBot 版本: {ncatbot.__version__}\n"
        text += f"Star NcatBot Meow~: https://github.com/liyihao1110/ncatbot\n"
        await event.reply(text)

    async def get_help(self, event: BaseMessageEvent, args: List[str]) -> None:
        text = f"ncatbot 帮助:\n"
        text += f"/ncs 查看ncatbot状态\n"
        text += f"/nch 查看ncatbot帮助\n"
        text += f"开发中... 敬请期待\n"
        await event.reply(text)

    