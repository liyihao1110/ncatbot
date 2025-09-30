from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent
from ncatbot.core.event.message_segment import Image, At


class ParamsMediaPlugin(NcatBotPlugin):
    name = "ParamsMediaPlugin"
    version = "1.0.0"

    async def on_load(self):
        pass

    @command_registry.command("analyze")
    async def analyze_cmd(
        self, event: BaseMessageEvent, description: str, image: Image
    ):
        await event.reply(f"分析图片: {description}\n图片信息: {image.file}")

    @command_registry.command("mention")
    async def mention_cmd(self, event: BaseMessageEvent, message: str, user: At):
        await event.reply(f"发送消息给 @{user.qq}: {message}")
