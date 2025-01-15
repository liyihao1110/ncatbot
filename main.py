# encoding: utf-8

import ncatpy
from ncatpy import logging
from ncatpy.message import GroupMessage,PrivateMessage

_log = logging.get_logger()

class MyClient(ncatpy.Client):
    async def on_group_message(self, message: GroupMessage):
        _log.info(message)

    async def on_private_message(self, message: PrivateMessage):
        _log.info(message)

if __name__ == "__main__":
    # 1. 通过预设置的类型，设置需要监听的事件通道
    # intents = ncatpy.Intents.public() # 可以订阅public，包括了私聊和群聊

    # 2. 通过kwargs，设置需要监听的事件通道
    intents = ncatpy.Intents(group_event=True)
    client = MyClient(intents=intents)
    client.run()
