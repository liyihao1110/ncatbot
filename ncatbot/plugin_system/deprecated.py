# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-08-05 21:53:12
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-08-05 21:53:23
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议 
# -------------------------

import functools
import warnings


class DeprecatedWarningState:
    def __init__(self):
        self.warned = set()

def deprecated(replacement=None):
    """
    装饰器，用于标记函数或方法为已弃用。
    Args:
        replacement: 可选参数，指定替代函数的名称。
    """
    state = DeprecatedWarningState()

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if func not in state.warned:
                msg = f"{func.__name__} is deprecated"
                if replacement:
                    msg += f", use {replacement} instead"
                warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
                state.warned.add(func)
            return func(*args, **kwargs)
        return wrapper
    return decorator