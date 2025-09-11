"""
MockAPIAdapter 用法测试
来源: docs/testing/guide.md
"""
from ncatbot.utils.testing import TestClient, TestHelper
from ..common.hello_plugin import HelloPlugin
import asyncio


async def main():
    """测试 MockAPIAdapter 用法"""
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(HelloPlugin)

    # 通过 helper 访问 mock_api
    mock_api = helper.mock_api

    # 获取 API 调用历史
    all_calls = mock_api.get_call_history()
    print(f"所有 API 调用: {len(all_calls)}")

    # 设置自定义响应
    mock_api.set_response("/custom_api", {
        "retcode": 0,
        "data": {"custom": "response"}
    })

    # 设置动态响应
    def dynamic_response(endpoint, data):
        if data.get("user_id") == "123456":
            return {"retcode": 0, "data": {"vip": True}}
        return {"retcode": 0, "data": {"vip": False}}

    mock_api.set_response("/get_user_info", dynamic_response)
    print("已设置动态响应")

    # 测试 API 调用记录
    await helper.send_private_message("/hello")
    calls_after = mock_api.get_call_history()
    print(f"发送消息后的 API 调用: {len(calls_after)}")

    print("✅ MockAPIAdapter 用法测试完成")


if __name__ == "__main__":
    asyncio.run(main())
