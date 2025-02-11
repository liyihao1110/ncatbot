import asyncio
import inspect
import re
from collections import defaultdict
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Pattern,
    Tuple,
)
from weakref import ReferenceType, WeakMethod, ref

from ncatbot.plugin.config import EVENT_QUEUE_MAX_SIZE
from ncatbot.utils.literals import (
    OFFICIAL_GROUP_MESSAGE_EVENT,
    OFFICIAL_NOTICE_EVENT,
    OFFICIAL_PRIVATE_MESSAGE_EVENT,
    OFFICIAL_REQUEST_EVENT,
)
from ncatbot.utils.logger import get_log

_log = get_log()


# endregion
# region ----------------- 事件对象 -----------------
class Event:
    """
    事件对象,用于在事件总线上传递事件数据
    """

    def __init__(self, type: str, data: Any):
        self.type = type
        self.data = data
        self._stopped: bool = False
        self.results: List[Any] = list()
        self.source: Optional[str] = None

    def stop_propagation(self):
        """
        停止事件传播,防止事件继续被后续处理器处理
        """
        self._stopped = True

    def add_result(self, result: Any):
        """
        向事件结果列表中添加处理结果
        """
        self.results.append(result)


# endregion
# region ----------------- 事件总线 -----------------
class EventBus:
    """
    事件总线,用于管理和分发事件
    """

    def __init__(self):
        """
        初始化事件总线,设置事件处理器存储结构和事件队列
        """
        self._exact_handlers: Dict[str, List[Tuple[int, Callable]]] = defaultdict(list)
        self._regex_handlers: List[Tuple[Pattern, int, Callable]] = []
        self._execution_order: Dict[str, List[Callable]] = defaultdict(list)
        self.exception_handlers: List[Callable] = []
        self._queues: Dict[str, asyncio.Queue] = defaultdict(
            lambda: asyncio.Queue(maxsize=EVENT_QUEUE_MAX_SIZE)
        )
        self._processing_tasks: Dict[str, asyncio.Task] = {}

    def _get_plugin_name(self, handler: Callable) -> str:
        """
        获取处理器所属插件名称
        """
        try:
            if inspect.ismethod(handler):
                return handler.__self__.name
            if isinstance(handler, (ref, WeakMethod, ReferenceType)):
                obj = handler()
                return getattr(obj, "name", "") if obj else ""
            if hasattr(handler, "__self__"):
                return handler.__self__.name
            return getattr(handler, "_plugin_name", "")
        except Exception:
            return ""

    def subscribe(self, event_type: str, handler: Callable, priority: int = 0):
        """
        订阅事件,支持正则表达式匹配
        :param event_type: 事件类型,支持正则表达式前缀为're:'
        :param handler: 事件处理器
        :param priority: 事件处理器优先级,数值越高优先级越高
        """
        # 处理弱引用
        if inspect.ismethod(handler):
            handler_ref = WeakMethod(handler)
        elif inspect.isfunction(handler):
            handler_ref = ref(handler)
        else:
            handler_ref = handler

        if event_type.startswith("re:"):
            pattern = re.compile(event_type[3:])
            self._regex_handlers.append((pattern, priority, handler_ref))
        else:
            self._exact_handlers[event_type].append((priority, handler_ref))

        self._rebuild_execution_order(event_type)

    def _rebuild_execution_order(self, event_type: str):
        """
        重建事件处理器的执行顺序,考虑优先级和插件名称排序
        """
        # 精确匹配处理
        exact_entries = sorted(
            self._exact_handlers[event_type],
            key=lambda x: (-x[0], self._get_plugin_name(x[1]).lower()),
        )
        exact_handlers = [h for _, h in exact_entries]

        # 正则匹配处理
        regex_handlers = []
        for pattern, priority, handler in self._regex_handlers:
            if pattern.search(event_type):
                regex_handlers.append(
                    (-priority, self._get_plugin_name(handler).lower(), handler)
                )

        regex_handlers.sort(key=lambda x: (x[0], x[1]))
        regex_handlers = [h for _, _, h in regex_handlers]

        # 合并处理顺序: 精确匹配优先于正则匹配
        combined = []
        seen = set()
        for h in exact_handlers + regex_handlers:
            handler = h() if isinstance(h, (ref, WeakMethod, ReferenceType)) else h
            if handler and id(handler) not in seen:
                combined.append(handler)
                seen.add(id(handler))

        self._execution_order[event_type] = combined

    async def _process_event(self, event: Event):
        """
        核心事件处理逻辑,依次调用事件处理器
        """
        for handler in self._execution_order.get(event.type, []):
            if event._stopped:
                break

            try:
                if inspect.iscoroutinefunction(handler):
                    if event.type in (
                        OFFICIAL_GROUP_MESSAGE_EVENT,
                        OFFICIAL_PRIVATE_MESSAGE_EVENT,
                        OFFICIAL_NOTICE_EVENT,
                        OFFICIAL_REQUEST_EVENT,
                    ):
                        await handler(event.data)
                    else:
                        await handler(event)
                else:
                    if event.type in (
                        OFFICIAL_GROUP_MESSAGE_EVENT,
                        OFFICIAL_PRIVATE_MESSAGE_EVENT,
                        OFFICIAL_NOTICE_EVENT,
                        OFFICIAL_REQUEST_EVENT,
                    ):
                        handler(event.data)
                    else:
                        handler(event)
            except Exception as e:
                _log.error(e)
                event.add_result({"error": str(e)})
                for eh in self.exception_handlers:
                    try:
                        if inspect.iscoroutinefunction(eh):
                            await eh(e, event)
                        else:
                            eh(e, event)
                    except Exception:
                        pass

    async def publish_sync(self, event: Event) -> List[Any]:
        """
        发布同步事件,等待事件返回
        :param event: 要发布的事件对象
        :return: 事件处理结果列表
        """
        _log.debug(f"发布同步事件: {event.type}")
        await self._queues[event.type].put(event)
        await self._process_event(event)
        return event.results

    async def publish_async(self, event: Event) -> None:
        """
        发布异步事件,不等待事件返回
        :param event: 要发布的事件对象
        """
        _log.debug(f"发布异步事件: {event.type}")
        await self._queues[event.type].put(event)
        if self._queues[event.type].qsize() == 1:  # 避免重复创建任务
            self._processing_tasks[event.type] = asyncio.create_task(
                self._process_queue(event.type)
            )

    async def _process_queue(self, event_type: str):
        """
        处理指定事件队列中的事件
        """
        while not self._queues[event_type].empty():
            event = await self._queues[event_type].get()
            await self._process_event(event)
            self._queues[event_type].task_done()


