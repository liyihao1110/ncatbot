from ncatbot.client import BotClient
from ncatbot.config import config
from ncatbot.logger import get_log
from ncatbot.message import GroupMessage, PrivateMessage

from ncatbot.plugins_sys import PluginLoader, Event
import os, asyncio

_log = get_log()

config.set_bot_uin("123456")  # 设置 bot qq 号
config.set_ws_uri("ws://localhost:3001")  # 设置 napcat websocket server 地址

bot = BotClient()
loader = PluginLoader()


@bot.group_event()
async def on_group_message(msg: GroupMessage):
    _log.info(msg)
    await loader.event_bus.publish_sync(Event('ncatbot.group_event', msg))


@bot.private_event()
async def on_private_message(msg: PrivateMessage):
    _log.info(msg)
    await loader.event_bus.publish_sync(Event('ncatbot.private_message', msg))


async def main():
    await loader.load_plugin('plugins')
    _log.info('插件列表: ', *list(loader.plugins.keys()), sep='\n')

    # 发布事件
    # await loader.event_bus.publish_sync(Event('ncatbot.group_event',{'test','hi'}))

    # 关闭插件
    # for plugin_name in list(loader.plugins.keys()).copy():
    #     await loader.unload_plugin(plugin_name)

    bot.run(reload=True)

if __name__ == "__main__":
    asyncio.run(main())