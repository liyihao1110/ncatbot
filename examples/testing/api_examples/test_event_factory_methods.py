"""
EventFactory 方法测试
来源: docs/testing/api-reference.md
"""

from ncatbot.utils.testing import EventFactory
import asyncio


async def main():
    """测试 EventFactory 的各种方法"""
    # 纯文本消息
    event = EventFactory.create_group_message("Hello")
    print(f"群消息事件: {event.message}")

    # 私聊消息
    event = EventFactory.create_private_message(
        message="私聊消息", user_id="123456", nickname="测试用户", sub_type="friend"
    )
    print(f"私聊消息事件: {event.user_id}")

    # 群成员增加通知
    event = EventFactory.create_notice_event(
        notice_type="group_increase",
        user_id="123456",
        group_id="789012",
        sub_type="approve",
    )
    print(f"通知事件: {event.notice_type}")

    # 好友请求事件
    event = EventFactory.create_request_event(
        request_type="friend",
        user_id="123456",
        flag="test_flag",
        comment="请加我为好友",
    )
    print(f"请求事件: {event.request_type}")

    print("✅ EventFactory 方法测试完成")


if __name__ == "__main__":
    print("测试 EventFactory 方法...")
    asyncio.run(main())
