#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "木子"
import asyncio

from Ncatbot.websockNB import core
from Ncatbot.message import GroupMessage

bot_websocket, bot_api = core(http_port=3000, ws_port=3001)
bot = bot_websocket.client

# 处理群消息，可用监听的数据在这：https://napneko.github.io/develop/msg
@bot.group_message(['face','text','image'])
async def group_message_handler(message: GroupMessage):
    # 打印text数据
    if message.message.text:
        print(message.message.text.text)
    # 打印face数据
    if message.message.face:
        print(message.message.face.id)
    # 打印image数据
    if message.message.image:
        print(message.message.image.url)

# 启动 WebSocket 客户端..
asyncio.run(bot_websocket.ws_run())