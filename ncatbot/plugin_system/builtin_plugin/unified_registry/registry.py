"""统一注册系统核心"""

from typing import Callable, List, Set, Optional, TYPE_CHECKING
from .filter_system import (
    GroupFilter, PrivateFilter, AdminFilter, RootFilter, 
    CustomFilter, CustomFilterFunc, FilterValidator
)
from .command_system import CommandGroup, CommandRouter
from ncatbot.utils import get_log

if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent
    from .plugin import UnifiedRegistryPlugin

LOG = get_log(__name__)

class UnifiedRegistry(CommandGroup):
    """统一注册系统
    
    提供 filter 和 command 的统一接口，继承自 CommandGroup 以支持命令功能。
    """
    
    def __init__(self):
        """初始化统一注册系统"""
        super().__init__(None, "unified_registry")
        
        # 过滤器相关
        self.filter_functions: Set[Callable] = set()  # 纯过滤器函数
        self.registered_notice_commands: Set[Callable] = set()
        self.registered_request_commands: Set[Callable] = set()
        
        # 命令路由器
        self.command_router = CommandRouter()
        
        # 延迟初始化的组件（需要插件实例）
        self._filter_validator: Optional[FilterValidator] = None
        
        LOG.debug("统一注册系统初始化完成")
    
    def set_plugin_manager(self, manager: "UnifiedRegistryPlugin"):
        """设置插件管理器实例
        
        Args:
            manager: 插件管理器实例
        """
        self._filter_validator = FilterValidator(manager)
        LOG.debug("设置插件管理器完成")
    
    # ==================== 过滤器装饰器 ====================
    
    def admin_only(self):
        """管理员权限装饰器"""
        def decorator(func: Callable):
            self._add_filter_to_function(func, AdminFilter())
            self._register_filter_function_if_needed(func)
            return func
        return decorator
    
    def root_only(self):
        """Root权限装饰器"""
        def decorator(func: Callable):
            self._add_filter_to_function(func, RootFilter())
            self._register_filter_function_if_needed(func)
            return func
        return decorator
    
    def group_message(self):
        """群聊消息装饰器"""
        def decorator(func: Callable):
            self._add_filter_to_function(func, GroupFilter())
            self._register_filter_function_if_needed(func)
            return func
        return decorator
    
    def private_message(self):
        """私聊消息装饰器"""
        def decorator(func: Callable):
            self._add_filter_to_function(func, PrivateFilter())
            self._register_filter_function_if_needed(func)
            return func
        return decorator
    
    def custom(self, filter_func: CustomFilterFunc):
        """自定义过滤器装饰器"""
        def decorator(func: Callable):
            try:
                custom_filter = CustomFilter(filter_func)
                self._add_filter_to_function(func, custom_filter)
                self._register_filter_function_if_needed(func)
                LOG.debug(f"成功注册自定义过滤器: {func.__name__} -> {custom_filter.func_name}")
            except (ValueError, TypeError) as e:
                LOG.error(f"注册自定义过滤器失败，函数: {func.__name__}, 过滤器: {filter_func}, 错误: {e}")
                raise
            return func
        return decorator
    
    # ==================== 事件装饰器 ====================
    
    def notice_event(self):
        """通知事件装饰器"""
        def decorator(func: Callable):
            self.registered_notice_commands.add(func)
            return func
        return decorator
    
    def request_event(self):
        """请求事件装饰器"""
        def decorator(func: Callable):
            self.registered_request_commands.add(func)
            return func
        return decorator
    
    # ==================== 命令装饰器 ====================
    
    def command(self, name: str, alias: Optional[List[str]] = None):
        """命令注册装饰器"""
        def decorator(func: Callable):
            # 标记为命令函数
            setattr(func, "__is_command__", True)
            # 调用父类方法注册命令
            return super(UnifiedRegistry, self).command(name, alias)(func)
        return decorator
    
    # ==================== 内部方法 ====================
    
    def _add_filter_to_function(self, func: Callable, filter_instance):
        """为函数添加过滤器"""
        if self._filter_validator:
            self._filter_validator.add_filter_to_function(func, filter_instance)
        else:
            # 如果验证器还未初始化，直接添加到函数属性
            if not hasattr(func, "__filter__"):
                setattr(func, "__filter__", [])
            getattr(func, "__filter__").append(filter_instance)
    
    def _register_filter_function_if_needed(self, func: Callable):
        """如果需要，将函数注册为过滤器函数"""
        # 只有非命令函数才添加到 filter_functions
        if not getattr(func, "__is_command__", False):
            self.filter_functions.add(func)
            LOG.debug(f"注册过滤器函数: {func.__name__}")
    
    # ==================== 公共接口 ====================
    
    def initialize_router(self):
        """初始化命令路由器"""
        self.command_router.initialize(self)
    
    def find_command(self, event: "BaseMessageEvent"):
        """查找命令"""
        return self.command_router.find_command(event)
    
    def validate_filters(self, func: Callable, event: "BaseMessageEvent") -> bool:
        """验证函数的过滤器"""
        if self._filter_validator:
            return self._filter_validator.validate_filters(func, event)
        return True
    
    def clear(self):
        """清理状态"""
        self.command_router.clear()
    
    # ==================== 别名方法 ====================
    
    # 保持向后兼容
    private_event = private_message
    group_event = group_message

# 创建全局实例
filter = UnifiedRegistry()
register = filter  # 别名
