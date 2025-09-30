"""过滤器基础模块 v2.0"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent


class BaseFilter(ABC):
    """过滤器基类 v2.0

    简化设计：过滤器函数只接受 event 参数
    """

    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__

    @abstractmethod
    def check(self, event: "BaseMessageEvent") -> bool:
        """检查事件是否通过过滤器

        Args:
            event: 消息事件

        Returns:
            bool: True 表示通过过滤器，False 表示被拦截
        """
        pass

    def __call__(self, func: Callable) -> Callable:
        """使过滤器实例可作为装饰器使用"""

        from .registry import filter_registry

        # 将过滤器添加到函数
        filter_registry.add_filter_to_function(func, self)
        return func

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self) -> str:
        return self.__str__()
