import asyncio
import re
import threading
import uuid
import time
import ctypes
import queue
from queue import Queue
import traceback
from concurrent.futures import Future
from functools import lru_cache
from ncatbot.utils import get_log

# from logging import getLogger
from typing import Any, Callable, Dict, List, Optional, Tuple, TYPE_CHECKING, Set

from ncatbot.utils import run_coroutine

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
    def __init__(self, default_timeout: float = 5, max_workers: int = 2) -> None:
        """
        事件总线实现 - 线程池

        Args:
            default_timeout: 默认处理器超时时间（秒）
            max_workers: 最大工作线程数
        """
        self._exact: Dict[str, List[Tuple]] = {}
        self._regex: List[Tuple] = []
        self._lock = threading.Lock()
        self.default_timeout = default_timeout
        self.max_workers = max_workers

        # 线程池状态
        self.task_queue = queue.Queue()
        self.task_queue: "Queue[Tuple[Callable, Callable, NcatBotEvent, float, asyncio.Queue, uuid.UUID]]"
        self.worker_lock = threading.Lock()
        self._worker_map: dict[int, threading.Thread] = {}
        self.worker_timeouts: Dict[int, float] = {}
        self.active_tasks: Dict[int, Future] = {}

        # 存储处理器元数据
        self._handler_meta: Dict[uuid.UUID, Dict] = {}
        self.result_queues: Dict[uuid.UUID, asyncio.Queue] = {}

        # 初始化工作线程
        for i in range(max_workers):
            self._add_worker(i)

        # 启动监控线程
        self.monitor_thread = threading.Thread(
            target=self._monitor_timeouts, daemon=True
        )
        self.monitor_thread.start()
    
    @property
    def workers(self) -> Set[threading.Thread]:
        """当前存活的工作线程（只读）"""
        with self.worker_lock:
            return {t for t in self._worker_map.values() if t.is_alive()}
    
    def _add_worker(self, worker_id: int) -> bool:
        """创建/复活一个工作线程；成功返回 True"""
        with self.worker_lock:
            old = self._worker_map.get(worker_id)
            if old is not None and old.is_alive():
                return True
            if old is not None:
                self._worker_map.pop(worker_id, None)

            try:
                t = threading.Thread(
                    target=self._worker_loop,
                    args=(worker_id,),
                    daemon=True,
                    name=f"EventBus_Worker-{worker_id}"
                )
                t.start()
                self._worker_map[worker_id] = t
                return True
            except Exception as exc:
                LOG.error(f"无法启动工作线程: {worker_id}: {exc}")
                return False

    def _worker_loop(self, worker_id: int):
        """工作线程"""
        while True:
            try:
                task = self.task_queue.get(timeout=0.1)
                runner, handler, event, timeout, result_queue, hid = task

                thread_id = threading.get_ident()
                start = time.time()
                self.worker_timeouts[thread_id] = start + timeout

                try:
                    result = runner(handler, event)
                    result_queue.put(result)
                except Exception as e:
                    LOG.debug(f"任务 {hid} 执行错误: {e}")
                    result_queue.put(e)
                finally:
                    self.worker_timeouts.pop(thread_id, None)
                    self.task_queue.task_done()
            except queue.Empty:
                # 只有“过剩”线程才退出
                with self.worker_lock:
                    alive = sum(1 for t in self._worker_map.values() if t.is_alive())
                if alive <= self.max_workers:
                    continue
                if alive > int(self.max_workers * 1.5):
                    LOG.debug(f"Worker-{worker_id} 退出, 原因: 线程数超量150%")
                    break

    def _monitor_timeouts(self):
        """监控超时任务并强制终止线程，随后补充新线程"""
        while True:
            time.sleep(self.default_timeout / 4)
            now = time.time()

            with self.worker_lock:
                for wid, worker in list(self._worker_map.items()):
                    tid = worker.ident
                    if tid in self.worker_timeouts and now > self.worker_timeouts[tid]:
                        self._terminate_thread(worker)
                        self._worker_map.pop(wid, None)
                        self._add_worker(wid)          # 补充同 ID 新线程

                        if tid in self.active_tasks:
                            fut = self.active_tasks.pop(tid)
                            if not fut.done():
                                fut.set_exception(TimeoutError("处理器超时"))

    def _terminate_thread(self, thread: threading.Thread):
        """强制终止线程"""
        if not thread.is_alive():
            return

        exc = ctypes.py_object(TimeoutError)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(thread.ident), exc
        )

        if res == 0:
            raise ValueError("无效的线程 ID")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread.ident, None)

    def _run_handler(self, handler: Callable, event: NcatBotEvent) -> Any:
        """
        执行处理程序
        """
        # 如果是异步函数，在独立事件循环中运行
        # LOG.debug(f"执行处理程序: {handler.__name__}")
        try:
            if asyncio.iscoroutinefunction(handler):
                return run_coroutine(handler, event)
            else:
                return handler(event)
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
        """订阅事件处理程序"""
        hid = uuid.uuid4()
        timeout_val = timeout if timeout is not None else self.default_timeout

        # 记录处理器元数据
        if plugin:
            self._handler_meta[hid] = plugin.meta_data

        with self._lock:
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
        """取消订阅事件处理程序"""
        removed = False
        with self._lock:
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
        """发布事件并等待所有处理器完成"""
        handlers = self._collect_handlers(event.type)
        handler_meta = self._handler_meta.copy()

        # 为每个handler提交任务
        for _, _, handler, hid, timeout in handlers:
            if event._propagation_stopped:
                break

            # 为每个任务创建结果队列
            with self._lock:
                if hid in self.result_queues:
                    result_queue = self.result_queues[hid]
                else:
                    result_queue = Queue()
                    self.result_queues[hid] = result_queue
                # 提交任务到线程池
                LOG.debug(f"提交任务到线程池: {handler.__name__}, {hid}")
                self.task_queue.put(
                    (self._run_handler, handler, event, timeout, result_queue, hid)
                )
            try:
                result = result_queue.get(timeout=timeout)
                if isinstance(result, Exception):
                    LOG.error(
                        f"任务 {handler_meta[hid].__name__} {hid} 发生错误: {result}"
                    )
                    if isinstance(result, TimeoutError):
                        event.add_exception(
                            HandlerTimeoutError(
                                meta_data=handler_meta[hid], handler=hid, time=timeout
                            )
                        )
                    else:
                        event.add_exception(result)
                else:
                    event._results.append(result)
            except asyncio.TimeoutError:
                LOG.error(f"任务 {hid} 超时")
                event.add_exception(
                    HandlerTimeoutError(
                        meta_data=handler_meta[hid], handler=hid, time=timeout
                    )
                )
            finally:
                # 清理结果队列
                try:
                    with self._lock:
                        if (
                            hid in self.result_queues
                            and self.result_queues[hid].empty()
                        ):
                            del self.result_queues[hid]
                except Exception as e:
                    LOG.error(f"清理结果队列时发生错误: {e}")
                    LOG.info(traceback.format_exc())

        try:
            for e in event.exceptions:
                LOG.error(str(e))
            # LOG.debug(f"收集结果: {event._results}")
            return event._results.copy()
        except Exception as e:
            LOG.error(f"收集结果时发生错误: {e}")
            LOG.info(traceback.format_exc())
            return []

    def _collect_handlers(self, event_type: str) -> List[Tuple]:
        """收集匹配的事件处理程序"""
        with self._lock:
            # 获取精确匹配的处理程序
            exact_handlers = self._exact.get(event_type, [])[:]

            # 获取正则匹配的处理程序
            regex_handlers = []
            for pattern, priority, handler, hid, timeout in self._regex:
                if pattern and pattern.match(event_type):
                    regex_handlers.append((pattern, priority, handler, hid, timeout))

        # 合并并排序处理程序
        all_handlers = exact_handlers + regex_handlers
        all_handlers.sort(key=lambda t: (-t[1], t[2].__name__))
        return all_handlers

    def shutdown(self):
        """关闭事件总线并清理资源"""
        # 终止所有工作线程
        with self.worker_lock:
            for worker in list(self._worker_map.values()):
                if worker.is_alive():
                    self._terminate_thread(worker)
            self._worker_map.clear()          # 清空映射表

        # 清空任务队列
        while not self.task_queue.empty():
            try:
                self.task_queue.get_nowait()
                self.task_queue.task_done()
            except queue.Empty:
                break


@lru_cache(maxsize=128)
def _compile_regex(pattern: str) -> re.Pattern:
    """编译正则表达式并缓存"""
    try:
        return re.compile(pattern)
    except re.error as e:
        raise ValueError(f"无效正则表达式: {pattern}") from e
