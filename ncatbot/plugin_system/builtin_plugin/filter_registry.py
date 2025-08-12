# from ncatbot.plugin_system.base_plugin import BasePlugin
# from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
# from typing import Dict, Callable, Optional, List
# from ncatbot.core.event import MessageEventData
# from ncatbot.plugin_system.loader import _iter_callables
# from ncatbot.utils import OFFICIAL_GROUP_MESSAGE_EVENT, OFFICIAL_PRIVATE_MESSAGE_EVENT
# from abc import ABC, abstractmethod


# # filter 全部存在 func.__filter__ 里
# def get_subclass_recursive(cls: type) -> List[type]:
#     return [cls] + [subcls for subcls in cls.__subclasses__() for subcls in get_subclass_recursive(subcls)]

# class BaseFilter:
#     @abstractmethod
#     def check(self, event: MessageEventData) -> bool:
#         pass

# class CustomFilter(BaseFilter):
#     def __init__(self, func: Callable[..., bool]):
#         self.func = func
        
#     def check(self, event: MessageEventData) -> bool:
#         pass

# class GroupFilter(BaseFilter):
#     def check(self, event: MessageEventData) -> bool:
#         pass
    
# class PrivateFilter(BaseFilter):
#     def check(self, event: MessageEventData) -> bool:
#         pass

# class AdminFilter(BaseFilter):
#     def check(self, event: MessageEventData) -> bool:
#         pass
    
# class RootFilter(BaseFilter):
#     def check(self, event: MessageEventData) -> bool:
#         pass

# class PermissionFilter(BaseFilter):
#     def check(self, event: MessageEventData) -> bool:
#         pass


# class CommandGroup:
#     def __init__(self, parent: "CommandGroup"=None, name: str=None):
#         self.parent: "CommandGroup"  = parent
#         self.command_map: Dict[str, Callable] = {}
#         self.command_group_map: Dict[str, "CommandGroup"] = {}
#         self.children: List["CommandGroup"] = []
#         self.name = name

#     def command(self, name: str, alias: List[str]=None):
#         # alias: 直接别名, 跳过中间的一大堆 command_group
#         def decorator(func: Callable):
#             self.command_map[name] = func
#             setattr(func, "__alias__", alias)
#             return func
#         return decorator
    
#     def command_group(self, name: str):
#         command_group = CommandGroup(self, name)
#         self.children.append(command_group)
#         return command_group

# class FilterRegistry(CommandGroup):
#     def __init__(self):
#         super().__init__()
#         self.registered_commands: set(Callable) = set()
    
#     def admin_only(self):
#         # 权限大于等于管理员
#         def decorator(func: Callable):
#             if not hasattr(func, "__filter__"):
#                 setattr(func, "__filter__", [])
#             getattr(func, "__filter__").append(AdminFilter())
#             return func
#         return decorator
    
#     def root_only(self):
#         def decorator(func: Callable):
#             if not hasattr(func, "__filter__"):
#                 setattr(func, "__filter__", [])
#             getattr(func, "__filter__").append(RootFilter())
#             return func
#         return decorator
    
#     def group_message(self):
#         def decorator(func: Callable):
#             self.registered_commands.add(func)
#             if not hasattr(func, "__filter__"):
#                 setattr(func, "__filter__", [])
#             getattr(func, "__filter__").append(GroupFilter())
#             return func
#         return decorator
    
#     def private_message(self):
#         def decorator(func: Callable):
#             self.registered_commands.add(func)
#             if not hasattr(func, "__filter__"):
#                 setattr(func, "__filter__", [])
#             getattr(func, "__filter__").append(PrivateFilter())
#             return func
#         return decorator

# filter = FilterRegistry()
# register = filter

# class FilterRegistryPlugin(NcatBotPlugin):
#     name = "FilterRegistryPlugin"
#     author = "huan-yp"
#     desc = "过滤器注册插件"
#     ver = "1.0.0"
#     async def on_load(self) -> None:
#         self.event_bus.subscribe(OFFICIAL_GROUP_MESSAGE_EVENT, self.do_command)
#         self.event_bus.subscribe(OFFICIAL_PRIVATE_MESSAGE_EVENT, self.do_command)
#         return await super().on_load()
    
#     def initialize(self):
#         if not hasattr(self, "initialized"):
#             self.initialized = True
#         else:
#             return
#         self.alias_map: Dict[str, Callable] = {}
#         for func in _iter_callables(self):
#             if hasattr(func, "__alias__"):
#                 for alias in func.__alias__:
#                     if alias in self.alias_map:
                        
#                     self.alias_map[alias] = func
    
#     async def do_command(self, data: MessageEventData) -> bool:
#         self.initialize()
#         pass

