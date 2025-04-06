# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-21 18:23:06
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-02-21 19:44:14
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @message: 喵喵喵?
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
import inspect
from functools import wraps

from ncatbot.plugin.event import Event
from ncatbot.utils import (
    OFFICIAL_GROUP_MESSAGE_EVENT,
    OFFICIAL_NOTICE_EVENT,
    OFFICIAL_PRIVATE_MESSAGE_EVENT,
    OFFICIAL_REQUEST_EVENT,
)


class CompatibleEnrollment:
    events = {
        OFFICIAL_PRIVATE_MESSAGE_EVENT: [],
        OFFICIAL_GROUP_MESSAGE_EVENT: [],
        OFFICIAL_REQUEST_EVENT: [],
        OFFICIAL_NOTICE_EVENT: [],
    }

    def __init__(self):
        raise ValueError("不需要实例化该类")  # 防止实例化该类

    def event_decorator(event_type):
        """装饰器工厂，生成特定事件类型的装饰器"""

        def decorator_generator(types="all", row_event=False):
            def decorator(func):
                signature = inspect.signature(func)
                in_class = len(signature.parameters) > 1
                if in_class:
                    if row_event:

                        @wraps(func)
                        def wrapper(self, event: Event):
                            return func(self, event)

                    else:

                        @wraps(func)
                        def wrapper(self, event: Event):
                            return func(self, event.data)

                else:
                    if row_event:

                        @wraps(func)
                        def wrapper(event: Event):
                            return func(event)

                    else:

                        @wraps(func)
                        def wrapper(event: Event):
                            return func(event.data)

                CompatibleEnrollment.events[event_type].append(
                    (
                        wrapper,
                        0,
                        in_class,
                    )
                )
                return wrapper

            return decorator

        return decorator_generator

    # 自动生成各个事件类型的装饰器
    group_event = event_decorator(OFFICIAL_GROUP_MESSAGE_EVENT)
    private_event = event_decorator(OFFICIAL_PRIVATE_MESSAGE_EVENT)
    notice_event = event_decorator(OFFICIAL_NOTICE_EVENT)
    request_event = event_decorator(OFFICIAL_REQUEST_EVENT)
