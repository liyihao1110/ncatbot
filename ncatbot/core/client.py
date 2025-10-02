import asyncio
import inspect
import traceback
import threading
from typing import (
    Callable,
    Optional,
    Type,
    Literal,
    Union,
    TypedDict,
    List,
    TypeVar,
    Dict,
    TYPE_CHECKING,
)
from typing_extensions import Unpack

if TYPE_CHECKING:
    from ncatbot.plugin_system import BasePlugin

from .adapter import lanuch_napcat_service, Adapter
from .api import BotAPI
from .event import (
    MessageSegment,
    BaseEventData,
    PrivateMessageEvent,
    GroupMessageEvent,
    NoticeEvent,
    RequestEvent,
    MetaEvent,
)
from ..utils import get_log, run_coroutine, ThreadPool
from ..utils import status, ncatbot_config
from ..utils import NcatBotError, NcatBotConnectionError
from ..utils import (
    OFFICIAL_PRIVATE_MESSAGE_EVENT,
    OFFICIAL_GROUP_MESSAGE_EVENT,
    OFFICIAL_NOTICE_EVENT,
    OFFICIAL_REQUEST_EVENT,
    OFFICIAL_STARTUP_EVENT,
    OFFICIAL_SHUTDOWN_EVENT,
    OFFICIAL_HEARTBEAT_EVENT,
)

T = TypeVar("T")
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


class StartArgs(TypedDict, total=False):
    bt_uin: Optional[int]
    root: Optional[str]
    ws_uri: Optional[str]
    webui_uri: Optional[str]
    ws_token: Optional[str]
    webui_token: Optional[str]
    ws_listen_ip: Optional[str]
    remote_mode: Optional[bool]
    enable_webui_interaction: Optional[bool]
    debug: Optional[bool]
    # 以后再加参数直接在这里补一行即可，无需改函数签名


