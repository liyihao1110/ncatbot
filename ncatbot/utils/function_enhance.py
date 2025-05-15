"""NcatBot 函数增强模块。"""

import asyncio
import functools
import inspect
import time
import traceback
from typing import Any, Callable, TypeVar, cast

from ncatbot.utils.config import ncatbot_config as config
from ncatbot.utils.logger import get_log

T = TypeVar("T", bound=Callable[..., Any])
logger = get_log()

LOG = get_log("FunctionEnhance")


async def run_func_async(func, *args, **kwargs):
    # 异步运行异步或者同步的函数
    try:
        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            if config and config.__dict__.get("blocking_sync", False):
                return func(*args, **kwargs)
            else:
                import threading

                threading.Thread(
                    target=func, args=args, kwargs=kwargs, daemon=True
                ).start()
    except Exception as e:
        logger.error(f"函数 {func.__name__} 执行失败: {e}")
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


def log_execution_time(func: T) -> T:
    """记录函数执行时间的装饰器。

    Args:
        func: 要装饰的函数

    Returns:
        装饰后的函数
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        LOG.debug(f"函数 {func.__name__} 执行时间: {execution_time:.2f} 秒")
        return result

    return cast(T, wrapper)


def retry(max_retries: int = 3, delay: float = 1.0) -> Callable[[T], T]:
    """重试装饰器。

    Args:
        max_retries: 最大重试次数
        delay: 重试延迟（秒）

    Returns:
        装饰器函数
    """

    def decorator(func: T) -> T:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if i < max_retries - 1:
                        LOG.warning(
                            f"函数 {func.__name__} 执行失败，{delay} 秒后重试: {e}"
                        )
                        time.sleep(delay)
            LOG.error(
                f"函数 {func.__name__} 在 {max_retries} 次重试后仍然失败: {last_exception}"
            )
            raise last_exception

        return cast(T, wrapper)

    return decorator


def validate_args(*validators: Callable[[Any], bool]) -> Callable[[T], T]:
    """参数验证装饰器。

    Args:
        *validators: 验证器函数列表

    Returns:
        装饰器函数
    """

    def decorator(func: T) -> T:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            for i, (name, value) in enumerate(bound_args.arguments.items()):
                if i < len(validators):
                    if not validators[i](value):
                        raise ValueError(f"参数 {name} 验证失败")
            return func(*args, **kwargs)

        return cast(T, wrapper)

    return decorator


def cache_result(ttl: float = 300.0) -> Callable[[T], T]:
    """缓存函数结果的装饰器。

    Args:
        ttl: 缓存生存时间（秒）

    Returns:
        装饰器函数
    """
    cache: dict[str, tuple[float, Any]] = {}

    def decorator(func: T) -> T:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            now = time.time()

            if key in cache:
                timestamp, result = cache[key]
                if now - timestamp < ttl:
                    return result

            result = func(*args, **kwargs)
            cache[key] = (now, result)
            return result

        return cast(T, wrapper)

    return decorator


def async_retry(max_retries: int = 3, delay: float = 1.0) -> Callable[[T], T]:
    """异步重试装饰器。

    Args:
        max_retries: 最大重试次数
        delay: 重试延迟（秒）

    Returns:
        装饰器函数
    """

    def decorator(func: T) -> T:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            for i in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if i < max_retries - 1:
                        LOG.warning(
                            f"异步函数 {func.__name__} 执行失败，{delay} 秒后重试: {e}"
                        )
                        await asyncio.sleep(delay)
            LOG.error(
                f"异步函数 {func.__name__} 在 {max_retries} 次重试后仍然失败: {last_exception}"
            )
            raise last_exception

        return cast(T, wrapper)

    return decorator