# endregion
# region ----------------- 注册兼容 -----------------
class CompatibleEnrollment:
    events = {
        OFFICIAL_PRIVATE_MESSAGE_EVENT: [],
        OFFICIAL_GROUP_MESSAGE_EVENT: [],
        OFFICIAL_REQUEST_EVENT: [],
        OFFICIAL_NOTICE_EVENT: [],
    }

    def __init__(self):
        raise ValueError("不需要实例化")

    @classmethod
    def group_event(cls, types=None):
        def decorator(func):  # ncatbot.private_event
            cls.events[OFFICIAL_GROUP_MESSAGE_EVENT].append(func)

            def wrapper(instance, event: Event):
                # 在这里过滤types
                return func(instance, event.data)

            return wrapper

        return decorator

    @classmethod
    def private_event(cls, types=None):
        def decorator(func):  # ncatbot.private_event
            cls.events[OFFICIAL_PRIVATE_MESSAGE_EVENT].append(func)

            def wrapper(instance, event: Event):
                # 在这里过滤types
                return func(instance, event.data)

            return wrapper

        return decorator

    @classmethod
    def notice_event(cls, types=None):
        def decorator(func):  # ncatbot.notice_event
            cls.events[OFFICIAL_NOTICE_EVENT].append(func)

            def wrapper(instance, event: Event):
                # 在这里过滤types
                return func(instance, event.data)

            return wrapper

        return decorator

    @classmethod
    def request_event(cls, types=None):
        def decorator(func):  # ncatbot.request_event
            cls.events[OFFICIAL_REQUEST_EVENT].append(func)

            def wrapper(instance, event: Event):
                # 在这里过滤types
                return func(instance, event.data)

            return wrapper

        return decorator


# endregin
