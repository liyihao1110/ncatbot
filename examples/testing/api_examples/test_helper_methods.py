"""
TestHelper 方法测试
来源: docs/testing/api-reference.md
"""
from ncatbot.utils.testing import TestClient, TestHelper
from ..common.hello_plugin import HelloPlugin
import asyncio


async def main():
    """测试 TestHelper 的各种方法"""
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(HelloPlugin)
    
    # 测试发送私聊消息
    await helper.send_private_message(
        "/hello",
        user_id="123456",
        nickname="测试用户"
    )
    
    # 测试发送群聊消息
    await helper.send_group_message(
        "大家好",
        group_id="888888",
        user_id="123456",
        nickname="测试用户",
        role="member"
    )
    
    # 获取最新回复
    latest = helper.get_latest_reply()
    print(f"最新回复: {latest}")
    
    # 获取倒数第二个回复
    try:
        second_last = helper.get_latest_reply(-2)
    except IndexError:
        # 第二个回复不存在
        pass
    
    # 断言回复
    try:
        helper.assert_reply_sent("你好")
        print("✅ 断言通过：包含期望文本")
    except AssertionError:
        print("❌ 断言失败")
    
    # 测试 API 响应设置
    helper.set_api_response("/get_user_info", {
        "retcode": 0,
        "data": {
            "user_id": "123456",
            "nickname": "测试用户",
            "level": 10
        }
    })
    print("✅ API 响应设置完成")
    print("✅ TestHelper 方法测试完成")


if __name__ == "__main__":
    print("测试 TestHelper 方法...")
    asyncio.run(main())
