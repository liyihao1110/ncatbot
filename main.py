# encoding: utf-8

import ncatpy
from ncatpy import logging
from ncatpy.message import GroupMessage,PrivateMessage

_log = logging.get_logger()

class MyClient(ncatpy.Client):
    async def on_group_message(self, message: GroupMessage):
        _log.info(f"收到群消息，ID: {message.message.text.text}")
        _log.info(message.user_id)
        if message.user_id == 2793415370:
            # 当提问者的QQ号是2793415370时，调用XunfeiGPT插件回答他的问题
            # t = await self._XunfeiGPT.ai_response(input=message.message.text.text, group_id=message.group_id) # 单轮ai聊天
            t = await self._XunfeiGPT.ai_response_history(input=message.message.text.text, info= True, group_id=message.group_id)# 多轮ai聊天,可用参数：开发者模式：info=True,历史记录次数：history_num=5
            _log.info(t)
        if message.message.text.text == "你好":
            # 通过http发送消息
            t = await message.add_text("你好,o").reply()
            _log.info(t)


    async def on_private_message(self, message: PrivateMessage):
        _log.info(f"收到私聊消息，ID: {message.message.text.text}")
        if message.message.text.text == "你好":
            t = await self._api.send_msg(user_id=message.user_id, text="你好,o")
            _log.info(t)

if __name__ == "__main__":
    # 1. 通过预设置的类型，设置需要监听的事件通道
    # intents = ncatpy.Intents.public() # 可以订阅public，包括了私聊和群聊

    # 2. 通过kwargs，设置需要监听的事件通道
    intents = ncatpy.Intents(group_event=True)
    client = MyClient(intents=intents, plugins=["XunfeiGPT"])# 如果没有插件，则不需要添加plugins=["XunfeiGPT"]
    client.run()
