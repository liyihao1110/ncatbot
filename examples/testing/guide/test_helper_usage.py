"""
TestHelper 基本用法测试
来源: docs/testing/guide.md
"""


from ncatbot.utils.testing import TestClient, TestHelper
from ..common.hello_plugin import HelloPlugin
import asyncio


async def main():
    """测试 TestHelper 基本用法"""
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(HelloPlugin)

    # 发送消息
    await helper.send_private_message("你好", user_id="123456")
    await helper.send_group_message("大家好", group_id="789012", user_id="123456")

    # 获取回复
    latest_reply = helper.get_latest_reply()  # 获取最新回复
    second_reply = helper.get_latest_reply(-2)  # 获取倒数第二个回复

    print(f"最新回复: {latest_reply}")
    print(f"倒数第二个回复: {second_reply}")

    # 断言方法示例
    try:
        helper.assert_reply_sent("期望的文本")  # 这可能会失败
    except AssertionError:
        print("断言失败，这是预期的")

    # 清理历史记录
    helper.clear_history()

    # 设置 API 响应
    helper.set_api_response("/get_group_info", {
        "retcode": 0,
        "data": {
            "group_id": "789012",
            "group_name": "测试群",
            "member_count": 100
        }
    })
    print("已设置 API 响应")

    print("✅ TestHelper 基本用法测试完成")


if __name__ == "__main__":
    asyncio.run(main())
