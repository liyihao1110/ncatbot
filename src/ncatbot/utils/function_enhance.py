import asyncio
import inspect
import traceback
from functools import wraps
from typing import Type, TypeVar

from ncatbot.utils.assets import REQUEST_SUCCESS
from ncatbot.utils.config import config
from ncatbot.utils.logger import get_log

T = TypeVar("T")
_log = get_log()


async def run_func_async(func, *args, **kwargs):
    # 异步运行异步或者同步的函数
    try:
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            if config.__dict__.get("blocking_sync", False):
                return func(*args, **kwargs)
            else:
                import threading

                threading.Thread(
                    target=func, args=args, kwargs=kwargs, daemon=True
                ).start()
    except Exception as e:
        _log.error(f"函数 {func.__name__} 执行失败: {e}")
        traceback.print_exc()


def run_func_sync(func, *args, **kwargs):
    if inspect.iscoroutinefunction(func):
        # 同步运行一个异步或者同步的函数
        try:
            from threading import Thread

            loop = asyncio.get_running_loop()
            result = []

            def task():
                result.append(asyncio.run(func(*args, **kwargs)))

            t = Thread(target=task, daemon=True)
            t.start()
            t.join(timeout=5)
            if len(result) == 0:
                raise TimeoutError("异步函数执行超时")
            else:
                return result[0]
        except RuntimeError:
            pass
        try:
            loop = asyncio.new_event_loop()  # 创建一个新的事件循环
            asyncio.set_event_loop(loop)  # 设置为当前线程的事件循环
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()  # 关闭事件循环
    else:
        return func(*args, **kwargs)


def to_sync(func):
    return lambda *args, **kwargs: run_func_sync(func, *args, **kwargs)


def to_async(func):
    return lambda *args, **kwargs: run_func_async(func)(*args, **kwargs)


def report(func):
    def check_and_log(result):
        if result.get("status", None) == REQUEST_SUCCESS:
            _log.debug(result)
        else:
            _log.warning(result)
        return result

    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        return check_and_log(result)

    return wrapper


def add_sync_methods(cls: Type[T]) -> Type[T]:
    """
    类装饰器：为类动态添加同步版本的方法
    """

    def async_to_sync(async_func):
        """
        装饰器：将异步函数转换为同步函数
        """

        @wraps(async_func)  # 保留原始函数的文档信息
        def sync_func(*args, **kwargs):
            return to_sync(async_func)(*args, **kwargs)

        return sync_func

    for name, method in inspect.getmembers(cls, predicate=inspect.iscoroutinefunction):
        if name.startswith("_"):  # 跳过私有方法
            continue
        sync_method_name = f"{name}_sync"

        # 获取原始方法的签名
        signature = inspect.signature(method)
        # 生成同步方法的文档字符串
        doc = f"""
        同步版本的 {method.__name__}
        {method.__doc__}
        """

        # 动态生成同步方法
        sync_method = async_to_sync(method)
        sync_method.__signature__ = signature  # 设置方法签名
        sync_method.__doc__ = doc  # 设置文档字符串

        setattr(cls, sync_method_name, sync_method)
    return cls
