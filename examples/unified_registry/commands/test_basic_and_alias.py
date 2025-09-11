import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

from .plugins.cmd_basic_alias_plugin import CmdBasicAliasPlugin


async def run_basic_and_alias_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(CmdBasicAliasPlugin)

    await helper.send_private_message("/hello")
    helper.assert_reply_sent("Hello, World!")
    helper.clear_history()

    await helper.send_private_message("/ping")
    helper.assert_reply_sent("pong!")
    helper.clear_history()

    for cmd in ("/status", "/stat", "/st"):
        await helper.send_private_message(cmd)
        helper.assert_reply_sent("机器人运行正常")
        helper.clear_history()

    print("\n✅ basic_and_alias 测试通过")


if __name__ == "__main__":
    asyncio.run(run_basic_and_alias_tests())


