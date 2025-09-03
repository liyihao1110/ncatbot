"""过滤器基础模块"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent
    from ...plugin import UnifiedRegistryPlugin

class BaseFilter(ABC):
    """过滤器基类
    
    所有过滤器都必须继承此类并实现 check 方法。
    """
    
    @abstractmethod
    def check(self, manager: "UnifiedRegistryPlugin", event: "BaseMessageEvent") -> bool:
        """检查事件是否通过过滤器
        
        Args:
            manager: 插件管理器实例
            event: 消息事件
            
        Returns:
            bool: True 表示通过过滤器，False 表示被过滤器拦截
        """
        pass
