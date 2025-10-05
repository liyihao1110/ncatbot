from ncatbot.core import BotClient, GroupMessage, PrivateMessage
from ncatbot.utils import config, get_log

_log = get_log()

# Bot 账号
config.set_bot_uin("123456789")

# Root 账号
config.set_root("123456789")

# WS Server Address
config.set_ws_uri("ws://localhost:3001")

# WS Server Token
config.set_ws_token("")

# WebUI Address
config.set_webui_uri("http://localhost:6099")

# WebUI Token
config.set_webui_token("napcat")

bot = BotClient()

@bot.group_event()
async def on_group_msg(group_msg: GroupMessage):
    _log.info(group_msg)
    if group_msg.raw_message == "test":
        await group_msg.reply("Ncatbot Group Msg Test Success")
        
    if group_msg.raw_message == "test a":
        await bot.api.post_all_group_msg(bot_client = bot, text = "Everybody good evening, This is a test group msg")


@bot.private_event()
def on_private_msg(priv_msg: PrivateMessage):
    _log.info(priv_msg)
    if priv_msg.raw_message == "test":
        bot.api.post_private_msg_sync(priv_msg.user_id, "Ncatbot Private Msg Test Success")

if __name__ == "__main__":
    bot.run()