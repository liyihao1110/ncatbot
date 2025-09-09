"""Legacy filter base module"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent
    from ...plugin import UnifiedRegistryPlugin


class BaseFilter(ABC):
    """Legacy filter base class"""

    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__

    @abstractmethod
    async def check(self, manager: "UnifiedRegistryPlugin", event: "BaseMessageEvent") -> bool:
        """检查事件是否通过过滤器"""
        pass

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self) -> str:
        return self.__str__()