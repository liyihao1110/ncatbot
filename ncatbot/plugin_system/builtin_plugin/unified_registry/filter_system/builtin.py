"""内置过滤器实现 v2.0"""

from typing import TYPE_CHECKING, Callable
from ncatbot.core import BaseMessageEvent
from ncatbot.utils import status
from ncatbot.utils.assets.literals import PermissionGroup
from .base import BaseFilter


if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent


class GroupFilter(BaseFilter):
    """群聊消息过滤器"""

    def check(self, event: "BaseMessageEvent") -> bool:
        """检查是否为群聊消息"""
        return event.is_group_msg()


class PrivateFilter(BaseFilter):
    """私聊消息过滤器"""

    def check(self, event: "BaseMessageEvent") -> bool:
        """检查是否为私聊消息"""
        return not event.is_group_msg()


class AdminFilter(BaseFilter):
    """管理员权限过滤器"""

    def check(self, event: "BaseMessageEvent") -> bool:
        """检查用户是否有管理员权限"""
        if not status.global_access_manager:
            return False

        user_id = event.user_id
        return status.global_access_manager.user_has_role(
            user_id, PermissionGroup.ADMIN.value
        ) or status.global_access_manager.user_has_role(
            user_id, PermissionGroup.ROOT.value
        )


class RootFilter(BaseFilter):
    """Root权限过滤器"""

    def check(self, event: "BaseMessageEvent") -> bool:
        """检查用户是否有root权限"""
        if not status.global_access_manager:
            return False

        user_id = event.user_id
        return status.global_access_manager.user_has_role(
            user_id, PermissionGroup.ROOT.value
        )


class TrueFilter(BaseFilter):
    """True过滤器, 用于注册发送消息时调用的功能"""

    def check(self, event: "BaseMessageEvent") -> bool:
        return True


class CustomFilter(BaseFilter):
    """自定义函数过滤器包装器"""

    def __init__(
        self, filter_func: Callable[[BaseMessageEvent], bool], name: str = None
    ):
        """初始化自定义过滤器

        Args:
            filter_func: 过滤器函数，签名为 (event: BaseMessageEvent) -> bool
            name: 过滤器名称
        """

        super().__init__(name or getattr(filter_func, "__name__", "custom"))
        self.filter_func = filter_func

    def check(self, event: "BaseMessageEvent") -> bool:
        """执行自定义过滤器检查"""
        return self.filter_func(event)
