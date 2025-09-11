"""
EventFactory 用法测试
来源: docs/testing/guide.md
"""
from ncatbot.utils.testing import EventFactory
from ncatbot.core.event.message_segment import MessageArray, Text, At, Image
import asyncio


async def main():
    """测试 EventFactory 用法"""
    # 创建纯文本消息事件
    event = EventFactory.create_group_message(
        message="Hello World",
        group_id="123456789",
        user_id="987654321",
        nickname="TestUser",
        role="member"  # member, admin, owner
    )
    print(f"群消息事件: {event}")

    # 创建复杂消息事件
    msg_array = MessageArray(
        Text("你好 "),
        At("123456"),
        Text(" 这是一张图片："),
        Image("http://example.com/image.jpg")
    )
    event = EventFactory.create_group_message(message=msg_array)
    print(f"复杂消息事件: {event}")

    # 创建私聊消息事件
    event = EventFactory.create_private_message(
        message="私聊消息",
        user_id="123456",
        sub_type="friend"  # friend, group, other
    )
    print(f"私聊消息事件: {event}")

    # 创建通知事件
    event = EventFactory.create_notice_event(
        notice_type="group_increase",
        user_id="123456",
        group_id="789012",
        sub_type="approve"
    )
    print(f"通知事件: {event}")

    # 创建请求事件
    event = EventFactory.create_request_event(
        request_type="friend",
        user_id="123456",
        flag="unique_flag",
        comment="请加我为好友"
    )
    print(f"请求事件: {event}")

    print("✅ EventFactory 用法测试完成")


if __name__ == "__main__":
    asyncio.run(main())
