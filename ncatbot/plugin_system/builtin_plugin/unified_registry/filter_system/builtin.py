"""内置过滤器实现 v2.0"""

from typing import TYPE_CHECKING, Callable, Optional, Union, Iterable
from ncatbot.core import BaseMessageEvent, MessageSentEvent
from ncatbot.utils import status
from ncatbot.utils.assets.literals import PermissionGroup
from .base import BaseFilter


if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent


class GroupFilter(BaseFilter):
    """群聊消息过滤器"""

    def __init__(
        self,
        allowed: Optional[Union[str, int, Iterable[Union[str, int]]]] = None,
        name: str = None,
    ):
        """
        初始化 GroupFilter

        Args:
            allowed: 可选的群号或群号列表（str 或 int），若为 None 则允许任意群聊
            name: 可选名称，默认保留类名
        """
        super().__init__(name=name or "GroupFilter")
        if allowed is None:
            self.allowed = None
        else:
            # 单个 id 转为集合，统一为字符串比较
            if isinstance(allowed, (str, int)):
                self.allowed = {str(allowed)}
            else:
                try:
                    self.allowed = {str(x) for x in allowed}
                except TypeError:
                    raise TypeError("allowed must be str|int or an iterable of str|int")

    def check(self, event: "BaseMessageEvent") -> bool:
        """检查是否为群聊消息且（可选）群号在允许列表中"""
        if not event.is_group_event():
            return False
        if self.allowed is None:
            return True
        group_id = getattr(event, "group_id", None)
        if group_id is None:
            return False
        return str(group_id) in self.allowed


class PrivateFilter(BaseFilter):
    """私聊消息过滤器"""

    def check(self, event: "BaseMessageEvent") -> bool:
        """检查是否为私聊消息"""
        return not event.is_group_event()


class MessageSentFilter(BaseFilter):
    """自身上报消息过滤器"""

    def check(self, event: "BaseMessageEvent") -> bool:
        """检查是否为自身上报的消息"""
        return isinstance(event, MessageSentEvent)


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


class GroupAdminFilter(BaseFilter):
    """群管理员权限过滤器"""

    def check(self, event: "BaseMessageEvent") -> bool:
        """检查用户是否为群管理员"""
        group_id = getattr(event, "group_id", None)
        if not group_id:  # 不是群事件
            return False
        # FIXME: napcat 可能不会实时更新 sender 信息，同步问题修复后考虑通过api获取role信息
        sender_info = event.sender
        sender_role = getattr(sender_info, "role", None)
        return sender_role in ["admin", "owner"]


class GroupOwnerFilter(BaseFilter):
    """群主权限过滤器"""

    def check(self, event: "BaseMessageEvent") -> bool:
        """检查用户是否为群主"""
        # 与 GroupAdminFilter 类似，考虑重构
        group_id = getattr(event, "group_id", None)
        if not group_id:  # 不是群事件
            return False
        # FIXME: napcat 可能不会实时更新 sender 信息，同步问题修复后考虑通过api获取role信息
        sender = event.sender
        sender_role = getattr(sender, "role", None)
        return sender_role == "owner"


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


class NonSelfFilter(BaseFilter):
    """非自身消息过滤器"""

    def check(self, event: "BaseMessageEvent") -> bool:
        return not isinstance(event, MessageSentEvent)


class TrueFilter(BaseFilter):
    """True过滤器, 用于注册发送消息时调用的功能"""

    def check(self, event: "BaseMessageEvent") -> bool:
        return True


class CustomFilter(BaseFilter):
    """自定义函数过滤器包装器"""

    def __init__(self, filter_func: Callable[[BaseMessageEvent], bool], name: str = ""):
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
