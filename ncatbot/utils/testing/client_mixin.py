from typing import List, Tuple
from ncatbot.core.event import BaseEventData
from ncatbot.utils import (
    OFFICIAL_PRIVATE_MESSAGE_EVENT,
    OFFICIAL_GROUP_MESSAGE_EVENT,
    OFFICIAL_NOTICE_EVENT,
    OFFICIAL_REQUEST_EVENT,
)
from ncatbot.utils import get_log

LOG = get_log("ClientMixin")


class ClientMixin:
    """客户端混入类，为 BotClient 添加测试功能"""

    def __init__(self, *args, **kwargs):
        # 测试模式默认不加载插件，需要手动加载要测试的插件
        self.mock_mode = True
        self.event_history: List[Tuple[str, BaseEventData]] = []

    def enable_mock_mode(self):
        """启用 Mock 模式"""
        self.mock_mode = True
        LOG.info("Mock 模式已启用")

    def disable_mock_mode(self):
        """禁用 Mock 模式"""
        self.mock_mode = False
        LOG.info("Mock 模式已禁用")

    def mock_start(self):
        LOG.info("Mock 模式启动：跳过 NapCat 服务和 WebSocket 连接")
        # 在 mock 模式下触发启动事件
        from ncatbot.core.event.meta import MetaEvent

        startup_event = MetaEvent(
            {
                "post_type": "meta_event",
                "meta_event_type": "lifecycle",
                "sub_type": "enable",
                "self_id": "123456789",
                "time": int(__import__("time").time()),
            }
        )
        # 同步调用启动处理器
        import inspect
        from ncatbot.utils import run_coroutine
        from ncatbot.utils import OFFICIAL_STARTUP_EVENT

        for handler in self.event_handlers[OFFICIAL_STARTUP_EVENT]:
            if inspect.iscoroutinefunction(handler):
                run_coroutine(handler, startup_event)
            else:
                handler(startup_event)
        return

    async def inject_event(self, event: BaseEventData):
        """注入事件到客户端，模拟从适配器接收事件

        Args:
            event: 要注入的事件对象
        """
        if not self.mock_mode:
            raise RuntimeError("必须先启用 Mock 模式才能注入事件")

        # 记录事件历史
        self.event_history.append((event.post_type, event))
        LOG.debug(f"注入事件: {event.post_type} - {event}")

        # 确定事件类型并调用相应的处理器
        if hasattr(event, "message_type"):
            if event.message_type == "group":
                await self._handle_group_message(event)
            elif event.message_type == "private":
                await self._handle_private_message(event)
        elif event.post_type == "notice":
            await self._handle_notice(event)
        elif event.post_type == "request":
            await self._handle_request(event)

    async def _handle_group_message(self, event):
        """处理群聊消息事件"""
        for handler in self.event_handlers.get(OFFICIAL_GROUP_MESSAGE_EVENT, []):
            try:
                await handler(event)
            except Exception as e:
                LOG.error(f"处理群聊消息时出错: {e}")

    async def _handle_private_message(self, event):
        """处理私聊消息事件"""
        for handler in self.event_handlers.get(OFFICIAL_PRIVATE_MESSAGE_EVENT, []):
            try:
                await handler(event)
            except Exception as e:
                LOG.error(f"处理私聊消息时出错: {e}")

    async def _handle_notice(self, event):
        """处理通知事件"""
        for handler in self.event_handlers.get(OFFICIAL_NOTICE_EVENT, []):
            try:
                await handler(event)
            except Exception as e:
                LOG.error(f"处理通知事件时出错: {e}")

    async def _handle_request(self, event):
        """处理请求事件"""
        for handler in self.event_handlers.get(OFFICIAL_REQUEST_EVENT, []):
            try:
                await handler(event)
            except Exception as e:
                LOG.error(f"处理请求事件时出错: {e}")

    def get_event_history(self) -> List[Tuple[str, BaseEventData]]:
        """获取事件历史记录"""
        return self.event_history.copy()

    def clear_event_history(self):
        """清空事件历史记录"""
        self.event_history.clear()
