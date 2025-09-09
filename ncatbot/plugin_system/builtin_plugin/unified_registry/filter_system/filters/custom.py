"""自定义过滤器实现"""

import inspect
from typing import Callable, TYPE_CHECKING
from .base import BaseFilter
from ncatbot.utils import get_log

if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent
    from ...plugin import UnifiedRegistryPlugin

LOG = get_log(__name__)

# 自定义过滤器函数类型
# CustomFilterFunc = Callable

class CustomFilter(BaseFilter):
    """自定义过滤器包装器
    
    支持两种过滤器函数签名：
    1. 简单过滤器: (event: BaseMessageEvent) -> bool  
    2. 高级过滤器: (manager: UnifiedRegistryPlugin, event: BaseMessageEvent) -> bool
    """
    
    def __init__(self, filter_func):
        """初始化自定义过滤器
        
        Args:
            filter_func: 过滤器函数
        """
        self.filter_func = filter_func
        self.func_name = getattr(filter_func, '__name__', str(filter_func))
        LOG.debug(f"注册自定义过滤器: {self.func_name}")
    
    def check(self, manager: "UnifiedRegistryPlugin", event: "BaseMessageEvent") -> bool:
        """执行自定义过滤器检查"""
        try:
            # 简单的参数数量检测，先尝试高级模式，失败则尝试简单模式
            sig = inspect.signature(self.filter_func)
            param_count = len(sig.parameters)
            
            if param_count == 2:
                # 高级过滤器: (manager, event)
                return self.filter_func(manager, event)
            elif param_count == 1:
                # 简单过滤器: (event)
                return self.filter_func(event)
            else:
                LOG.error(f"过滤器函数 {self.func_name} 参数数量错误: {param_count}，应为1个或2个参数")
                return False
                
        except Exception as e:
            LOG.error(f"执行自定义过滤器失败: {self.func_name}, 错误: {e}")
            return False
