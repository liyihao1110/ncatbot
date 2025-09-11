from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.decorators import group_only
from ncatbot.core.event import BaseMessageEvent


class QSPureFilterPlugin(NcatBotPlugin):
    name = "QSPureFilterPlugin"
    version = "1.0.0"
    author = "doc-verify"
    description = "快速开始-纯过滤器功能"

    async def on_load(self):
        pass

    def _is_command(self, event: BaseMessageEvent) -> bool:
        raw = getattr(event, "raw_message", None) or ""
        return isinstance(raw, str) and (raw.startswith("/") or raw.startswith("!"))

    # 非命令，仅过滤器
    @group_only
    async def on_group_message(self, event: BaseMessageEvent):
        if self._is_command(event):
            return
        await event.reply("收到一条群聊消息")


