from typing import Optional, List, Callable, Any, Union
from ncatbot.message import GroupMessage, PrivateMessage
import logging

class Plugin:
    def __init__(self, name: str):
        self.name = name
        self.log = logging.getLogger(f"plugin.{name}")
        self._group_handlers = []
        self._private_handlers = []
        self._notice_handlers = []
        self._request_handlers = []
        
    def group_event(self, types: Optional[List[str]] = None):
        def decorator(func: Callable):
            self._group_handlers.append((func, types))
            return func
        return decorator
        
    def private_event(self, types: Optional[List[str]] = None):
        def decorator(func: Callable):
            self._private_handlers.append((func, types))
            return func
        return decorator
        
    def notice_event(self):
        def decorator(func: Callable):
            self._notice_handlers.append(func)
            return func
        return decorator
        
    def request_event(self):
        def decorator(func: Callable):
            self._request_handlers.append(func)
            return func
        return decorator

    async def handle_group_message(self, msg: GroupMessage):
        for handler, types in self._group_handlers:
            try:
                if types is None or any(i["type"] in types for i in msg.message):
                    await handler(msg)
            except Exception as e:
                self.log.error(f"处理群消息失败: {e}")

    async def handle_private_message(self, msg: PrivateMessage):
        for handler, types in self._private_handlers:
            try:
                if types is None or any(i["type"] in types for i in msg.message):
                    await handler(msg)
            except Exception as e:
                self.log.error(f"处理私聊消息失败: {e}")
                
    def init_plugin(self, bot) -> None:
        """插件初始化方法,由插件实现"""
        raise NotImplementedError
