
from ncatbot.client import BotClient
from ncatbot.message import GroupMessage,PrivateMessage

bot = BotClient()

@bot.group_event
async def on_group_message(msg:GroupMessage):
    print(msg)

@bot.private_event
async def on_private_message(msg:PrivateMessage):
    print(msg)

@bot.notice_event
async def on_notice(msg):
    print(msg)

@bot.request_event
async def on_request(msg):
    print(msg)

bot.run(reload=True)