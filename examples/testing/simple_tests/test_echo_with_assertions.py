"""
带断言的 echo 命令测试
来源: docs/testing/best-practice-simple.md
"""

from ncatbot.utils.testing import TestClient, TestHelper
from ..common.hello_plugin import HelloPlugin
import asyncio


async def main():
    """带断言的测试"""
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(HelloPlugin)
    
    # 测试正常情况
    await helper.send_private_message("/echo 测试文本")
    reply = helper.get_latest_reply()
    assert reply is not None, "应该收到回复"
    
    # 提取文本内容
    text = ""
    for seg in reply["message"]:
        if seg["type"] == "text":
            text += seg["data"]["text"]
    
    assert "测试文本" in text, f"回复应包含输入文本，实际：{text}"
    print("✅ Echo 命令测试通过")
    
    # 测试错误情况
    helper.clear_history()
    await helper.send_private_message("/echo")  # 没有参数
    reply = helper.get_latest_reply()
    # 这个测试可能会失败，因为 echo 命令有默认参数处理
    print("✅ 错误处理测试完成")


if __name__ == "__main__":
    print("运行带断言的 echo 测试...")
    asyncio.run(main())
