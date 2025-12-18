"""
快速上手指南中的测试示例
来源: docs/testing/quick-start.md
"""

from ncatbot.utils.testing import TestClient, TestHelper
import asyncio

# 导入通用插件
from ..common.hello_plugin import HelloPlugin


async def test_hello_plugin():
    """测试 HelloPlugin 的基本功能"""

    # 1. 创建测试客户端
    client = TestClient()
    helper = TestHelper(client)

    # 2. 启动客户端（Mock 模式默认开启）
    client.start()

    # 3. 注册要测试的插件
    client.register_plugin(HelloPlugin)

    # 4. 测试 hello 命令
    await helper.send_private_message("/hello", user_id="test_user")

    # 5. 验证回复
    reply = helper.get_latest_reply()
    assert reply is not None, "应该收到回复"

    # 提取消息文本
    message_text = ""
    for seg in reply["message"]:
        if seg["type"] == "text":
            message_text += seg["data"]["text"]

    assert "你好！这是来自 HelloPlugin 的问候。" in message_text
    print("✅ hello 命令测试通过")

    # 6. 清理历史记录，准备下一个测试
    helper.clear_history()

    # 7. 测试命令别名
    await helper.send_private_message("/hi", user_id="test_user")
    reply = helper.get_latest_reply()
    assert reply is not None, "别名命令应该有回复"
    print("✅ 命令别名测试通过")

    helper.clear_history()

    # 8. 测试带参数/选项/命名参数
    await helper.send_private_message(
        "/echo 测试文本 --lang=zh -v", user_id="test_user"
    )
    reply = helper.get_latest_reply()
    assert reply is not None

    message_text = ""
    for seg in reply["message"]:
        if seg["type"] == "text":
            message_text += seg["data"]["text"]

    assert "你说的是：测试文本" in message_text
    print("✅ echo 命令测试通过")

    print("\n🎉 所有测试通过！")


# 运行测试
if __name__ == "__main__":
    asyncio.run(test_hello_plugin())
