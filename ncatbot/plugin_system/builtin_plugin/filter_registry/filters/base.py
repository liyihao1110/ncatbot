"""过滤器基类模块"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent
    from ..filter_registry import FilterRegistryPlugin


class BaseFilter(ABC):
    """过滤器抽象基类
    
    所有过滤器都必须继承这个基类并实现 check 方法。
    """
    
    @abstractmethod
    def check(self, manager: "FilterRegistryPlugin", event: "BaseMessageEvent") -> bool:
        """检查事件是否通过过滤器
        
        Args:
            manager: FilterRegistryPlugin 实例
            event: 消息事件
            
        Returns:
            bool: 是否通过过滤器检查
        """
        pass
