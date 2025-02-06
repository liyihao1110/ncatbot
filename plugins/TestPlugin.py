from ncatbot.message import GroupMessage, PrivateMessage
from ncatbot.client import BotClient
from ncatbot.logger import get_log
from ncatbot.plugins_base import PluginBase

_log = get_log()
bot = BotClient()

class TestPlugin(PluginBase):
    async def on_group_message(self, msg: GroupMessage):
        _log.info(f"Test Plugin: Received Group Message: {msg}")

    async def on_private_message(self, msg: PrivateMessage):
        _log.info(f"Test Plugin: Received Private Message: {msg}")
        if msg.raw_message == "ping":
            await bot.api.add_at(msg.user_id).add_face(1).add_text("你好").add_face(2).send_private_msg(msg.user_id, reply=msg.message_id)

    async def on_notice(self, msg):
        _log.info(f"Test Plugin: Received Notice: {msg}")

    async def on_request(self, msg):
        _log.info(f"Test Plugin: Received Request: {msg}")
