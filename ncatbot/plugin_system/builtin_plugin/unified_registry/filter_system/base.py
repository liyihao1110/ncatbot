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

    def __or__(self, other: "BaseFilter") -> "BaseFilter":
        """支持使用 | 将两个过滤器组合为或逻辑"""
        if not isinstance(other, BaseFilter):
            raise TypeError("右操作数必须是 BaseFilter 实例")
        return CombinedFilter(self, other, "or")

    def __and__(self, other: "BaseFilter") -> "BaseFilter":
        """支持使用 & 将两个过滤器组合为与逻辑"""
        if not isinstance(other, BaseFilter):
            raise TypeError("右操作数必须是 BaseFilter 实例")
        return CombinedFilter(self, other, "and")


class CombinedFilter(BaseFilter):
    """组合过滤器，支持 AND/OR 两种模式"""

    def __init__(self, left: BaseFilter, right: BaseFilter, mode: str = "or"):
        super().__init__(name=f"Combined({left.name},{right.name},{mode})")
        self.left = left
        self.right = right
        if mode not in ("or", "and"):
            raise ValueError("mode must be 'or' or 'and'")
        self.mode = mode

    def check(self, event: "BaseMessageEvent") -> bool:
        if self.mode == "or":
            try:
                return self.left.check(event) or self.right.check(event)
            except Exception:
                # 保守策略：出现异常视为未通过
                return False
        else:
            try:
                return self.left.check(event) and self.right.check(event)
            except Exception:
                return False
