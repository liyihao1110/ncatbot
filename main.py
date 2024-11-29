# main.py
import asyncio

from Ncatbot.api import face
from Ncatbot.websockNB import core
from Ncatbot.message import GroupMessage,PrivateMessage

bot_websocket, bot_api = core(http_port=3000, ws_port=3001)
bot_client = bot_websocket.client


@bot_client.group_message(['text','face', 'image'])
# 处理群消息，可用监听的数据在这：https://napneko.github.io/develop/msg
async def group_message_handler(message: GroupMessage):
    # 自动贴表情包
    f = message.message.face
    if f:
        await message.set_msg_emoji_like(message_id=message.message_id, emoji_id=f.id)
    # 重复发图片
    i = message.message.image
    if i:
        await message.add_image(i.url).reply()
    if '第二个表情包' in message.raw_message:
        bqb = await message.fetch_custom_face(count=2)
        if bqb['data']:
            await message.add_image(bqb['data'][-1]).reply()
        await message.add_text('穷的连一个表情包都没有！').reply()
    if '发送一堆小表情' in message.raw_message:
        message.add_text('小表情来喽，接好！\n')
        for f in dir(face):
            if not f.startswith('__'):
                message.add_face(getattr(face, f))
        await message.reply()


@bot_client.private_message(['text','face'])
async def private_message_handler(message: PrivateMessage):
    print(message)
    print(message.message)
    print(message.message.text)
    print(message.message.reply)
    if message.raw_message == '你好':
        await message.add_text('hi').reply()
    elif message.raw_message == 'md':
        await message.add_markdown('##你好啊\n<b>测试</b>').reply()
"""
>>>terminal
...
[{'type': 'reply', 'data': {'id': '1704856505'}}, {'type': 'text', 'data': {'text': '你好'}}]
['你好']
['1704856505']
"""


@bot_client.private_message(['image'])
async def private_message_handler(message: PrivateMessage):
    # 自动OCR图片
    for msg in message.message.message:
        if msg['type'] == 'image':
            text = await message.ocr_image(msg['data']['url'])
            await message.add_text('\n'.join(t['text'] for t in text['data'])).reply()


@bot_client.request
async def request_handler(message):
    print(message)

@bot_client.notice
async def notice_handler(message):
    print(message)
# 启动 WebSocket 客户端
asyncio.run(bot_websocket.ws_run())
