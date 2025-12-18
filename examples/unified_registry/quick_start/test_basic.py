import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

from .plugins.qs_basic_plugin import QSBasicPlugin


async def run_basic_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(QSBasicPlugin)

    # hello/ping
    await helper.send_private_message("/hello")
    helper.assert_reply_sent("你好！我是机器人。")
    helper.clear_history()

    await helper.send_private_message("/ping")
    helper.assert_reply_sent("pong!")
    helper.clear_history()

    # 参数命令
    await helper.send_private_message("/echo 测试文本")
    helper.assert_reply_sent("你说的是: 测试文本")
    helper.clear_history()

    await helper.send_private_message("/add 10 20")
    helper.assert_reply_sent("10 + 20 = 30")
    helper.clear_history()

    # 复杂参数与选项（按修复后的语义）
    await helper.send_private_message("/deploy myapp")
    helper.assert_reply_sent("正在部署 myapp 到 dev 环境")
    helper.clear_history()

    await helper.send_private_message("/deploy myapp --env=prod -v")
    helper.assert_reply_sent("正在部署 myapp 到 prod 环境")
    helper.assert_reply_sent("详细信息: 开始部署流程...")
    helper.clear_history()

    await helper.send_private_message("/deploy myapp --force")
    helper.assert_reply_sent("正在部署 myapp 到 dev 环境 (强制模式)")
    helper.clear_history()

    await helper.send_private_message("/deploy --force myapp")
    helper.assert_reply_sent("正在部署 myapp 到 dev 环境 (强制模式)")
    helper.clear_history()

    # 别名
    for cmd in ("/status", "/stat", "/st"):
        await helper.send_private_message(cmd)
        helper.assert_reply_sent("机器人运行正常")
        helper.clear_history()

    print("\n✅ basic 测试通过")


if __name__ == "__main__":
    asyncio.run(run_basic_tests())
