from ncatbot.core.event.event_data import BaseEventData
from ncatbot.plugin_system.base_plugin import BasePlugin
from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from typing import Dict, Callable, Optional, List, Union, TYPE_CHECKING
from ncatbot.core.event import BaseMessageEvent, Text, MessageSegment
from ncatbot.plugin_system.event.event import NcatBotEvent
from ncatbot.utils import OFFICIAL_GROUP_MESSAGE_EVENT, OFFICIAL_PRIVATE_MESSAGE_EVENT
from abc import ABC, abstractmethod
from ncatbot.utils import get_log
import copy
import inspect
import asyncio

LOG = get_log(__name__)

# filter 全部存在 func.__filter__ 里

def get_subclass_recursive(cls: type) -> List[type]:
    return [cls] + [subcls for subcls in cls.__subclasses__() for subcls in get_subclass_recursive(subcls)]

class BaseFilter:
    @abstractmethod
    def check(self, manager: "FilterRegistryPlugin", event: BaseMessageEvent) -> bool:
        pass

class CustomFilter(BaseFilter):
    def __init__(self, func: Callable[..., bool]):
        self.func = func
        
    def check(self, manager: "FilterRegistryPlugin", event: BaseMessageEvent) -> bool:
        pass

class GroupFilter(BaseFilter):
    def check(self, manager: "FilterRegistryPlugin", event: BaseMessageEvent) -> bool:
        return event.is_group_msg()
    
class PrivateFilter(BaseFilter):
    def check(self, manager: "FilterRegistryPlugin", event: BaseMessageEvent) -> bool:
        return not event.is_group_msg()

class AdminFilter(BaseFilter):
    def check(self, manager: "FilterRegistryPlugin", event: BaseMessageEvent) -> bool:
        return manager.rbac_manager.user_has_role(event.user_id, "admin") or manager.rbac_manager.user_has_role(event.user_id, "root")
    
class RootFilter(BaseFilter):
    def check(self, manager: "FilterRegistryPlugin", event: BaseMessageEvent) -> bool:
        return manager.rbac_manager.user_has_role(event.user_id, "root")

class CommandGroup:
    # TODO: 精细权限控制
    def __init__(self, parent: "CommandGroup"=None, name: str=None):
        self.parent: "CommandGroup"  = parent
        self.command_map: Dict[str, Callable] = {}
        self.command_group_map: Dict[str, "CommandGroup"] = {}
        self.children: List["CommandGroup"] = []
        self.name = name

    def command(self, name: str, alias: List[str]=None):
        # alias: 直接别名, 跳过中间的一大堆 command_group
        def decorator(func: Callable):
            self.command_map[name] = func
            setattr(func, "__alias__", alias)
            return func
        return decorator
    
    def command_group(self, name: str):
        command_group = CommandGroup(self, name)
        self.children.append(command_group)
        return command_group
    
    def build_path(self, command_name) -> tuple[str, ...]:
        if self.parent is None:
            return (command_name,)
        return self.parent.build_path(command_name) + (command_name,)


class FilterRegistry(CommandGroup):
    def __init__(self):
        super().__init__()
        self.registered_commands: set(Callable) = set()
        self.registered_notice_commands: set(Callable) = set()
        self.registered_request_commands: set(Callable) = set()
    
    def admin_only(self):
        # 权限大于等于管理员
        def decorator(func: Callable):
            self.registered_commands.add(func)
            if not hasattr(func, "__filter__"):
                setattr(func, "__filter__", [])
            getattr(func, "__filter__").append(AdminFilter())
            return func
        return decorator
    
    def root_only(self):
        def decorator(func: Callable):
            self.registered_commands.add(func)
            if not hasattr(func, "__filter__"):
                setattr(func, "__filter__", [])
            getattr(func, "__filter__").append(RootFilter())
            return func
        return decorator
    
    def group_message(self):
        def decorator(func: Callable):
            self.registered_commands.add(func)
            if not hasattr(func, "__filter__"):
                setattr(func, "__filter__", [])
            getattr(func, "__filter__").append(GroupFilter())
            return func
        return decorator
    
    def private_message(self):
        def decorator(func: Callable):
            self.registered_commands.add(func)
            if not hasattr(func, "__filter__"):
                setattr(func, "__filter__", [])
            getattr(func, "__filter__").append(PrivateFilter())
            return func
        return decorator

    def notice_event(self):
        def decorator(func: Callable):
            self.registered_notice_commands.add(func)
            return func
        return decorator
    
    def request_event(self):
        def decorator(func: Callable):
            self.registered_request_commands.add(func)
            return func
        return decorator
    
    private_event = private_message
    group_event = group_message
    

