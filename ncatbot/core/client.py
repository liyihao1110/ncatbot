import asyncio
import copy
import inspect
import traceback
import threading
from typing import Callable, Optional, Type, Literal, Union

from ncatbot.core.adapter.adapter import Adapter
from ncatbot.core.api.api import BotAPI
from ncatbot.core.event import MessageSegment
from ncatbot.plugin_system.event import EventBus
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
from ncatbot.core.adapter.nc.launch import lanuch_napcat_service
from ncatbot.utils.error import NcatBotError, NcatBotConnectionError
from ncatbot.plugin_system import PluginLoader, NcatBotEvent

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
    def __init__(self, *args, **kwargs):
        self.adapter = Adapter()
        self.event_handlers: dict[str, list] = {}
        self.thread_pool = ThreadPool(max_workers=1, max_per_func=1)
        self.api = BotAPI(self.adapter.send)
        self.crash_flag = False
        status.global_api = self.api
        for event_name in EVENTS:
            self.create_official_event_handler_group(event_name)
        
        self.register_builtin_handler(*args, **kwargs)
    
    def register_builtin_handler(self, *args, **kwargs):
        # 注册插件系统事件处理器
        def make_async_handler(event_name):
            async def warpper(event: BaseEventData):
                LOG.debug(f"已发布 {event_name} 事件")
                await self.event_bus.publish(NcatBotEvent(event_name, event))
            return warpper
        
        if 'only_private' in kwargs and kwargs['only_private']:
            self.add_private_message_handler(make_async_handler(OFFICIAL_PRIVATE_MESSAGE_EVENT))
        else:
            self.add_startup_handler(lambda x: LOG.info(f"Bot {x.self_id} 启动成功"))
            self.add_startup_handler(make_async_handler(OFFICIAL_STARTUP_EVENT))
            self.add_private_message_handler(make_async_handler(OFFICIAL_PRIVATE_MESSAGE_EVENT))
            self.add_group_message_handler(make_async_handler(OFFICIAL_GROUP_MESSAGE_EVENT))
            self.add_notice_handler(make_async_handler(OFFICIAL_NOTICE_EVENT))
            self.add_request_handler(make_async_handler(OFFICIAL_REQUEST_EVENT))
            self.add_shutdown_handler(make_async_handler(OFFICIAL_SHUTDOWN_EVENT))
            self.add_heartbeat_handler(make_async_handler(OFFICIAL_HEARTBEAT_EVENT))
    
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
        asyncio.run(self.plugin_loader.unload_all())
        LOG.info("Bot 已经正常退出")
    
    def run_frontend(
        self,
        bt_uin=None,
        root=None,
        ws_uri=None,
        webui_uri=None,
        ws_token=None,
        webui_token=None,
        ws_listen_ip=None,
        remote_mode=None,
        enable_webui_interaction=None,
        debug=None,
        *args,
        **kwargs
    ):
        try:
            self.start(
                bt_uin=bt_uin,
                root=root,
                ws_uri=ws_uri,
                webui_uri=webui_uri,
                ws_token=ws_token,
                webui_token=webui_token,
                ws_listen_ip=ws_listen_ip,
                remote_mode=remote_mode,
                enable_webui_interaction=enable_webui_interaction,
                debug=debug,
                *args,
                **kwargs
            )
        except KeyboardInterrupt:
            self.bot_exit()
        except Exception:
            raise
            
    def run_backend(
        self,
        bt_uin=None,
        root=None,
        ws_uri=None,
        webui_uri=None,
        ws_token=None,
        webui_token=None,
        ws_listen_ip=None,
        remote_mode=None,
        enable_webui_interaction=None,
        debug=None,
        *args,
        **kwargs
    ):
        def run_async_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                self.start(
                    bt_uin=bt_uin,
                    root=root,
                    ws_uri=ws_uri,
                    webui_uri=webui_uri,
                    ws_token=ws_token,
                    webui_token=webui_token,
                    ws_listen_ip=ws_listen_ip,
                    remote_mode=remote_mode,
                    enable_webui_interaction=enable_webui_interaction,
                    debug=debug,
                    *args,
                    **kwargs
                )
            except Exception as e:
                LOG.error(f"Bot 启动失败: {e}")
                LOG.info(traceback.format_exc())
            finally:
                loop.close()
                self.crash_flag = True
                self.release_callback(None)
        
        thread = threading.Thread(target=run_async_task)
        thread.daemon = True  # 设置为守护线程
        self.lock = threading.Lock()
        self.lock.acquire()
        self.release_callback = lambda x: self.lock.release()
        self.add_startup_handler(self.release_callback)
        thread.start()
        flag = self.lock.acquire(timeout=90)
        if self.crash_flag:
            raise NcatBotError("Bot 启动失败", log=False)
        if not flag:
            raise NcatBotError("Bot 启动超时", log=True)
        return self.api
            
    def start(self, **kwargs):
        # 配置参数
        legal_args = [
            "bt_uin", "root", "ws_uri", "webui_uri", "ws_token",
            "webui_token", "ws_listen_ip", "remote_mode",
            "enable_webui_interaction", "debug"
        ]
        for key, value in kwargs.items():
            if key not in legal_args:
                raise NcatBotError(f"非法参数: {key}")
            if value is None:
                continue
            ncatbot_config.update_value(key, value)
        ncatbot_config.validate_config()
        # 加载插件
        self.event_bus = EventBus()
        self.plugin_loader = PluginLoader(self.event_bus, debug=ncatbot_config.debug)
        asyncio.run(self.plugin_loader.load_plugins())
        # 启动服务
        lanuch_napcat_service()
        try:
            asyncio.run(self.adapter.connect_websocket())
        except NcatBotConnectionError as e:
            self.bot_exit()
            raise
    
    # 兼容 3xx 版本
    group_event = on_group_message
    private_event = on_private_message
    notice_event = on_notice
    request_event = on_request
    startup_event = on_startup
    shutdown_event = on_shutdown
    heartbeat_event = on_heartbeat
    add_group_event_handler = add_group_message_handler
    add_private_event_handler = add_private_message_handler
    add_notice_event_handler = add_notice_handler
    add_request_event_handler = add_request_handler
    add_startup_event_handler = add_startup_handler
    run_blocking = run_frontend
    run_non_blocking = run_backend
    run = run_frontend