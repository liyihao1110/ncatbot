"""
简单的 hello 命令测试
来源: docs/testing/best-practice-simple.md
"""

from ncatbot.utils.testing import TestClient, TestHelper
from ..common.hello_plugin import HelloPlugin
import asyncio


async def main():
    """测试 hello 命令"""
    # 创建客户端和辅助器
    client = TestClient()
    helper = TestHelper(client)
    
    # 启动并注册插件
    client.start()
    client.register_plugin(HelloPlugin)
    
    # 发送测试消息
    await helper.send_private_message("/hello")
    
    # 验证回复
    reply = helper.get_latest_reply()
    if reply:
        print("✅ 测试通过：收到回复")
        print(f"回复内容：{reply['message']}")
    else:
        print("❌ 测试失败：没有收到回复")


if __name__ == "__main__":
    print("运行 hello 命令测试...")
    asyncio.run(main())