class FuncAnalyser:
    def __init__(self, func: Callable):
        self.func = func
        self.alias = getattr(func, "__alias__", [])
        
        # 生成 metadata 以便代码更易于理解
        self.func_name = func.__name__
        self.func_module = func.__module__
        self.func_qualname = func.__qualname__
        self.signature = inspect.signature(func)
        self.param_list = list(self.signature.parameters.values())
        self.param_names = [param.name for param in self.param_list]
        self.param_annotations = [param.annotation for param in self.param_list]
        
        # 验证函数签名
        self._validate_signature()
    
    def _validate_signature(self):
        """验证函数签名是否符合要求"""
        if len(self.param_list) < 2:
            LOG.error(f"函数参数不足: {self.func_qualname} 需要至少两个参数")
            LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
            raise ValueError(f"函数参数不足: {self.func_qualname} 需要至少两个参数")
        
        # 检查第一个参数名必须是 self
        first_param = self.param_list[0]
        if first_param.name != "self":
            LOG.error(f"第一个参数名必须是 'self': {self.func_qualname} 的第一个参数是 '{first_param.name}'")
            LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
            raise ValueError(f"第一个参数名必须是 'self': {self.func_qualname} 的第一个参数是 '{first_param.name}'")
        
        # 检查第二个参数必须被注解为 BaseMessageEvent 的子类
        second_param = self.param_list[1]
        if second_param.annotation == inspect.Parameter.empty:
            LOG.error(f"第二个参数缺少类型注解: {self.func_qualname} 的参数 '{second_param.name}' 需要 BaseMessageEvent 或其子类注解")
            LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
            raise ValueError(f"第二个参数缺少类型注解: {self.func_qualname} 的参数 '{second_param.name}' 需要 BaseMessageEvent 或其子类注解")
        
        # 检查第二个参数是否为 BaseMessageEvent 或其子类
        from ncatbot.core.event import BaseMessageEvent
        if not (isinstance(second_param.annotation, type) and issubclass(second_param.annotation, BaseMessageEvent)):
            LOG.error(f"第二个参数类型注解错误: {self.func_qualname} 的参数 '{second_param.name}' 注解为 {second_param.annotation}，需要 BaseMessageEvent 或其子类")
            LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
            raise ValueError(f"第二个参数类型注解错误: {self.func_qualname} 的参数 '{second_param.name}' 注解为 {second_param.annotation}，需要 BaseMessageEvent 或其子类")
    
    def build_help_info(self) -> str:
        # 生成一行帮助
        pass
    
    def detect_args_type(self) -> list[type]:
        # 探测参数表类型, 跳过第一二个参数, 其余参数如果没写注解直接报错
        # 前两个参数的验证已经在 _validate_signature 中完成
        param_list = self.param_list[2:]  # 跳过前两个参数
        args_types = []
        
        for param in param_list:
            annotation = param.annotation
            # 检查是否有注解
            if annotation == inspect.Parameter.empty:
                LOG.error(f"函数参数缺少类型注解: {self.func_qualname} 的参数 '{param.name}' 缺少类型注解")
                LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
                raise ValueError(f"函数参数缺少类型注解: {self.func_qualname} 的参数 '{param.name}' 缺少类型注解")
            
            # 检查注解是否为支持的类型
            if annotation in (str, int, float, bool):
                args_types.append(annotation)
            elif isinstance(annotation, type) and issubclass(annotation, MessageSegment):
                args_types.append(annotation)
            else:
                LOG.error(f"函数参数类型不支持: {self.func_qualname} 的参数 '{param.name}' 的类型注解 {annotation} 不支持")
                LOG.info(f"函数来自 {self.func_module}.{self.func_qualname}")
                LOG.info(f"支持的类型: str, int, float, bool 或 MessageSegment 的子类")
                raise ValueError(f"函数参数类型不支持: {self.func_qualname} 的参数 '{param.name}' 的类型注解 {annotation} 不支持，"
                               f"支持的类型: str, int, float, bool 或 MessageSegment 的子类")
        
        return args_types
    
    def convert_args(self, event: BaseMessageEvent) -> tuple[tuple[...], bool]: # 将事件中的参数转换为函数参数
        # 需要保证参数类型正确, 否则异常
        args_type = self.detect_args_type()
        args_list = []
        cur_index = 0
        def add_arg(arg: Union[str, MessageSegment]):
            if cur_index >= len(args_type):
                return False
            if args_type[cur_index] in (str, int, float, bool):
                args_list.append(args_type[cur_index](arg))
                cur_index += 1
            elif issubclass(args_type[cur_index], MessageSegment):
                args_list.append(arg)
                cur_index += 1
            return True
            
        for arg in event.message.messages:            
            if isinstance(arg, Text):
                cur_str_list = arg.text.split(" ")
                for str in cur_str_list:
                    if not add_arg(str):
                        return (False, args_list)
            else:
                if not add_arg(arg):
                    return (False, args_list)
        return (True, tuple(args_list))

