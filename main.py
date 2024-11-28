# main.py
import asyncio

from Ncatbot.websockNB import core
from Ncatbot.message import GroupMessage,PrivateMessage
bot_websocket, bot_api = core(http_port=3000, ws_port=3001)
bot_client = bot_websocket.client

@bot_client.group_message(['text','face'])
# 处理群消息，可用监听的数据在这：https://napneko.github.io/develop/msg
async def group_message_handler(message: GroupMessage):
    print(message.message)

@bot_client.private_message(['text','face'])
async def private_message_handler(message: PrivateMessage):
    print(message)
    print(message.message)
    print(message.message.text)
    print(message.message.reply)
    if message.raw_message == '你好':
        await message.add_text('hi').reply()
"""
>>>terminal
...
[{'type': 'reply', 'data': {'id': '1704856505'}}, {'type': 'text', 'data': {'text': '你好'}}]
['你好']
['1704856505']
"""



@bot_client.request
async def request_handler(message):
    print(message)

@bot_client.notice
async def notice_handler(message):
    print(message)
# 启动 WebSocket 客户端
asyncio.run(bot_websocket.ws_run())