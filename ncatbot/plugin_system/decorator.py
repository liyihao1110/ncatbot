# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-05-15 19:12:16
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-08-04 15:26:29
# @Description  : IPluginApi用于显示声明动态添加的属性
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议 
# -------------------------
from functools import wraps
from typing import Protocol, Callable, List, ClassVar, TYPE_CHECKING
if TYPE_CHECKING:
    from .base_plugin import BasePlugin
    from .event.event_bus import EventBus, NcatBotEvent


class CompatibleHandler(Protocol):  # 我觉得应该改个名字
    """兼容性处理器协议"""
    _subclasses: ClassVar[List["CompatibleHandler"]] = []

    def __init__(self, attr_name: str) -> None:
        self.attr_name = attr_name

    @staticmethod
    def check(func: Callable) -> bool: ...
    @staticmethod
    def handle(plugin: 'BasePlugin', func: Callable, event_bus: 'EventBus') -> None: ...

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        if cls is not CompatibleHandler:
            CompatibleHandler._subclasses.append(cls)



def register_server(addr: str) -> Callable:
    '''注册服务到指定地址'''
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, event: 'NcatBotEvent'):
            result = func(self, event.data)
            event.add_result(result)
        if tag := getattr(wrapper ,"_tag", None):
            tag["server"] = addr
            wrapper._tag = tag
        else:
            wrapper._tag = {"server": addr}
        return wrapper
    return decorator

class RegisterServer(CompatibleHandler):
    servers = {}
    @staticmethod
    def check(func: Callable) -> bool:
        if tag := getattr(func, "_tag", None):
            if "server" in tag:
                return True
        return False
    
    @staticmethod
    def handle(plugin: 'BasePlugin', func: Callable, event_bus: 'EventBus') -> None:
        addr = func._tag["server"]
        if addr in RegisterServer.servers:
            raise RuntimeError(f"服务地址已经存在: {addr}")
        id = plugin.register_handler(f"SERVER-{addr}", func)
        RegisterServer.servers[addr] = id


def register_handler(event_type: str, priority: int = 0, get_event: bool = True) -> Callable:
    '''注册事件处理器'''
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, event: 'NcatBotEvent'):
            if get_event:
                func(self, event)
            else:
                result = func(self, event.data)
                event.add_result(result)
        if tag := getattr(wrapper ,"_tag", None):
            tag["handler"] = {'type': event_type, 'priority': priority}
            wrapper._tag = tag
        else:
            wrapper._tag = {'type': event_type, 'priority': priority}
        return wrapper
    return decorator

class RegisterHandler(CompatibleHandler):

    @staticmethod
    def check(func: Callable) -> bool:
        if tag := getattr(func, "_tag", None):
            if "handler" in tag:
                return True
        return False
    
    @staticmethod
    def handle(plugin: 'BasePlugin', func: Callable, event_bus: 'EventBus') -> None:
        tag = func._tag["handler"]
        plugin.register_handler(tag['type'], func, tag['priority'])