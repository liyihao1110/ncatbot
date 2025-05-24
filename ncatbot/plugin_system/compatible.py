# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-05-24 18:04:18
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-05-24 18:25:12
# @Description  : 此文件用于与不同系统兼容
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议 
# -------------------------
# * 此文件用于与不同系统兼容，同时abc_api.IPluginApi允许你添加一些属性注释(通常是初始化时传入的关键字参数)
# ! 你必须重写此文件
# from typing import Callable, Any, List, Optional, TypeVar
# import inspect
# from functools import wraps

# from .api import CompatibleHandler, COMPATIBLE_HANDLERS
# from .base_plugin import BasePlugin
# from .event.event_bus import EventBus
# from .event import Event
# from ..config import (
#     OFFICIAL_PRIVATE_MESSAGE_EVENT,
#     OFFICIAL_GROUP_MESSAGE_EVENT,
#     OFFICIAL_FRIEND_REQUEST_EVENT,
#     OFFICIAL_GROUP_REQUEST_EVENT,
#     OFFICIAL_NOTICE_EVENT,
#     OFFICIAL_GROUP_COMMAND_EVENT,
#     OFFICIAL_PRIVATE_COMMAND_EVENT,
# )

# # 定义泛型类型变量用于装饰器返回类型
# F = TypeVar("F", bound=Callable[..., Any])

# class CompatibleEnrollment:
#     # 事件类型常量集合
#     event_types = [
#         OFFICIAL_GROUP_MESSAGE_EVENT,
#         OFFICIAL_PRIVATE_MESSAGE_EVENT,
#         OFFICIAL_FRIEND_REQUEST_EVENT,
#         OFFICIAL_GROUP_REQUEST_EVENT,
#         OFFICIAL_NOTICE_EVENT,
#         OFFICIAL_GROUP_COMMAND_EVENT,
#         OFFICIAL_PRIVATE_COMMAND_EVENT,
#     ]

#     def __init__(self):
#         raise ValueError("该类不需要实例化")

#     class _EventDecorator:
#         def __init__(self, event_type: str):
#             self.event_type = event_type

#         def __call__(self, row_event: bool = False) -> Callable[[F], F]:
#             def decorator(func: F) -> F:
#                 signature = inspect.signature(func)
#                 in_class = len(signature.parameters) > 1

#                 @wraps(func)
#                 def wrapper(*args, **kwargs) -> Optional[Any]:
#                     event = args[1] if in_class else args[0]
#                     if row_event:
#                         return func(*args, **kwargs)
#                     else:
#                         if in_class:
#                             return func(args[0], event.data, *args[2:], **kwargs)
#                         else:
#                             return func(event.data, *args[1:], **kwargs)

#                 # 添加元数据用于事件注册
#                 setattr(wrapper, "_compatible_event", {
#                     "event_type": self.event_type,
#                     "priority": 0,
#                     "in_class": in_class,
#                     "row_event": row_event,
#                 })
#                 return wrapper  # type: ignore
#             return decorator

#     class _TriggerDecorator:
#         @staticmethod
#         def keywords(*words: str, policy: str = "any") -> Callable[[F], F]:
#             def decorator(func: F) -> F:
#                 @wraps(func)
#                 def wrapper(*args, **kwargs) -> Optional[Any]:
#                     event = args[-1] if isinstance(args[-1], Event) else None
#                     if not event or not hasattr(event.data, 'message'):
#                         return func(*args, **kwargs)
#                     msg_text = str(event.data.message)
#                     if policy == "any":
#                         if not any(word in msg_text for word in words):
#                             return None
#                     else:
#                         if not all(word in msg_text for word in words):
#                             return None
#                     return func(*args, **kwargs)
                
#                 # 添加触发器元数据
#                 setattr(wrapper, "_compatible_trigger", {
#                     "type": "keywords",
#                     "words": words,
#                     "policy": policy,
#                 })
#                 return wrapper  # type: ignore
#             return decorator

