from ncatbot.core.client import BotClient
from ncatbot.core.message import GroupMessage, PrivateMessage
from ncatbot.utils.config import config
from ncatbot.utils.logger import get_log

_log = get_log()

config.set_bot_uin("1550507358")  # 设置 bot qq 号
config.set_ws_uri("ws://62.234.222.17:3001")  # 设置 napcat websocket server 地址
config.set_token("2006")

bot = BotClient()


@bot.group_event()
async def on_group_message(msg: GroupMessage):
    _log.info(msg)


@bot.private_event()
async def on_private_message(msg: PrivateMessage):
    _log.info(msg)
    if msg.raw_message == "测试":
        await bot.api.post_private_msg(msg.user_id, text="NcatBot 测试成功喵~")


if __name__ == "__main__":
    bot.run(reload=True)
