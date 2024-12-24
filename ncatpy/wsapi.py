# encoding: utf-8

import websockets
import json
from .types import message

from .setting import SetConfig

class BotWs:
    def __init__(self):
        self.ws_url = SetConfig().ws_url
    async def post(self, data):
        async with websockets.connect(self.ws_url + "/api") as websocket:
            await websocket.send(data)
            return await websocket.recv()

class WsApi:
    def __init__(self):
        self._ws = BotWs()

    async def send_msg(self, group_id=None, user_id=None, **kwargs):
        if len(kwargs) != 1:
            raise ValueError("[ncatpy] kwargs can only have one parameter")
        if group_id:
            payload = locals()
            del payload['user_id'], payload['self']
            return await self._ws.post(json.dumps(message.create_group_message(payload)))
            
        elif user_id:
            payload = locals()
            del payload['group_id'], payload['self']
            return await self._ws.post(json.dumps(message.create_private_message(payload)))

        else:
            raise ValueError("[ncatpy] group_id or user_id must be set")

    async def reply(self, message_id, group_id=None, user_id=None, **kwargs):
        if len(kwargs) != 1:
            raise ValueError("[ncatpy] kwargs can only have one parameter")
        if group_id:
            payload = locals()
            del payload['user_id'], payload['self']
            payload = message.create_group_message(payload)
            payload['params']['message'].insert(0, {"type":"reply", "data":{"id":message_id}})
            return await self._ws.post(json.dumps(payload))
        elif user_id:
            payload = locals()
            del payload['group_id'], payload['self']
            payload = message.create_private_message(payload)
            payload['params']['message'].insert(0, {"type":"reply", "data":{"id":message_id}})
            return await self._ws.post(json.dumps(payload))
        else:
            raise ValueError("[ncatpy] group_id or user_id must be set")

    async def at(self, qq_uin, group_id, **kwargs):
        payload = locals()
        del payload['self']
        payload = message.create_group_message(payload)
        payload['params']['message'].insert(0, {"type":"at", "data":{"qq":qq_uin}})
        return await self._ws.post(json.dumps(payload))


    async def delete_msg(self, message_id):
        data = {
            "action": "delete_msg",
            "params": {
                "message_id": message_id
            }
        }
        return await self._ws.post(json.dumps(data))




