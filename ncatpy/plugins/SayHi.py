# encoding=utf-8
'''仅供参考'''
from ..wsapi import WsApi

class SayHi:
    def __init__(self):
        self.wsapi = WsApi()

    async def SayHi(self, **kwargs):
        r = 'Hi'
        return await self.wsapi.send_msg(text=r, **kwargs)