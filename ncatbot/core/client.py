import asyncio
import copy
import inspect
from typing import Callable, Optional, Type, Literal, Union
from ncatbot.core.adapter.adapter import Adapter
from ncatbot.core.api.api import BotAPI
from ncatbot.core.event import MessageSegment
from ncatbot.core.event import BaseEventData, PrivateMessageEvent, GroupMessageEvent, NoticeEvent, RequestEvent, MetaEvent
from ncatbot.utils import (
    OFFICIAL_PRIVATE_MESSAGE_EVENT,
    OFFICIAL_GROUP_MESSAGE_EVENT,
    OFFICIAL_NOTICE_EVENT,
    OFFICIAL_REQUEST_EVENT,
    OFFICIAL_STARTUP_EVENT,
    OFFICIAL_SHUTDOWN_EVENT,
    OFFICIAL_HEARTBEAT_EVENT,
)
from ncatbot.utils import get_log, status, ncatbot_config, ThreadPool

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
        self.adapter = Adapter(ncatbot_config.napcat.ws_uri)
        self.event_handlers: dict[str, list] = {}
        self.thread_pool = ThreadPool(max_workers=8, max_per_func=2)
        self.api = BotAPI(self.adapter.send)
        status.global_api = self.api
        for event_name in EVENTS:
            self.create_official_event_handler_group(event_name)
        
        self.register_builtin_handler()
    
    def register_builtin_handler(self):
        self.add_startup_handler(lambda x: LOG.info(f"Bot {x.self_id} 启动成功"))
    
    def create_official_event_handler_group(self, event_name):
        async def event_callback(event: BaseEventData):
            # 处理回调, 不能阻塞
            for handler in self.event_handlers[event_name]:
                self.thread_pool.submit(handler, event)
            
        self.adapter.event_callback[event_name] = event_callback
        self.event_handlers[event_name] = []
    
    def add_handler(self, event_name, handler):
        self.event_handlers[event_name].append(handler)
    
    # 计划为 filter 提供全面支持, 会直接从 MessageArray 中过滤
    def add_group_message_handler(self, handler: Callable[[GroupMessageEvent], None], filter = None):
        async def warpper(event: GroupMessageEvent):
            new_messages = event.message.filter(filter)
            if len(new_messages) == 0:
                return
            if inspect.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        self.add_handler(OFFICIAL_GROUP_MESSAGE_EVENT, warpper)
    
    def add_private_message_handler(self, handler: Callable[[PrivateMessageEvent], None], filter = None):
        async def warpper(event: PrivateMessageEvent):
            new_messages = event.message.filter(filter)
            if len(new_messages) == 0:
                return
            if inspect.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        self.add_handler(OFFICIAL_PRIVATE_MESSAGE_EVENT, warpper)
    
    def add_notice_handler(self, handler: Callable[[NoticeEvent], None], filter = None):
        self.add_handler(OFFICIAL_NOTICE_EVENT, handler)
    
    def add_request_handler(self, handler: Callable[[RequestEvent], None], filter = Literal["group", "friend"]):
        async def warpper(event: RequestEvent):
            if filter != event.request_type:
                return
            if inspect.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        self.add_handler(OFFICIAL_REQUEST_EVENT, warpper)
    
    def add_startup_handler(self, handler: Callable[[MetaEvent], None]):
        self.add_handler(OFFICIAL_STARTUP_EVENT, handler)
    
    def add_shutdown_handler(self, handler: Callable[[MetaEvent], None]):
        self.add_handler(OFFICIAL_SHUTDOWN_EVENT, handler)
    
    def add_heartbeat_handler(self, handler: Callable[[MetaEvent], None]):
        self.add_handler(OFFICIAL_HEARTBEAT_EVENT, handler)
    
    # 装饰器版本 ==========================================
    def on_group_message(self, handler: Optional[Callable] = None, filter: Union[Type[MessageSegment], None] = None):
        """装饰器注册群消息处理器"""
        if filter is not None and not issubclass(filter, MessageSegment):
            raise TypeError("filter 必须是 MessageSegment 的子类")
        def decorator(f: Callable[[GroupMessageEvent], None]):
            self.add_group_message_handler(f, filter)
            return f # 其实没有必要
        return decorator(handler) if handler else decorator
    
    def on_private_message(self, handler: Optional[Callable] = None, filter: Union[Type[MessageSegment], None] = None):
        """装饰器注册私聊消息处理器"""
        if filter is not None and not issubclass(filter, MessageSegment):
            raise TypeError("filter 必须是 MessageSegment 的子类")
        def decorator(f: Callable[[PrivateMessageEvent], None]):
            self.add_private_message_handler(f, filter)
            return f # 其实没有必要
        return decorator(handler) if handler else decorator
    
    def on_notice(self, handler: Optional[Callable] = None, filter = None):
        """装饰器注册通知事件处理器"""
        def decorator(f: Callable[[NoticeEvent], None]):
            self.add_notice_handler(f, filter)
            return f
        return decorator(handler) if handler else decorator
    
    def on_request(self, handler: Optional[Callable] = None, filter = Literal["group", "friend"]):
        """装饰器注册请求事件处理器"""
        def decorator(f: Callable[[RequestEvent], None]):
            self.add_request_handler(f, filter)
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
    
    def bot_exit(self):
        status.exit = True
        LOG.info("Bot 已经正常退出")
    
    def run(self):
        try:
            asyncio.run(self.adapter.connect_websocket())
        except KeyboardInterrupt:
            self.bot_exit()
            
    def start(self):
        pass
        