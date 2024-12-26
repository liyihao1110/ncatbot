# encoding: utf-8

"""机器人客户端文件，处理事件和业务逻辑"""

import asyncio
import importlib

from .wsapi import WsApi
from .api import BotAPI
from .flags import Intents
from .wstart import BotWebSocket

from . import logging
from . import message

_log = logging.get_logger()

class Client:
    def __init__(self, intents: Intents, plugins: list = None):
        self.intents = intents
        self._websocket = None
        self._plugins = plugins or []
        self._api = WsApi()
        self._hpapi = BotAPI()

        for plugin_name in self._plugins:
            try:
                module = importlib.import_module(f".plugins.{plugin_name}", __package__)
                plugin_class = getattr(module, plugin_name, None)
                if plugin_class is None:
                    _log.warning(f"[ncatpy] 插件 {plugin_name} 未找到对应的类，跳过加载。")
                    continue
                setattr(self, f"_{plugin_name}", plugin_class())
                _log.info(f"[ncatpy] 插件 {plugin_name} 加载成功")
            except ImportError as e:
                _log.error(f"[ncatpy] 插件 {plugin_name} 加载失败: {e}")
            except Exception as e:
                _log.error(f"[ncatpy] 插件 {plugin_name} 初始化时发生异常: {e}")



    async def on_event(self, event_type: str, data: dict):
        if event_type == "message" or event_type == "message_sent":
            if data.get("message_type") == "group" and self.intents.group_event:
                await self.on_group_message(message.GroupMessage(data))
            elif data.get("message_type") == "private" and self.intents.private_event:
                await self.on_private_message(message.PrivateMessage(data))
        elif event_type == "notice":
            await self.on_notice(message.NoticeMessage(data))
        elif event_type == "request":
            await self.on_request(message.RequestMessage(data))
        elif event_type == "meta_event":
            if data.get('meta_event_type') == "lifecycle":
                _log.info(f"[ncatpy] 机器人 {data.get('self_id')} 已启动!")
            elif data.get('meta_event_type') == "heartbeat":
                _log.debug(f"[ncatpy] 收到心跳包: {data}")
        else:
            _log.warning(f"[ncatpy] 收到未知事件: {event_type}")


    async def on_group_message(self, message):
        _log.debug(f"[ncatpy] 收到群消息: {message}")

    async def on_private_message(self, message):
        _log.debug(f"[ncatpy] 收到私聊消息: {message}")

    async def on_notice(self, notice):
        _log.debug(f"[ncatpy] 收到通知消息: {notice}")

    async def on_request(self, request):
        _log.debug(f"[ncatpy] 收到请求消息: {request}")

    def run(self):
        loop = asyncio.get_event_loop()
        self._websocket = BotWebSocket(self)
        loop.run_until_complete(self._websocket.ws_connect())
