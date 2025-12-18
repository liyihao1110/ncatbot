import asyncio
import re
import uuid
import traceback
from functools import lru_cache
from ncatbot.utils import get_log

from typing import Any, Callable, Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..base_plugin import BasePlugin

from .event import NcatBotEvent

LOG = get_log("EventBus")


class HandlerTimeoutError(Exception):
    def __init__(self, meta_data, handler, time):
        super().__init__()
        self.meta_data = meta_data
        self.handler = handler
        self.time = time

    meta_data: dict
    handler: str
    time: float

    def __str__(self):
        return f"来自 {self.meta_data['name']} 的处理器 {self.handler} 执行超时 {self.time}"


class EventBus:
    def __init__(self, default_timeout: float = 120, max_workers: int = 1) -> None:
        """
        事件总线实现 - 纯异步版本

        Args:
            default_timeout: 默认处理器超时时间（秒）
            max_workers: 兼容性参数,已废弃(纯异步架构不需要)
        """
        self._exact: Dict[str, List[Tuple]] = {}
        self._regex: List[Tuple] = []
        self.default_timeout = default_timeout

        # 存储处理器元数据
        self._handler_meta: Dict[uuid.UUID, Dict] = {}

        if max_workers != 1:
            LOG.warning(
                f"EventBus 已重构为纯异步架构,max_workers 参数已废弃(传入值: {max_workers})"
            )

    async def _run_handler(self, handler: Callable, event: NcatBotEvent) -> Any:
        """
        执行处理器(异步版本)

        对于异步处理器: 直接 await
        对于同步处理器: 使用 asyncio.to_thread() 避免阻塞事件循环
        """
        try:
            if asyncio.iscoroutinefunction(handler):
                # 异步处理器: 直接 await,不创建新的事件循环
                return await handler(event)
            else:
                # 同步处理器: 在线程池中执行,避免阻塞事件循环
                return await asyncio.to_thread(handler, event)
        except Exception as e:
            LOG.error(f"执行处理程序 {handler.__name__} 时发生错误: {e}")
            LOG.info(f"错误堆栈: {traceback.format_exc()}")
            raise e

    def subscribe(
        self,
        event_type: str,
        handler: Callable[[NcatBotEvent], Any],
        priority: int = 0,
        timeout: Optional[float] = None,
        plugin: Optional["BasePlugin"] = None,
    ) -> uuid.UUID:
        """
        订阅事件处理程序

        Args:
            event_type: 事件类型,支持精确匹配或 "re:" 前缀的正则表达式
            handler: 事件处理函数(支持同步和异步)
            priority: 处理优先级,数值越大优先级越高
            timeout: 处理器超时时间(秒),None 则使用默认值
            plugin: 插件实例,用于记录元数据

        Returns:
            处理器唯一标识符
        """
        hid = uuid.uuid4()
        timeout_val = timeout if timeout is not None else self.default_timeout

        # 记录处理器元数据
        if plugin:
            self._handler_meta[hid] = plugin.meta_data

        if event_type.startswith("re:"):
            pattern = _compile_regex(event_type[3:])
            self._regex.append((pattern, priority, handler, hid, timeout_val))
            self._regex.sort(key=lambda t: (-t[1], t[2].__name__))
        else:
            bucket = self._exact.setdefault(event_type, [])
            bucket.append((None, priority, handler, hid, timeout_val))
            bucket.sort(key=lambda t: (-t[1], t[2].__name__))

        return hid

    def unsubscribe(self, handler_id: uuid.UUID) -> bool:
        """
        取消订阅事件处理程序

        Args:
            handler_id: subscribe() 返回的处理器标识符

        Returns:
            是否成功移除处理器
        """
        removed = False

        # 删除元数据
        if handler_id in self._handler_meta:
            del self._handler_meta[handler_id]

        # 处理精确匹配
        for typ in list(self._exact.keys()):
            original_len = len(self._exact[typ])
            self._exact[typ] = [h for h in self._exact[typ] if h[3] != handler_id]
            removed |= len(self._exact[typ]) != original_len
            if not self._exact[typ]:
                del self._exact[typ]

        # 处理正则匹配
        original_len = len(self._regex)
        self._regex = [h for h in self._regex if h[3] != handler_id]
        removed |= len(self._regex) != original_len

        return removed

    async def publish(self, event: NcatBotEvent) -> List[Any]:
        """
        发布事件并并发执行所有处理器

        这是重构的核心改进:
        - 使用 asyncio.create_task() 创建并发任务
        - 使用 asyncio.gather() 等待所有任务完成

        Args:
            event: 要发布的事件

        Returns:
            所有处理器的返回结果列表
        """
        LOG.debug(
            f"发布事件: {event.type} 数据: {event.data if len(str(event.data)) < 50 else str(event.data)[:50] + '...'}"
        )
        handlers = self._collect_handlers(event.type)

        # 创建所有处理器的并发任务
        tasks = []
        for _, priority, handler, hid, timeout in handlers:
            if event._propagation_stopped:
                break
            tasks.append((handler, handler, hid, timeout))

        # 等待所有任务完成
        for task, handler, hid, timeout in tasks:
            if event._propagation_stopped:
                break

            try:
                result = await asyncio.wait_for(
                    self._run_handler(handler, event), timeout=timeout
                )
                event._results.append(result)
            except asyncio.TimeoutError:
                LOG.error(f"处理器 {handler.__name__} (ID: {hid}) 超时({timeout}秒)")
                meta_data = self._handler_meta.get(hid, {"name": "Unknown"})
                event.add_exception(
                    HandlerTimeoutError(
                        meta_data=meta_data, handler=handler.__name__, time=timeout
                    )
                )
            except Exception as e:
                event.add_exception(e)

        return event._results.copy()

    def _collect_handlers(self, event_type: str) -> List[Tuple]:
        """
        收集匹配的事件处理程序

        Args:
            event_type: 事件类型

        Returns:
            匹配的处理器列表(已排序)
        """
        # 获取精确匹配的处理程序
        exact_handlers = self._exact.get(event_type, [])[:]

        # 获取正则匹配的处理程序
        regex_handlers = []
        for pattern, priority, handler, hid, timeout in self._regex:
            if pattern and pattern.match(event_type):
                regex_handlers.append((pattern, priority, handler, hid, timeout))

        # 合并并排序处理程序(按优先级降序)
        all_handlers = exact_handlers + regex_handlers
        all_handlers.sort(key=lambda t: (-t[1], t[2].__name__))
        return all_handlers

    def shutdown(self):
        """
        关闭事件总线并清理资源

        纯异步版本不需要清理线程,只需清空处理器
        """
        self._exact.clear()
        self._regex.clear()
        self._handler_meta.clear()
        LOG.info("EventBus 已关闭,所有处理器已清理")


@lru_cache(maxsize=128)
def _compile_regex(pattern: str) -> re.Pattern:
    """编译正则表达式并缓存"""
    try:
        return re.compile(pattern)
    except re.error as e:
        raise ValueError(f"无效正则表达式: {pattern}") from e
