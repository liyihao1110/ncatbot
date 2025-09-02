# 过滤器注册插件实现

# 导入基础模块
from ncatbot.core.event.event_data import BaseEventData
from ncatbot.plugin_system.base_plugin import BasePlugin
from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from typing import Dict, Callable, Optional, List, Union, TYPE_CHECKING
from ncatbot.core.event import BaseMessageEvent, Text, MessageSegment
from ncatbot.plugin_system.event.event import NcatBotEvent
from ncatbot.utils import get_log
import copy
import inspect
import asyncio

# 导入子模块
from .filters import BaseFilter
from .command import filter, register, CommandGroup
from .analyzer import FuncAnalyser

LOG = get_log(__name__)

# filter 全部存在 func.__filter__ 里


class FilterRegistryPlugin(NcatBotPlugin):
    """过滤器注册插件
    
    提供命令注册、过滤器管理和事件处理功能。
    """
    
    name = "FilterRegistryPlugin"
    author = "huan-yp"
    desc = "过滤器注册插件"
    version = "1.0.0"
    
    async def on_load(self) -> None:
        """插件加载时的初始化"""
        self.event_bus.subscribe("re:ncatbot.group_message_event|ncatbot.private_message_event", self.do_command, timeout=900)
        self.event_bus.subscribe("re:ncatbot.notice_event|ncatbot.request_event", self.do_legacy_command, timeout=900)
        self.func_plugin_map: Dict[Callable, NcatBotPlugin] = {}
        self.max_length = 0
        return await super().on_load()
    
    def initialize(self):
        """初始化命令映射和验证"""
        def check_prefix(command: Union[str, tuple[str, ...]], func: Callable) -> bool:
            """检查命令前缀冲突"""
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
            """构建命令映射表"""
            self.command_group_map[current_node.build_path("")[:-1]] = current_node
            for command in current_node.command_map.keys():
                path = current_node.build_path(command)
                func = current_node.command_map[command]
                check_prefix(path, func)
                self.max_length = max(self.max_length, len(command))
                self.command_map[path] = func
                if hasattr(current_node.command_map[command], "__alias__"):
                    for alias in current_node.command_map[command].__alias__:
                        check_prefix(alias, func)
                        self.alias_map[(alias, )] = func
            for child in current_node.children:
                build_command_map(child)
        
        def validate_func(func: Callable):
            """验证函数签名"""
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

        if getattr(self, "initialized", False):
            return
        self.initialized = True
        self.alias_map: Dict[str, Callable] = {}
        self.command_map: Dict[tuple[str, ...], Callable] = {}
        self.command_group_map: Dict[tuple[str, ...], CommandGroup] = {}
        build_command_map(register)    
    
        for normal_func in register.filter_functions:
            validate_func(normal_func)
    
    def clear(self):
        """清理初始化状态"""
        self.initialized = False
    
    def find_plugin(self, func: Callable) -> NcatBotPlugin:
        """查找函数所属的插件"""
        plugins = self.list_plugins(obj=True)
        for plugin in plugins:
            # 获取对象的最终类
            plugin_class = plugin.__class__
            # 检查类方法是否存在于这个对象的最终类中
            class_methods = [
                value for name, value in inspect.getmembers(plugin_class, predicate=inspect.isfunction)
            ]
            # 直接检查函数是否在类方法列表中
            if func in class_methods:
                return plugin
        return None
    
    async def run_func(self, func: Callable, *args, **kwargs):
        """运行函数并应用过滤器"""
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
        """处理通知和请求事件"""
        data: BaseEventData = data.data
        if data.post_type == "notice":
            for func in filter.registered_notice_commands:
                self.run_func(func, data)
        else:
            for func in filter.registered_request_commands:
                self.run_func(func, data)
    
    async def do_command(self, data: NcatBotEvent) -> bool:
        """处理消息命令"""
        def build_activator(texts: list[str]) -> tuple[tuple[str, ...], ...]:
            activators = []
            for i in range(len(texts)):
                activators.append(tuple(texts[:i+1]))
            return activators
            
        data: BaseMessageEvent = data.data
        self.initialize()
        if len(data.message.filter_text()) == 0:
            return 
        if data.message.messages[0].msg_seg_type != "text":
            return
        activators = build_activator(data.message.messages[0].text.split(" "))
        for activator in activators:
            if activator in self.command_map:
                func = self.command_map[activator]
                success, args = FuncAnalyser(func, ignore=activator).convert_args(data)
                if success:
                    return await self.run_func(func, data, *args)
            if activator in self.alias_map:
                func = self.alias_map[activator]
                success, args = FuncAnalyser(func, ignore=activator).convert_args(data)
                if success:
                    return await self.run_func(func, data, *args)
        for func in filter.filter_functions:
            await self.run_func(func, data)
