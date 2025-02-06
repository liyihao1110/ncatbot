from ncatbot.client import BotClient
from ncatbot.logger import get_log
from ncatbot.message import GroupMessage, PrivateMessage
from plugin_manager import PluginManager

_log = get_log()
bot = BotClient()
plugin_manager = PluginManager(plugin_dir="plugins")

# 加载所有插件
plugin_manager.load_plugins()


@bot.group_event()
async def on_group_message(msg: GroupMessage):
    await plugin_manager.handle_group_message(msg)


@bot.private_event()
async def on_private_message(msg: PrivateMessage):
    _log.info(f"收到私聊消息: {msg.raw_message}")
    await plugin_manager.handle_private_message(msg)


@bot.notice_event
async def on_notice(msg):
    await plugin_manager.handle_notice(msg)


@bot.request_event
async def on_request(msg):
    await plugin_manager.handle_request(msg)


if __name__ == "__main__":
    bot.run(reload=True)
