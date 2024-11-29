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
    # 媒体文件base64支持
    if message.raw_message == 'base64':
        await message.add_image('base64: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').reply(reply=True)
    # 合并转发上条消息
    if 'node' in message.raw_message:
        await message.node(id_=message.message_id).reply(reply=True)
    # 推荐自身
    if message.raw_message == 'me':
        await message.contact(qq=message.sender.user_id).reply(reply=True)
    # 自动贴表情包
    f = message.message.face
    if f:
        await message.set_msg_emoji_like(message_id=message.message_id, emoji_id=f.id)
    # 重复发图片
    i = message.message.image
    if i:
        await message.add_image(i.url).reply(reply=True)
    if '第二个表情包' in message.raw_message:
        bqb = await message.fetch_custom_face(count=2)
        if bqb['data']:
            await message.add_image(bqb['data'][-1]).reply(reply=True)
        await message.add_text('穷的连一个表情包都没有！').reply(reply=True)
    if '发送一堆小表情' in message.raw_message:
        message.add_text('小表情来喽，接好！\n')
        for f in dir(face):
            if not f.startswith('__'):
                message.add_face(getattr(face, f))
        await message.reply(reply=True)


@bot_client.private_message(['text','face'])
async def private_message_handler(message: PrivateMessage):
    print(message)
    print(message.message)
    print(message.message.text)
    print(message.message.reply)
    if message.raw_message == '你好':
        await message.add_text('hi').reply(reply=True)
    elif message.raw_message == 'md':
        await message.add_markdown('##你好啊\n<b>测试</b>').reply(reply=True)
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
            await message.add_text('\n'.join(t['text'] for t in text['data'])).reply(reply=True)


@bot_client.request
async def request_handler(message):
    print(message)

@bot_client.notice
async def notice_handler(message):
    print(message)
# 启动 WebSocket 客户端
asyncio.run(bot_websocket.ws_run())