#         @staticmethod
#         def has_elements(*elements: str) -> Callable[[F], F]:
#             def decorator(func: F) -> F:
#                 @wraps(func)
#                 def wrapper(*args, **kwargs) -> Optional[Any]:
#                     event = args[-1] if isinstance(args[-1], Event) else None
#                     if not event or not hasattr(event.data, 'message'):
#                         return func(*args, **kwargs)
#                     msg = event.data.message
#                     if not all(msg.has_type(elem) for elem in elements):
#                         return None
#                     return func(*args, **kwargs)
                
#                 # 添加触发器元数据
#                 setattr(wrapper, "_compatible_trigger", {
#                     "type": "has_elements",
#                     "elements": elements,
#                 })
#                 return wrapper  # type: ignore
#             return decorator

#     # 显式声明类属性类型以提供IDE提示
#     def group_event(self, row_event: bool = False) -> F:
#         """群消息事件装饰器"""
#         return self._EventDecorator(OFFICIAL_GROUP_MESSAGE_EVENT)(row_event)

#     def private_event(self, row_event: bool = False) -> F:
#         """私聊消息事件装饰器"""
#         return self._EventDecorator(OFFICIAL_PRIVATE_MESSAGE_EVENT)(row_event)

#     def notice_event(self, row_event: bool = False) -> F:
#         """通知事件装饰器"""
#         return self._EventDecorator(OFFICIAL_NOTICE_EVENT)(row_event)

#     def group_command(self, row_event: bool = False) -> F:
#         """群命令事件装饰器"""
#         return self._EventDecorator(OFFICIAL_GROUP_COMMAND_EVENT)(row_event)

#     def private_command(self, row_event: bool = False) -> F:
#         """私聊命令事件装饰器"""
#         return self._EventDecorator(OFFICIAL_PRIVATE_COMMAND_EVENT)(row_event)

#     def friend_request(self, row_event: bool = False) -> F:
#         """好友请求事件装饰器"""
#         return self._EventDecorator(OFFICIAL_FRIEND_REQUEST_EVENT)(row_event)

#     def group_request(self, row_event: bool = False) -> F:
#         """群请求事件装饰器"""
#         return self._EventDecorator(OFFICIAL_GROUP_REQUEST_EVENT)(row_event)

#     group_event = _EventDecorator(OFFICIAL_GROUP_MESSAGE_EVENT)
#     private_event = _EventDecorator(OFFICIAL_PRIVATE_MESSAGE_EVENT)
#     notice_event = _EventDecorator(OFFICIAL_NOTICE_EVENT)
#     group_command = _EventDecorator(OFFICIAL_GROUP_COMMAND_EVENT)
#     private_command = _EventDecorator(OFFICIAL_PRIVATE_COMMAND_EVENT)
#     friend_request = _EventDecorator(OFFICIAL_FRIEND_REQUEST_EVENT)
#     group_request = _EventDecorator(OFFICIAL_GROUP_REQUEST_EVENT)
    
#     trigger:_TriggerDecorator = _TriggerDecorator()

# class EventCompatibleHandler(CompatibleHandler):
#     """事件兼容性处理器"""
#     def check(self, obj: Any) -> bool:
#         return hasattr(obj, "_compatible_event")
        
#     def handle(self, plugin: BasePlugin, func: Callable, event_bus: EventBus) -> None:
#         event_info = getattr(func, "_compatible_event")
#         if event_info:
#             if event_info["in_class"]:
#                 bound_func = func.__get__(plugin, plugin.__class__)
#             else:
#                 bound_func = func
                
#             handler_id = event_bus.subscribe(
#                 event_info["event_type"],
#                 bound_func,
#                 event_info.get("priority", 0)
#             )
#             plugin._event_handlers.append(handler_id)

# # 注册所有兼容性处理器
# COMPATIBLE_HANDLERS.extend([
#     EventCompatibleHandler("_compatible_event"),
# ])