from ncatbot.client import BotClient
from ncatbot.config import config
from ncatbot.logger import get_log
from ncatbot.message import GroupMessage, PrivateMessage

_log = get_log()

config.set_bot_uin("123456")  # 设置 bot qq 号
config.set_ws_uri("ws://localhost:3001")  # 设置 napcat websocket server 地址

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
    bot.run(reload=False)
