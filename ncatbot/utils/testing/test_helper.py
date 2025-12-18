from typing import Literal, Optional, Dict, List, Union, TYPE_CHECKING
from .event_factory import EventFactory
from .mock_api import MockAPIAdapter
from ncatbot.utils import get_log
from ncatbot.utils import run_coroutine

if TYPE_CHECKING:
    from ncatbot.core.event.message_segment import MessageArray
else:
    MessageArray = "MessageArray"

LOG = get_log("TestHelper")


class TestHelper:
    """通用测试助手类"""

    def __init__(self, client_with_mixin):
        self.client = client_with_mixin
        self.mock_api = MockAPIAdapter()

        # 替换客户端的 API 回调
        if hasattr(self.client, "api"):
            self.client.api.async_callback = self.mock_api.mock_callback
            LOG.info("API 回调已替换为 Mock 版本")

    async def send_group_message(
        self,
        message: Union[str, MessageArray],
        group_id: str = "123456789",
        user_id: str = "987654321",
        nickname: str = "TestUser",
        **kwargs,
    ):
        """发送群聊消息事件并处理"""
        event = EventFactory.create_group_message(
            message=message,
            group_id=group_id,
            user_id=user_id,
            nickname=nickname,
            **kwargs,
        )
        LOG.info(f"发送群聊消息事件: {event}")
        await self.client.inject_event(event)

    async def send_private_message(
        self,
        message: Union[str, MessageArray],
        user_id: str = "987654321",
        nickname: str = "TestUser",
        **kwargs,
    ):
        """发送私聊消息事件并处理"""
        event = EventFactory.create_private_message(
            message=message, user_id=user_id, nickname=nickname, **kwargs
        )
        LOG.info(f"发送私聊消息事件: {event}")
        await self.client.inject_event(event)

    def send_group_message_sync(
        self,
        message: Union[str, MessageArray],
        group_id: str = "123456789",
        user_id: str = "987654321",
        nickname: str = "TestUser",
        **kwargs,
    ):
        """同步发送群聊消息事件并处理"""
        run_coroutine(
            self.send_group_message, message, group_id, user_id, nickname, **kwargs
        )

    def send_private_message_sync(
        self,
        message: Union[str, MessageArray],
        user_id: str = "987654321",
        nickname: str = "TestUser",
        **kwargs,
    ):
        """同步发送私聊消息事件并处理"""
        run_coroutine(self.send_private_message, message, user_id, nickname, **kwargs)

    def assert_reply_sent(self, expected_text: Optional[str] = None):
        """断言发送了回复"""
        group_calls = self.mock_api.get_calls_for_endpoint("/send_group_msg")
        private_calls = self.mock_api.get_calls_for_endpoint("/send_private_msg")

        all_calls = group_calls + private_calls
        assert all_calls, "没有发送任何回复"

        if expected_text:
            for call in all_calls:
                message = call.get("message", [])
                # 检查消息段中是否包含预期文本
                for segment in message:
                    if isinstance(segment, dict) and segment.get("type") == "text":
                        if expected_text in segment.get("data", {}).get("text", ""):
                            return True
                # 也检查消息的字符串表示
                message_str = str(message)
                if expected_text in message_str:
                    return True
            raise AssertionError(f"回复中未包含预期文本: {expected_text}")

    def assert_no_reply(self):
        """断言没有发送回复"""
        group_calls = self.mock_api.get_calls_for_endpoint("/send_group_msg")
        private_calls = self.mock_api.get_calls_for_endpoint("/send_private_msg")

        all_calls = group_calls + private_calls
        assert not all_calls, f"意外发送了 {len(all_calls)} 条回复"

    def get_api_calls(self) -> List[tuple]:
        """获取所有 API 调用"""
        return self.mock_api.get_call_history()

    def get_latest_reply(self, index: int = -1) -> Optional[Dict]:
        """获取最新的回复"""
        group_calls = self.mock_api.get_calls_for_endpoint("/send_group_msg")
        private_calls = self.mock_api.get_calls_for_endpoint("/send_private_msg")

        all_calls = group_calls + private_calls
        return all_calls[index] if all_calls else None

    def clear_history(self):
        """清空所有历史记录"""
        self.mock_api.clear_call_history()

    def set_api_response(self, endpoint: str, response: Dict):
        """设置 API 响应"""
        self.mock_api.set_response(endpoint, response)

    def set_user_permission(self, user_id: str, role: str):
        """设置用户权限（需要配合 RBAC 系统）"""
        # 这里需要与 RBAC 系统集成
        # 暂时留空，等待 RBAC 系统的接口
        LOG.warning(f"set_user_permission 方法尚未实现: {user_id} -> {role}")

    async def on_friend_request(self, user_id: str = "987654321", comment: str = " "):
        """创建添加好友请求事件并处理"""
        event = EventFactory.create_friend_request_event(
            user_id=user_id, comment=comment
        )
        LOG.info(f"创建添加好友请求事件: {event}")
        await self.client.inject_event(event)

    async def on_group_add_request(
        self,
        user_id: str = "987654321",
        group_id: str = "123456789",
        comment: str = " ",
    ):
        """创建加入群聊请求事件并处理"""
        event = EventFactory.create_group_add_request_event(
            user_id=user_id, group_id=group_id, comment=comment
        )
        LOG.info(f"创建加入群聊请求事件: {event}")
        await self.client.inject_event(event)

    async def on_group_increase_notice(
        self,
        user_id: str = "987654321",
        group_id: str = "123456789",
        operator_id: str = "88888888",
        comment: str = " ",
        sub_type: Literal["approve", "invite"] = "approve",
    ):
        """创建群成员增加通知事件并处理"""
        if sub_type not in ["approve", "invite"]:
            raise ValueError("sub_type must be 'approve' or 'invite'")
        event = EventFactory.create_group_increase_notice_event(
            user_id=user_id,
            group_id=group_id,
            operator_id=operator_id,
            comment=comment,
            sub_type=sub_type,
        )
        LOG.info(f"创建群成员增加通知事件（sub_type={sub_type}）: {event}")
        await self.client.inject_event(event)

    async def on_group_decrease_notice(
        self,
        user_id: str = "987654321",
        group_id: str = "123456789",
        operator_id: str = "88888888",
        comment: str = " ",
        sub_type: Literal["leave", "kick"] = "leave",
    ):
        """创建群成员减少通知事件并处理"""
        if sub_type not in ["leave", "kick"]:
            raise ValueError("sub_type must be 'leave' or 'kick'")
        if sub_type == "leave":
            operator_id = "0"
        event = EventFactory.create_group_decrease_notice_event(
            user_id=user_id,
            group_id=group_id,
            operator_id=operator_id,
            comment=comment,
            sub_type=sub_type,
        )
        LOG.info(f"创建群成员减少通知事件（sub_type={sub_type}）: {event}")
        await self.client.inject_event(event)

    async def on_group_poke_notice(
        self,
        user_id: str = "987654321",
        group_id: str = "123456789",
        target_id: str = "77777777",
        raw_info: Optional[Dict] = None,
    ):
        """创建群成员戳一戳通知事件并处理，raw_info 没有进行数据验证，谨慎传入。"""
        event = EventFactory.create_group_poke_notice_event(
            user_id=user_id, group_id=group_id, target_id=target_id, raw_info=raw_info
        )
        LOG.info(f"创建群成员戳一戳通知事件: {event}")
        await self.client.inject_event(event)