filter = FilterRegistry()
register = filter

class FilterRegistryPlugin(NcatBotPlugin):
    name = "FilterRegistryPlugin"
    author = "huan-yp"
    desc = "过滤器注册插件"
    version = "1.0.0"
    async def on_load(self) -> None:
        self.event_bus.subscribe("re:ncatbot.group_message_event|ncatbot.private_message_event", self.do_command, timeout=900)
        self.event_bus.subscribe("re:ncatbot.notice_event|ncatbot.request_event", self.do_legacy_command, timeout=900)
        self.func_plugin_map: Dict[Callable, NcatBotPlugin] = {}
        self.max_length = 0
        return await super().on_load()
    
    def initialize(self):
        def check_prefix(command: Union[str, tuple[str, ...]]) -> bool:
            def is_prefix(command1: Union[str, tuple[str, ...]], command2: Union[str, tuple[str, ...]]) -> bool:
                if isinstance(command1, str):
                    command1 = (command1,)
                if isinstance(command2, str):
                    command2 = (command2,)
                for i in range(len(command1)):
                    if command1[i] != command2[i]:
                        return False
                return True
            
            for other_command in self.command_map.keys():
                if is_prefix(command, other_command) or is_prefix(other_command, command):
                    LOG.error(f"已注册命令 {other_command} 是 {command} 的前缀")
                    LOG.info(f"{other_command} 来自 {self.command_map[other_command].__module__}.{self.command_map[other_command].__qualname__}")
                    LOG.info(f"{command} 来自 {func.__module__}.{func.__qualname__}")
                    raise ValueError(f"已注册命令 {other_command} 是 {command} 的前缀")
            for alias in self.alias_map.keys():
                if is_prefix(command, alias) or is_prefix(alias, command):
                    LOG.error(f"已注册别名 {alias} 是 {command} 的前缀")
                    LOG.info(f"{alias} 来自 {self.alias_map[alias].__module__}.{self.alias_map[alias].__qualname__}")
                    LOG.info(f"{command} 来自 {func.__module__}.{func.__qualname__}")
                    raise ValueError(f"已注册别名 {alias} 是 {command} 的前缀")
        
        def build_command_map(current_node: CommandGroup):
            self.command_group_map[current_node.build_path("")[:-1]] = current_node
            for command in current_node.command_map.keys():
                self.command_map[current_node.build_path(command)] = current_node.command_map[command]
            for child in current_node.children:
                build_command_map(child)
        
        if getattr(self, "initialized", False):
            return
        self.initialized = True
        self.alias_map: Dict[str, Callable] = {}
        self.command_map: Dict[tuple[str, ...], Callable] = {}
        self.command_group_map: Dict[tuple[str, ...], CommandGroup] = {}
        build_command_map(register)
        
        
        from ncatbot.plugin_system.loader import _iter_callables
        for func in _iter_callables(self):
            if hasattr(func, "__alias__"):
                for alias in func.__alias__:
                    check_prefix(alias)
                    self.alias_map[alias] = func
        
        for command in self.command_map.keys():
            self.max_length = max(self.max_length, len(command))
            check_prefix(command)
    
        for normal_func in register.registered_commands:
            def validate_func(func: Callable):
                sig = inspect.signature(func)
                if len(sig.parameters) != 2:
                    LOG.error(f"函数 {func.__name__} 的参数数量不正确")
                    LOG.info(f"函数来自 {func.__module__}.{func.__qualname__}")
                    raise ValueError(f"函数 {func.__name__} 的参数数量不正确")
                if list(sig.parameters.values())[0].name != "self":
                    LOG.error(f"函数 {func.__name__} 的参数名不正确")
                    LOG.info(f"函数来自 {func.__module__}.{func.__qualname__}")
                    raise ValueError(f"函数 {func.__name__} 的参数名不正确, 应该为 self")
                if not issubclass(list(sig.parameters.values())[1].annotation, BaseMessageEvent):
                    LOG.error(f"函数 {func.__name__} 的参数类型不正确")
                    LOG.info(f"函数来自 {func.__module__}.{func.__qualname__}")
                    raise ValueError(f"函数 {func.__name__} 的参数类型不正确, 应该为 BaseMessageEvent")
            validate_func(normal_func)
    
    
    def clear(self):
        self.initialized = False
    
    def find_plugin(self, func: Callable) -> NcatBotPlugin:
        plugins = self.list_plugins(obj=True)
        for plugin in plugins:
            if func in plugin.__dict__.values():
                return plugin
        return None
    
    async def run_func(self, func: Callable, *args, **kwargs):
        plugin = self.find_plugin(func)
        filters: List[BaseFilter] = getattr(func, "__filter__", [])
        args = [plugin] + list(args)
        for filter in filters:
            if not filter.check(self, args[1]):
                return False
            
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    
    async def do_legacy_command(self, data: NcatBotEvent) -> bool:
        data: BaseEventData = data.data
        if data.post_type == "notice":
            for func in filter.registered_notice_commands:
                self.run_func(func, data)
        else:
            for func in filter.registered_request_commands:
                self.run_func(func, data)
    
    async def do_command(self, data: NcatBotEvent) -> bool:
        data: BaseMessageEvent = data.data
        self.initialize()
        if len(data.message.filter_text()) == 0:
            return 
        if data.message.messages[0].msg_seg_type != "text":
            return
        activator = data.message.messages[0].text.split(" ")
        for i in range(len(activator)):
            if activator[i] in self.command_map:
                func = self.command_map[activator[i]]
                args, success = FuncAnalyser(func).convert_args(data)
                return await self.run_func(func, data, *args)
            if activator[i] in self.alias_map:
                func = self.alias_map[activator[i]]
                args, success = FuncAnalyser(func).convert_args(data)
                return await self.run_func(func, data, *args)
        for func in filter.registered_commands:
            await self.run_func(func, data)

