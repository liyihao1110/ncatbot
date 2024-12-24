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
            t = await self._XunfeiGPT.ai_response(input=message.message.text.text, group_id = message.group_id)
            _log.info(t)
        if message.message.text.text == "你好":
            t = await message.add_text("你好,o").reply()

    async def on_private_message(self, message: PrivateMessage):
        _log.info(f"收到私聊消息，ID: {message.message.text.text}")
        if message.message.text.text == "你好":
            t = await self._api.send_msg(user_id=message.user_id, text="你好,o")
            _log.info(t)

if __name__ == "__main__":
    intents = ncatpy.Intents.public()
    client = MyClient(intents=intents, plugins=["XunfeiGPT"])# 如果没有插件，则不需要添加plugins=["XunfeiGPT"]
    client.run()# 只支持本地端口<-目前
