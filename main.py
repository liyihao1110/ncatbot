from ncatbot.core import BotClient, GroupMessage, PrivateMessage
from ncatbot.utils import config, get_log

_log = get_log()

config.set_bot_uin("123456")  # 设置 bot qq 号 (必填)
config.set_root("123456")  # 设置 bot 超级管理员账号 (建议填写)
config.set_ws_uri("ws://localhost:3001")  # 设置 napcat websocket server 地址
config.set_ws_token("")  # 设置 token (websocket 的 token)
config.set_webui_uri("http://localhost:6099")  # 设置 napcat webui 地址
config.set_webui_token("napcat")  # 设置 token (webui 的 token)

bot = BotClient()


@bot.group_event()
async def on_group_message(msg: GroupMessage):
    _log.info(msg)
    if msg.raw_message == "测试":
        await msg.reply(text="NcatBot 测试成功喵~")


@bot.private_event()
def on_private_message(msg: PrivateMessage):
    _log.info(msg)
    if msg.raw_message == "测试":
        bot.api.post_private_msg_sync(msg.user_id, text="NcatBot 测试成功喵~")


if __name__ == "__main__":
    bot.run()
