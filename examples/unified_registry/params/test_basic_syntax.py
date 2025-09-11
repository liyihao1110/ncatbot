import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

from .plugins.params_basic_plugin import ParamsBasicPlugin


async def run_basic_syntax_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(ParamsBasicPlugin)

    await helper.send_private_message("/echo hello")
    helper.assert_reply_sent("你说的是: hello")
    helper.clear_history()

    await helper.send_private_message("/echo 这是一段文本")
    helper.assert_reply_sent("你说的是: 这是一段文本")
    helper.clear_history()

    await helper.send_private_message("/calc 10 add 20")
    helper.assert_reply_sent("10 + 20 = 30")
    helper.clear_history()

    await helper.send_private_message("/calc 100 sub 50")
    helper.assert_reply_sent("100 - 50 = 50")
    helper.clear_history()

    await helper.send_private_message('/say "hello world"')
    helper.assert_reply_sent("机器人说: hello world")
    helper.clear_history()

    await helper.send_private_message('/say "包含 空格 的 消息"')
    helper.assert_reply_sent("机器人说: 包含 空格 的 消息")
    helper.clear_history()

    print("\n✅ basic_syntax 测试通过")


if __name__ == "__main__":
    asyncio.run(run_basic_syntax_tests())


