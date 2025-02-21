# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-21 18:23:06
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-02-21 19:44:50
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @message: 喵喵喵?
# @Copyright (c) 2025 by Fish-LP, MIT License
# -------------------------
import asyncio
import inspect
import re
import uuid
from typing import Any, Callable, List


class Event:
    """
    事件类，用于封装事件的类型和数据
    """

    def __init__(self, type: str, data: Any):
        """
        初始化事件

        参数:
            type: str - 事件的类型
            data: Any - 事件携带的数据
        """
        self.type = type
        self.data = data
        self._results: List[Any] = []
        self._propagation_stopped = False

    def stop_propagation(self):
        """
        停止事件的传播
        当调用此方法后，后续的处理器将不会被执行
        """
        self._propagation_stopped = True

    def add_result(self, result: Any):
        """
        添加事件处理结果

        参数:
            result: Any - 处理器返回的结果
        """
        self._results.append(result)

    def __repr__(self):
        return f'Event(type="{self.type}",data={self.data})'


class EventBus:
    """
    事件总线类，用于管理和分发事件
    """

    def __init__(self):
        """
        初始化事件总线
        """
        self._exact_handlers = {}
        self._regex_handlers = []

    def subscribe(
        self, event_type: str, handler: Callable[[Event], Any], priority: int = 0
    ) -> str:
        """
        订阅事件处理器，并返回处理器的唯一 ID

        参数:
            event_type: str - 事件类型或正则模式（以 're:' 开头表示正则匹配）
            handler: Callable[[Event], Any] - 事件处理器函数
            priority: int - 处理器的优先级（数字越大，优先级越高）

        返回:
            str - 处理器的唯一 ID
        """
        handler_id = str(uuid.uuid4())
        pattern = None
        if event_type.startswith("re:"):
            pattern = re.compile(event_type[3:])
            self._regex_handlers.append((pattern, priority, handler, handler_id))
        else:
            self._exact_handlers.setdefault(event_type, []).append(
                (pattern, priority, handler, handler_id)
            )
        return handler_id

    def unsubscribe(self, handler_id: str) -> bool:
        """
        取消订阅事件处理器

        参数:
            handler_id: str - 处理器的唯一 ID

        返回:
            bool - 是否成功取消订阅
        """
        # 取消精确匹配处理器
        for event_type in list(self._exact_handlers.keys()):
            self._exact_handlers[event_type] = [
                (patt, pr, h, hid)
                for (patt, pr, h, hid) in self._exact_handlers[event_type]
                if hid != handler_id
            ]
            if not self._exact_handlers[event_type]:
                del self._exact_handlers[event_type]
        # 取消正则匹配处理器
        self._regex_handlers = [
            (patt, pr, h, hid)
            for (patt, pr, h, hid) in self._regex_handlers
            if hid != handler_id
        ]
        return True

    async def publish_async(self, event: Event) -> List[Any]:
        """
        异步发布事件

        参数:
            event: Event - 要发布的事件

        返回值:
            List[Any] - 所有处理器返回的结果的列表
        """
        handlers = []
        if event.type in self._exact_handlers:
            # 处理精确匹配处理器
            for pattern, priority, handler, handler_id in self._exact_handlers[
                event.type
            ]:
                handlers.append((handler, priority, handler_id))
        else:
            # 处理正则匹配处理器
            for pattern, priority, handler, handler_id in self._regex_handlers:
                if pattern and pattern.match(event.type):
                    handlers.append((handler, priority, handler_id))

        # 按优先级排序
        sorted_handlers = sorted(handlers, key=lambda x: (-x[1], x[0].__name__))

        results = []
        # 按优先级顺序调用处理器
        for handler, priority, handler_id in sorted_handlers:
            if event._propagation_stopped:
                break

            if inspect.iscoroutinefunction(handler):
                await handler(event)
            else:
                asyncio.create_task(handler(event))

            # 收集结果
            results.extend(event._results)

        return results

    def publish_sync(self, event: Event) -> List[Any]:
        """
        同步发布事件

        参数:
            event: Event - 要发布的事件

        返回值:
            List[Any] - 所有处理器返回的结果的列表
        """
        loop = asyncio.new_event_loop()  # 创建新的事件循环
        try:
            asyncio.set_event_loop(loop)  # 设置为当前事件循环
            return loop.run_until_complete(self.publish_async(event))
        finally:
            loop.close()  # 关闭事件循环
