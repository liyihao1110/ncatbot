from ncatbot.core.client import BotClient
from ncatbot.core.message import GroupMessage, PrivateMessage
from ncatbot.utils.config import config
from ncatbot.utils.logger import get_log

_log = get_log()

config.set_bot_uin("2954796277")  # 设置 bot qq 号
config.set_ws_uri("ws://localhost:7211")  # 设置 napcat websocket server 地址
config.set_token("YuanShenQidong123")

bot = BotClient()


# @bot.group_event()
# async def on_group_message(msg: GroupMessage):
#     _log.info(msg)


@bot.private_event()
async def on_private_message(msg: PrivateMessage):
    _log.info(msg)
    if msg.raw_message == "1":
        await bot.api.post_private_msg(msg.user_id, image="test.jpg")


if __name__ == "__main__":
    bot.run(reload=False)
