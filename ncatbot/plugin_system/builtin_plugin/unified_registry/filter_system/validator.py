"""过滤器验证器"""

from typing import Callable, List, TYPE_CHECKING
from .filters import BaseFilter
from ncatbot.utils import get_log

if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent
    from ..plugin import UnifiedRegistryPlugin

LOG = get_log(__name__)

class FilterValidator:
    """过滤器验证器
    
    负责执行函数上的所有过滤器验证
    """
    
    def __init__(self, manager: "UnifiedRegistryPlugin"):
        """初始化验证器
        
        Args:
            manager: 插件管理器实例
        """
        self.manager = manager
    
    def validate_filters(self, func: Callable, event: "BaseMessageEvent") -> bool:
        """验证函数的所有过滤器
        
        Args:
            func: 要验证的函数
            event: 消息事件
            
        Returns:
            bool: True 表示通过所有过滤器，False 表示被拦截
        """
        filters: List[BaseFilter] = getattr(func, "__filter__", [])
        
        if not filters:
            # 没有过滤器的函数默认通过
            return True
        
        # 执行所有过滤器验证
        for filter_instance in filters:
            try:
                if not filter_instance.check(self.manager, event):
                    LOG.debug(f"函数 {func.__name__} 被过滤器 {filter_instance.__class__.__name__} 拦截")
                    return False
            except Exception as e:
                LOG.error(f"过滤器验证失败: {filter_instance.__class__.__name__}, 错误: {e}")
                return False
        
        LOG.debug(f"函数 {func.__name__} 通过所有过滤器验证")
        return True
    
    def add_filter_to_function(self, func: Callable, filter_instance: BaseFilter) -> Callable:
        """为函数添加过滤器
        
        Args:
            func: 目标函数
            filter_instance: 过滤器实例
            
        Returns:
            Callable: 修改后的函数
        """
        if not hasattr(func, "__filter__"):
            setattr(func, "__filter__", [])
        
        filters: List[BaseFilter] = getattr(func, "__filter__")
        filters.append(filter_instance)
        
        LOG.debug(f"为函数 {func.__name__} 添加过滤器 {filter_instance.__class__.__name__}")
        return func
