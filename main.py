import asyncio
from ncatbot.Logger import get_logger
from ncatbot.client import BotClient
from ncatbot.message import GroupMessage,PrivateMessage
from ncatbot.Plugin_system import AsyncPluginLoader, EventBus

bot = BotClient()
_LOG = get_logger("Main")

async def main(reload=True):
    # 创建事件总线实例
    event_bus = EventBus()

    # 创建异步插件加载器并加载插件
    async_plugin_loader = AsyncPluginLoader('plugins', event_bus)
    await async_plugin_loader.load_plugins()

    @bot.group_event
    async def on_group_message(msg:GroupMessage):
        await event_bus.publish('group_message', GroupMessage = msg)
        await event_bus.publish('all_message', GroupMessage = msg, PrivateMessage = None)
        _LOG.info(f"Bot.{msg.self_id}: [{(await msg.get_group_info(msg.group_id))['group_name']}({msg.group_id})] {msg.sender.nickname}({msg.user_id}) -> {msg.raw_message}")

    @bot.private_event
    async def on_private_message(msg:PrivateMessage):
        await event_bus.publish('private_message', PrivateMessage = msg)
        await event_bus.publish('all_message', GroupMessage = None, PrivateMessage = msg)
        _LOG.info(f"Bot.{msg.self_id}: [{msg.sender.nickname}({msg.user_id})] -> {msg.raw_message}")

    @bot.notice_event
    async def on_notice(msg):
        await event_bus.publish('nonotice_eventtice', msg)
        _LOG.info(msg)

    @bot.request_event
    async def on_request(msg):
        await event_bus.publish('request_event', msg)

    bot.run(reload=reload)

asyncio.run(main(reload=True))