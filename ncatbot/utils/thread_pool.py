import threading
import queue
import time
import os
from concurrent.futures import Future
from typing import Callable, Any, Dict
import inspect
import asyncio
import traceback

class ThreadPool:
    """
    线程池实现类，支持提交同步和异步任务，并对相同函数的任务进行并发限制
    """
    
    def __init__(self, max_workers: int = None, max_per_func: int = None):
        """
        初始化线程池
        
        :param max_workers: 最大工作线程数，默认为CPU核心数*5
        :param max_per_func: 每个函数的最大并发数，默认为max_workers的1/4
        """
        # 如果未指定最大工作线程数，则设置为CPU核心数*5
        if max_workers is None:
            max_workers = 5 * (os.cpu_count() or 1)
        
        self.max_workers = max_workers  # 最大线程数
        self.task_queue = queue.Queue()  # 任务队列
        self.workers = []  # 工作线程列表
        self.shutdown_flag = False  # 关闭标志
        
        # 函数跟踪字典
        self.func_tracker: Dict[Callable, int] = {}  # 记录每个函数的当前执行数
        self.func_lock = threading.Lock()  # 保护func_tracker的锁
        
        # 设置每个函数的最大并发数
        self.max_per_func = max_per_func if max_per_func is not None else max(1, max_workers // 4)
        
        # 创建并启动工作线程
        for _ in range(max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def _can_execute_func(self, func: Callable) -> bool:
        """检查是否可以执行该函数（未达到并发限制）"""
        if self.max_per_func <= 0:
            return True
            
        with self.func_lock:
            current = self.func_tracker.get(func, 0)
            return current < self.max_per_func
    
    def _increment_func_counter(self, func: Callable):
        """增加函数计数器"""
        if self.max_per_func <= 0:
            return
            
        with self.func_lock:
            self.func_tracker[func] = self.func_tracker.get(func, 0) + 1
    
    def _decrement_func_counter(self, func: Callable):
        """减少函数计数器"""
        if self.max_per_func <= 0:
            return
            
        with self.func_lock:
            if func in self.func_tracker:
                self.func_tracker[func] -= 1
                if self.func_tracker[func] <= 0:
                    del self.func_tracker[func]
    
    def _worker_loop(self):
        """
        工作线程的主循环，不断从任务队列中获取并执行任务
        """
        while True:
            # 如果设置了关闭标志且队列为空，则退出循环
            if self.shutdown_flag and self.task_queue.empty():
                break
                
            try:
                # 从队列中获取任务（阻塞式，最多等待1秒）
                task = self.task_queue.get(block=True, timeout=1)
                func, future, args, kwargs = task
                # 检查函数是否达到并发限制
                if not self._can_execute_func(func):
                    # 如果达到限制，将任务重新放回队列
                    self.task_queue.put(task)
                    time.sleep(0.1)  # 避免忙等待
                    continue
                
                # 增加函数计数器
                self._increment_func_counter(func)
                
                try:
                    # 执行函数并设置结果
                    if inspect.iscoroutinefunction(func):
                        result = asyncio.run(func(*args, **kwargs))
                    else:
                        result = func(*args, **kwargs)
                    future.set_result(result)
                except Exception as e:
                    print(e)
                    traceback.print_exc()
                    # 如果执行出错，设置异常
                    future.set_exception(e)
                finally:
                    # 减少函数计数器
                    self._decrement_func_counter(func)
                    # 标记任务完成
                    self.task_queue.task_done()
            except queue.Empty:
                # 队列为空时继续循环
                continue
    
    def submit(self, func: Callable, *args, **kwargs) -> Future:
        """
        提交一个任务到线程池（异步执行）
        
        :param func: 要执行的函数
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: Future对象，可用于获取结果
        """
        if self.shutdown_flag:
            raise RuntimeError("线程池已关闭，不能提交新任务")
            
        # 创建Future对象用于返回结果
        future = Future()
        # 将任务放入队列
        self.task_queue.put((func, future, args, kwargs))
        return future
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        提交并同步执行一个任务（阻塞直到返回结果）
        
        :param func: 要执行的函数
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 函数执行结果
        """
        future = self.submit(func, *args, **kwargs)
        return future.result()  # 阻塞直到获取结果
    
    def shutdown(self, wait: bool = True):
        """
        关闭线程池
        
        :param wait: 是否等待所有任务完成
        """
        self.shutdown_flag = True
        
        if wait:
            # 等待所有任务完成
            self.task_queue.join()
        
        # 等待所有工作线程结束
        for worker in self.workers:
            worker.join()
    
    def __enter__(self):
        """支持with语句"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出with语句时自动关闭线程池"""
        self.shutdown(wait=True)