class BotClient:
    _initialized = False  # 兼容旧版本检查

    def __init__(self, only_private: bool = False, max_workers: int = 16):
        if self._initialized:
            raise NcatBotError("BotClient 实例只能创建一次")
        self._initialized = True
        self.adapter = Adapter()
        self.event_handlers: Dict[str, list] = {}
        self.thread_pool = ThreadPool(max_workers=max_workers, max_per_func=4)
        self.api = BotAPI(self.adapter.send)
        self.crash_flag = False
        status.global_api = self.api
        for event_name in EVENTS:
            self.create_official_event_handler_group(event_name)

        self.register_builtin_handler(only_private=only_private)

    def register_builtin_handler(self, only_private: bool = False):
        # 注册插件系统事件处理器
        def make_async_handler(event_name):
            async def wrapper(event: BaseEventData):
                LOG.debug(f"已发布 {event_name} 事件")
                from ncatbot.plugin_system.event import NcatBotEvent

                await self.event_bus.publish(NcatBotEvent(event_name, event))

            return wrapper

        if only_private:
            self.add_private_message_handler(
                make_async_handler(OFFICIAL_PRIVATE_MESSAGE_EVENT)
            )
        else:
            self.add_startup_handler(lambda x: LOG.info(f"Bot {x.self_id} 启动成功"))
            self.add_startup_handler(make_async_handler(OFFICIAL_STARTUP_EVENT))
            self.add_private_message_handler(
                make_async_handler(OFFICIAL_PRIVATE_MESSAGE_EVENT)
            )
            self.add_group_message_handler(
                make_async_handler(OFFICIAL_GROUP_MESSAGE_EVENT)
            )
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
    def add_group_message_handler(
        self, handler: Callable[[GroupMessageEvent], None], filter=None
    ):
        async def wrapper(event: GroupMessageEvent):
            new_messages = event.message.filter(filter)
            if len(new_messages) == 0:
                return
            if inspect.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)

        self.add_handler(OFFICIAL_GROUP_MESSAGE_EVENT, wrapper)

    def add_private_message_handler(
        self, handler: Callable[[PrivateMessageEvent], None], filter=None
    ):
        async def wrapper(event: PrivateMessageEvent):
            new_messages = event.message.filter(filter)
            if len(new_messages) == 0:
                return
            if inspect.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)

        self.add_handler(OFFICIAL_PRIVATE_MESSAGE_EVENT, wrapper)

    def add_notice_handler(self, handler: Callable[[NoticeEvent], None], filter=None):
        self.add_handler(OFFICIAL_NOTICE_EVENT, handler)

    def add_request_handler(
        self, handler: Callable[[RequestEvent], None], filter=Literal["group", "friend"]
    ):
        async def wrapper(event: RequestEvent):
            if filter != event.request_type:
                return
            if inspect.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)

        self.add_handler(OFFICIAL_REQUEST_EVENT, wrapper)

    def add_startup_handler(self, handler: Callable[[MetaEvent], None]):
        self.add_handler(OFFICIAL_STARTUP_EVENT, handler)

    def add_shutdown_handler(self, handler: Callable[[MetaEvent], None]):
        self.add_handler(OFFICIAL_SHUTDOWN_EVENT, handler)

    def add_heartbeat_handler(self, handler: Callable[[MetaEvent], None]):
        self.add_handler(OFFICIAL_HEARTBEAT_EVENT, handler)

    # 装饰器版本 ==========================================
    def on_group_message(
        self,
        filter: Union[Type[MessageSegment], None] = None,
    ):
        """装饰器注册群消息处理器"""
        if filter is not None and not issubclass(filter, MessageSegment):
            raise TypeError("filter 必须是 MessageSegment 的子类")

        def decorator(f: Callable[[GroupMessageEvent], None]):
            self.add_group_message_handler(f, filter)
            return f  # 其实没有必要

        return decorator

    def on_private_message(
        self,
        filter: Union[Type[MessageSegment], None] = None,
    ):
        """装饰器注册私聊消息处理器"""
        if filter is not None and not issubclass(filter, MessageSegment):
            raise TypeError("filter 必须是 MessageSegment 的子类")

        def decorator(f: Callable[[PrivateMessageEvent], None]):
            self.add_private_message_handler(f, filter)
            return f  # 其实没有必要

        return decorator

    def on_notice(self, filter=None):
        """装饰器注册通知事件处理器"""

        def decorator(f: Callable[[NoticeEvent], None]):
            self.add_notice_handler(f, filter)
            return f

        return decorator

    def on_request(self, filter=Literal["group", "friend"]):
        """装饰器注册请求事件处理器"""

        def decorator(f: Callable[[RequestEvent], None]):
            self.add_request_handler(f, filter)
            return f

        return decorator

    def on_startup(self):
        """装饰器注册启动事件处理器"""

        def decorator(f: Callable[[MetaEvent], None]):
            self.add_startup_handler(f)
            return f

        return decorator

    def on_shutdown(self):
        """装饰器注册关闭事件处理器"""

        def decorator(f: Callable[[MetaEvent], None]):
            self.add_shutdown_handler(f)
            return f

        return decorator

    def on_heartbeat(self):
        """装饰器注册心跳事件处理器"""

        def decorator(f: Callable[[MetaEvent], None]):
            self.add_heartbeat_handler(f)
            return f

        return decorator

    def bot_exit(self):
        status.exit = True
        asyncio.run(self.plugin_loader.unload_all())
        LOG.info("Bot 已经正常退出")

    def run_frontend(self, **kwargs: Unpack[StartArgs]):
        try:
            self.start(**kwargs)
        except KeyboardInterrupt:
            self.bot_exit()
        except Exception:
            raise

    def run_backend(self, **kwargs: Unpack[StartArgs]):
        def run_async_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                self.start(**kwargs)
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
            "bt_uin",
            "root",
            "ws_uri",
            "webui_uri",
            "ws_token",
            "webui_token",
            "ws_listen_ip",
            "remote_mode",
            "enable_webui_interaction",
            "debug",
            "skip_plugin_load",
        ]
        for key, value in kwargs.items():
            if key not in legal_args:
                raise NcatBotError(f"非法参数: {key}")
            elif value is None:
                continue
            else:
                ncatbot_config.update_value(key, value)

        ncatbot_config.validate_config()

        # 加载插件
        from ncatbot.plugin_system import EventBus, PluginLoader

        self.event_bus = EventBus()
        self.plugin_loader = PluginLoader(self.event_bus, debug=ncatbot_config.debug)

        run_coroutine(self.plugin_loader.load_plugins)

        if getattr(self, "mock_mode", False):  # MockMixin 中提供
            self.mock_start()
        else:
            # 启动服务（仅在非 mock 模式下）
            lanuch_napcat_service()
            try:
                asyncio.run(self.adapter.connect_websocket())
            except NcatBotConnectionError:
                self.bot_exit()
                raise

    def get_registered_plugins(self) -> List["BasePlugin"]:
        return list(self.plugin_loader.plugins.values())

    def get_plugin(self, type: Type[T]) -> T:
        for plugin in self.get_registered_plugins():
            if isinstance(plugin, type):
                return plugin
        raise ValueError(f"插件 {type.__name__} 未找到")

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
