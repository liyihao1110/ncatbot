import asyncio
import datetime
import json
from typing import Dict, Callable, Any, Optional, Literal
import websockets
import uuid
from threading import Lock
from queue import Queue
from websockets.client import WebSocketClientProtocol
from ncatbot.core.event import PrivateMessageEvent, GroupMessageEvent, NoticeEvent, RequestEvent, MetaEvent, BaseEventData
from ncatbot.utils import get_log
from ncatbot.utils import (
    OFFICIAL_PRIVATE_MESSAGE_EVENT,
    OFFICIAL_GROUP_MESSAGE_EVENT,
    OFFICIAL_NOTICE_EVENT,
    OFFICIAL_REQUEST_EVENT,
    OFFICIAL_STARTUP_EVENT,
    OFFICIAL_SHUTDOWN_EVENT,
    OFFICIAL_HEARTBEAT_EVENT,
)

LOG = get_log("Adapter")

class Adapter:
    def __init__(self, ws_url: str):
        self.pending_requests: Dict[str, Queue] = {}
        self.ws_url = ws_url
        self.client: Optional[WebSocketClientProtocol] = None
        self.event_callback: Dict[str, Callable[[BaseEventData], None]] = {}
        self._lock = Lock()

    def start_websocket(self):
        """启动服务器"""
        pass

    def is_websocket_online(self):
        """检查服务器是否在线"""
        return self.client is not None and not self.client.closed

    async def debug_event_loop(self):
        while True:
            print("Event loop is alive:", datetime.datetime.now())
            await asyncio.sleep(1)

    async def send(self, path: str, params: dict = None, timeout: float = 10.0) -> dict:
        """异步发送消息并等待响应"""
        # send 函数可能会在其它事件循环被调用, 需要使用线程安全通信方式
        echo = str(uuid.uuid4())
        queue = Queue(maxsize=1)
        
        with self._lock:
            self.pending_requests[echo] = queue

        try:
            if not self.client or self.client.closed:
                raise ConnectionError("WebSocket 未连接")
                
            await self.client.send(json.dumps({
                "action": path.replace("/", ""),
                "params": params or {},
                "echo": echo
            }))
            
            result = await asyncio.to_thread(queue.get, timeout=timeout)
            return result
            
        finally:
            with self._lock:
                self.pending_requests.pop(echo, None)

    async def connect_websocket(self) -> bool:
        """连接 ws 客户端"""
        asyncio.create_task(self.debug_event_loop())
        self.client = await websockets.connect(self.ws_url)
        try:
            while True:
                message = await self.client.recv()
                message_data: dict = json.loads(message)
                if "echo" in message_data:
                    # 处理API响应
                    await self._handle_response(message_data)
                else:
                    # 处理事件
                    await self._handle_event(message_data)
                
        except websockets.exceptions.ConnectionClosed:
            await self._cleanup()
            raise ConnectionError("WebSocket 连接已关闭")
        except Exception as e:
            await self._cleanup()
            raise

    async def _handle_response(self, message: dict):
        """处理API响应, 不能阻塞"""
        with self._lock:
            queue = self.pending_requests.get(message.get("echo"))
            queue.put(message)

    async def _handle_event(self, message: dict):
        """处理事件, 不能阻塞"""
        post_type: Literal["message", "notice", "request", "meta"] = message.get("post_type")
        
        if post_type == "message":
            message_type: Literal["private", "group"] = message.get("message_type")
            if message_type == "private":
                event = PrivateMessageEvent(message)
                callback = self.event_callback.get(OFFICIAL_PRIVATE_MESSAGE_EVENT)
            elif message_type == "group":
                event = GroupMessageEvent(message)
                callback = self.event_callback.get(OFFICIAL_GROUP_MESSAGE_EVENT)
        elif post_type == "notice":
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
        
        if callback:
            try:
                await callback(event)
            except Exception as e:
                LOG.error(f"处理事件时出错: {e}")

    async def _cleanup(self):
        """清理资源"""
        async with self._lock:
            for future in self.pending_requests.values():
                if not future.done():
                    future.cancel()
            self.pending_requests.clear()
        
        if self.client and not self.client.closed:
            await self.client.close()
        self.client = None
        