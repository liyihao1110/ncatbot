"""过滤器注册模块"""

from typing import Callable, List, Set
from .group import CommandGroup
from ..filters import (
    AdminFilter, RootFilter, GroupFilter, PrivateFilter, 
    CustomFilter, CustomFilterFunc
)
from ncatbot.utils import get_log

LOG = get_log(__name__)


class FilterRegistry(CommandGroup):
    """过滤器注册类
    
    继承自 CommandGroup，提供装饰器形式的过滤器注册功能。
    支持权限过滤、消息类型过滤、事件类型过滤和自定义过滤器。
    """
    
    def __init__(self):
        super().__init__(None, "filter_registry")
        self.registered_commands: Set[Callable] = set()
        self.registered_notice_commands: Set[Callable] = set()
        self.registered_request_commands: Set[Callable] = set()
    
    def admin_only(self):
        """管理员权限装饰器
        
        只允许具有管理员或root权限的用户执行命令。
        """
        def decorator(func: Callable):
            self.registered_commands.add(func)
            if not hasattr(func, "__filter__"):
                setattr(func, "__filter__", [])
            getattr(func, "__filter__").append(AdminFilter())
            return func
        return decorator
    
    def root_only(self):
        """Root权限装饰器
        
        只允许具有root权限的用户执行命令。
        """
        def decorator(func: Callable):
            self.registered_commands.add(func)
            if not hasattr(func, "__filter__"):
                setattr(func, "__filter__", [])
            getattr(func, "__filter__").append(RootFilter())
            return func
        return decorator
    
    def group_message(self):
        """群组消息装饰器
        
        只允许群组消息触发命令。
        """
        def decorator(func: Callable):
            self.registered_commands.add(func)
            if not hasattr(func, "__filter__"):
                setattr(func, "__filter__", [])
            getattr(func, "__filter__").append(GroupFilter())
            return func
        return decorator
    
    def private_message(self):
        """私聊消息装饰器
        
        只允许私聊消息触发命令。
        """
        def decorator(func: Callable):
            self.registered_commands.add(func)
            if not hasattr(func, "__filter__"):
                setattr(func, "__filter__", [])
            getattr(func, "__filter__").append(PrivateFilter())
            return func
        return decorator

    def notice_event(self):
        """通知事件装饰器
        
        将函数注册为通知事件处理器。
        """
        def decorator(func: Callable):
            self.registered_notice_commands.add(func)
            return func
        return decorator
    
    def request_event(self):
        """请求事件装饰器
        
        将函数注册为请求事件处理器。
        """
        def decorator(func: Callable):
            self.registered_request_commands.add(func)
            return func
        return decorator
    
    def custom(self, filter_func: CustomFilterFunc) -> Callable[[Callable], Callable]:
        """自定义过滤器装饰器
        
        Args:
            filter_func: 自定义过滤函数，支持两种签名：
                - SimpleFilterFunc: (event: BaseMessageEvent) -> bool
                - AdvancedFilterFunc: (manager: FilterRegistryPlugin, event: BaseMessageEvent) -> bool
        
        Returns:
            装饰器函数
            
        Raises:
            ValueError: 当函数签名不符合要求时
            
        Examples:
            # 简单过滤器 - lambda 表达式
            @filter.custom(lambda event: 'special' in event.message.filter_text())
            async def handle_special(self, event: BaseMessageEvent):
                await event.reply("检测到特殊消息！")
            
            # 高级过滤器 - 函数引用，带类型注解
            def admin_filter(manager: FilterRegistryPlugin, event: BaseMessageEvent) -> bool:
                return manager.rbac_manager.user_has_role(event.user_id, "admin")
            
            @filter.custom(admin_filter)
            async def admin_command(self, event: BaseMessageEvent):
                await event.reply("管理员命令")
                
            # 简单过滤器 - 函数引用，带类型注解
            def keyword_filter(event: BaseMessageEvent) -> bool:
                return 'keyword' in event.message.filter_text().lower()
            
            @filter.custom(keyword_filter)
            async def handle_keyword(self, event: BaseMessageEvent):
                await event.reply("检测到关键词！")
        """
        def decorator(func: Callable) -> Callable:
            self.registered_commands.add(func)
            if not hasattr(func, "__filter__"):
                setattr(func, "__filter__", [])
            
            try:
                # 创建 CustomFilter 时会进行签名验证和类型检查
                custom_filter = CustomFilter(filter_func)
                getattr(func, "__filter__").append(custom_filter)
                LOG.debug(f"成功注册自定义过滤器: {func.__name__} -> {custom_filter.func_name}")
            except (ValueError, TypeError) as e:
                LOG.error(f"注册自定义过滤器失败，函数: {func.__name__}, 过滤器: {filter_func}, 错误: {e}")
                raise
            
            return func
        return decorator

    # 别名方法
    private_event = private_message
    group_event = group_message


# 创建全局实例
filter = FilterRegistry()
register = filter
