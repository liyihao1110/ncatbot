import asyncio
import json
import traceback
from typing import Dict, Callable, Optional, Literal
import uuid
from threading import Lock
from queue import Queue
import websockets
from .nc.launch import napcat_service_ok
from websockets.exceptions import ConnectionClosedError
from ncatbot.core.event import (
    PokeNoticeEvent,
    PrivateMessageEvent,
    GroupMessageEvent,
    MessageSentEvent,
    NoticeEvent,
    RequestEvent,
    MetaEvent,
    BaseEventData,
)
from ncatbot.utils import get_log, ncatbot_config
from ncatbot.utils import (
    OFFICIAL_PRIVATE_MESSAGE_EVENT,
    OFFICIAL_GROUP_MESSAGE_EVENT,
    OFFICIAL_MESSAGE_SENT_EVENT,
    OFFICIAL_NOTICE_EVENT,
    OFFICIAL_REQUEST_EVENT,
    OFFICIAL_STARTUP_EVENT,
    OFFICIAL_HEARTBEAT_EVENT,
)
from ncatbot.utils.error import NcatBotError, NcatBotConnectionError, AdapterEventError

LOG = get_log("Adapter")


class Adapter:
    def __init__(self):
        self.pending_requests: Dict[str, Queue] = {}
        self.client: Optional[websockets.ClientConnection] = None
        self.event_callback: Dict[str, Callable[[BaseEventData], None]] = {}
        self._lock = Lock()

    def start_websocket(self):
        """启动服务器"""
        pass

    def is_websocket_online(self):
        """检查服务器是否在线"""
        return self.client is not None

    async def send(
        self, path: str, params: dict = None, timeout: float = 300.0
    ) -> dict:
        """异步发送消息并等待响应"""
        # send 函数可能会在其它事件循环被调用, 需要使用线程安全通信方式
        echo = str(uuid.uuid4())
        queue = Queue(maxsize=1)
        LOG.debug(f"向 {path} 发送请求: {echo}")
        LOG.debug(f"请求参数: {params}")

        with self._lock:
            self.pending_requests[echo] = queue

        try:
            if not self.client:
                raise ConnectionError("WebSocket 未连接")

            await self.client.send(
                json.dumps(
                    {
                        "action": path.replace("/", ""),
                        "params": params or {},
                        "echo": echo,
                    }
                )
            )

            # 为了避免使用异步队列的心智开销使用线程池
            result = await asyncio.to_thread(queue.get, timeout=timeout)
            return result

        finally:
            with self._lock:
                self.pending_requests.pop(echo, None)

    async def connect_websocket(self) -> bool:
        """连接 ws 客户端"""
        uri_with_token = ncatbot_config.get_uri_with_token()
        self.client = await websockets.connect(
            uri_with_token, close_timeout=0.2, max_size=2**30, open_timeout=1
        )
        LOG.info("NapCat WebSocket 连接成功")
        while True:
            try:
                while True:
                    LOG.debug("looping")
                    message = await self.client.recv()
                    message_data: dict = json.loads(message)
                    LOG.debug(message_data)
                    if "echo" in message_data:
                        await self._handle_response(message_data)
                    else:
                        await self._handle_event(message_data)

            except asyncio.CancelledError:
                # 当任务被取消时（如KeyboardInterrupt）
                await self.cleanup()
                raise

            except ConnectionClosedError:
                LOG.info("NapCat WebSocket 连接已关闭, 正在尝试重新连接...")
                if napcat_service_ok(ncatbot_config.websocket_timeout):
                    self.client = await websockets.connect(
                        uri_with_token,
                        close_timeout=0.2,
                        max_size=2**30,
                        open_timeout=1,
                    )
                    LOG.info("NapCat WebSocket 重新连接成功")
                    continue
                # TODO 细化判断
                raise NcatBotConnectionError("NapCat 服务主动关闭了连接")

            except AdapterEventError:
                LOG.warning("构造事件时出错, 已抛弃该事件")

            except Exception:
                await self.cleanup()
                LOG.info(traceback.format_exc())
                raise NcatBotError("未知网络错误")

    async def _handle_response(self, message: dict):
        """处理API响应, 不能阻塞"""
        with self._lock:
            queue = self.pending_requests.get(message.get("echo"))
            if queue is None:
                LOG.warning(f"收到未匹配的响应: {message.get('echo')}")
                return
            queue.put(message)

    async def _handle_event(self, message: dict):
        """处理事件, 不能阻塞"""
        LOG.debug(f"收到事件: {message}")
        try:
            post_type: Literal[
                "message", "notice", "request", "meta_event", "message_sent"
            ] = message.get("post_type")

            callback = None

            if post_type == "message":
                message_type: Literal["private", "group"] = message.get("message_type")
                if message_type == "private":
                    event = PrivateMessageEvent(message)
                    callback = self.event_callback.get(OFFICIAL_PRIVATE_MESSAGE_EVENT)
                elif message_type == "group":
                    event = GroupMessageEvent(message)
                    callback = self.event_callback.get(OFFICIAL_GROUP_MESSAGE_EVENT)
            elif post_type == "notice":
                if message.get("sub_type", "") == "poke":
                    event = PokeNoticeEvent(message)
                else:
                    event = NoticeEvent(message)
                callback = self.event_callback.get(OFFICIAL_NOTICE_EVENT)
            elif post_type == "request":
                event = RequestEvent(message)
                callback = self.event_callback.get(OFFICIAL_REQUEST_EVENT)
            elif post_type == "meta_event":
                event = MetaEvent(message)
                if event.meta_event_type == "lifecycle":
                    if event.sub_type == "enable":
                        callback = None
                        # TODO: 正确的 Bot 上线处理
                    elif event.sub_type == "disable":
                        callback = None
                        # TODO: 正确的 Bot 下线处理
                    elif event.sub_type == "connect":
                        callback = self.event_callback.get(OFFICIAL_STARTUP_EVENT)
                elif event.meta_event_type == "heartbeat":
                    callback = self.event_callback.get(OFFICIAL_HEARTBEAT_EVENT)
            elif post_type == "message_sent":
                event = MessageSentEvent(message)
                callback = self.event_callback.get(OFFICIAL_MESSAGE_SENT_EVENT)
        except Exception as e:
            raise AdapterEventError(f"构造{post_type}事件时出错: {e}")

        try:
            if callback:
                try:
                    await callback(event)
                except Exception as e:
                    LOG.error(f"处理事件回调时出错: {e}")
            else:
                LOG.warning(f"未找到事件回调: {post_type}")
        except Exception as e:
            raise NcatBotError(f"处理事件回调时出错: {e}")

    async def cleanup(self):
        """清理资源"""
        try:
            with self._lock:
                for future in self.pending_requests.values():
                    if not future.done():
                        future.cancel()
                self.pending_requests.clear()

            if self.client:
                await self.client.close()
            LOG.info("NapCat WebSocket 连接已关闭")
            self.client = None
        except Exception as e:
            LOG.error(f"清理资源时出错: {e}")
