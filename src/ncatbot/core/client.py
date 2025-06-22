import asyncio

from typing import Callable, Optional
from ncatbot.core.adapter.adapter import Adapter
from ncatbot.core.api.api import BotAPI
from ncatbot.core.event import BaseEventData, PrivateMessageEvent, GroupMessageEvent, NoticeEvent, RequestEvent, MetaEvent
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import functools
import threading
from ncatbot.utils import (
    OFFICIAL_PRIVATE_MESSAGE_EVENT,
    OFFICIAL_GROUP_MESSAGE_EVENT,
    OFFICIAL_NOTICE_EVENT,
    OFFICIAL_REQUEST_EVENT,
    OFFICIAL_STARTUP_EVENT,
    OFFICIAL_SHUTDOWN_EVENT,
    OFFICIAL_HEARTBEAT_EVENT,
)
from ncatbot.utils import get_log, fire_and_forget, run_func_async

LOG = get_log("Client")    
EVENTS = (
    OFFICIAL_PRIVATE_MESSAGE_EVENT,
    OFFICIAL_GROUP_MESSAGE_EVENT,
    OFFICIAL_NOTICE_EVENT,
    OFFICIAL_REQUEST_EVENT,
    OFFICIAL_STARTUP_EVENT,
    OFFICIAL_SHUTDOWN_EVENT,
    OFFICIAL_HEARTBEAT_EVENT,
)

class BotClient:
    def __init__(self):
        self.adapter = Adapter("ws://10.208.96.251:3001")
        self.event_handlers: dict[str, list] = {}
        self.api = BotAPI(self.adapter.send)
        for event_name in EVENTS:
            self.create_official_event_handler_group(event_name)
            
        # 调试
        async def test(msg: PrivateMessageEvent):
            result = await self.api.simple_send_private_msg(
                user_id=msg.user_id,
                message=[
                    {
                        "type": "text",
                        "data": {
                            "text": "Hello NcatBot"
                        }
                    }
                ]
            )
            print(result)
            
        self.add_private_message_handler(test)
    
    def create_official_event_handler_group(self, event_name):
        async def event_callback(event: BaseEventData):
            # 处理回调, 不能阻塞
            for handler in self.event_handlers[event_name]:
                fire_and_forget(run_func_async(handler, event))
            
        self.adapter.event_callback[event_name] = event_callback
        self.event_handlers[event_name] = []
    
    def add_handler(self, event_name, handler):
        self.event_handlers[event_name].append(handler)
    
    # 计划为 filter 提供全面支持, 会直接从 MessageArray 中过滤
    def add_group_message_handler(self, handler: Callable[[GroupMessageEvent], None], filter = None):
        self.add_handler(OFFICIAL_GROUP_MESSAGE_EVENT, handler)
    
    def add_private_message_handler(self, handler: Callable[[PrivateMessageEvent], None], filter = None):
        self.add_handler(OFFICIAL_PRIVATE_MESSAGE_EVENT, handler)
    
    def add_notice_handler(self, handler: Callable[[NoticeEvent], None], filter = None):
        self.add_handler(OFFICIAL_NOTICE_EVENT, handler)
    
    def add_request_handler(self, handler: Callable[[RequestEvent], None], filter = None):
        self.add_handler(OFFICIAL_REQUEST_EVENT, handler)
    
    def add_startup_handler(self, handler: Callable[[MetaEvent], None]):
        self.add_handler(OFFICIAL_STARTUP_EVENT, handler)
    
    def add_shutdown_handler(self, handler: Callable[[MetaEvent], None]):
        self.add_handler(OFFICIAL_SHUTDOWN_EVENT, handler)
    
    def add_heartbeat_handler(self, handler: Callable[[MetaEvent], None]):
        self.add_handler(OFFICIAL_HEARTBEAT_EVENT, handler)
    
    # 装饰器版本 ==========================================
    def on_group_message(self, handler: Optional[Callable] = None, filter = None):
        """装饰器注册群消息处理器"""
        def decorator(f: Callable[[GroupMessageEvent], None]):
            self.add_group_message_handler(f)
            return f
        return decorator(handler) if handler else decorator
    
    def on_private_message(self, handler: Optional[Callable] = None, filter = None):
        """装饰器注册私聊消息处理器"""
        def decorator(f: Callable[[PrivateMessageEvent], None]):
            self.add_private_message_handler(f)
            return f
        return decorator(handler) if handler else decorator
    
    def on_notice(self, handler: Optional[Callable] = None, filter = None):
        """装饰器注册通知事件处理器"""
        def decorator(f: Callable[[NoticeEvent], None]):
            self.add_notice_handler(f)
            return f
        return decorator(handler) if handler else decorator
    
    def on_request(self, handler: Optional[Callable] = None, filter = None):
        """装饰器注册请求事件处理器"""
        def decorator(f: Callable[[RequestEvent], None]):
            self.add_request_handler(f)
            return f
        return decorator(handler) if handler else decorator
    
    def on_startup(self, handler: Optional[Callable] = None):
        """装饰器注册启动事件处理器"""
        def decorator(f: Callable[[MetaEvent], None]):
            self.add_startup_handler(f)
            return f
        return decorator(handler) if handler else decorator
    
    def on_shutdown(self, handler: Optional[Callable] = None):
        """装饰器注册关闭事件处理器"""
        def decorator(f: Callable[[MetaEvent], None]):
            self.add_shutdown_handler(f)
            return f
        return decorator(handler) if handler else decorator
    
    def on_heartbeat(self, handler: Optional[Callable] = None):
        """装饰器注册心跳事件处理器"""
        def decorator(f: Callable[[MetaEvent], None]):
            self.add_heartbeat_handler(f)
            return f
        return decorator(handler) if handler else decorator    
    
    def run(self):
        asyncio.run(self.adapter.connect_websocket())
    
    def start(self):
        pass
        