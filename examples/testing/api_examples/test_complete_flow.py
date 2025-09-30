"""
完整测试流程示例
来源: docs/testing/api-reference.md
"""

from ncatbot.utils.testing import TestClient, TestHelper
from ..common.hello_plugin import HelloPlugin
import asyncio


def extract_text(message_segments):
    """从消息段列表中提取纯文本"""
    text = ""
    for seg in message_segments:
        if isinstance(seg, dict) and seg.get("type") == "text":
            text += seg.get("data", {}).get("text", "")
    return text


async def main():
    """完整测试流程示例"""
    # 1. 初始化
    client = TestClient()
    helper = TestHelper(client)

    # 2. 启动客户端
    client.start()

    # 3. 注册插件
    client.register_plugin(HelloPlugin)

    # 4. 设置 Mock 响应
    helper.set_api_response(
        "/get_user_info", {"retcode": 0, "data": {"nickname": "测试用户", "level": 10}}
    )

    # 5. 发送测试消息
    await helper.send_private_message("/hello")

    # 6. 验证回复
    reply = helper.get_latest_reply()
    assert reply is not None
    print(f"收到回复: {extract_text(reply['message'])}")

    # 7. 检查 API 调用
    api_calls = helper.get_api_calls()
    print(f"API 调用次数: {len(api_calls)}")
    for endpoint, data in api_calls:
        print(f"API: {endpoint}")

    # 8. 清理
    helper.clear_history()

    print("✅ 完整测试流程完成")


if __name__ == "__main__":
    print("运行完整测试流程...")
    asyncio.run(main())
