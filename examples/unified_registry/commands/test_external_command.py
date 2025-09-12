import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

from .plugins.cmd_external_plugin import CmdExternalPlugin


async def run_external_command_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(CmdExternalPlugin)

    for cmd in ("/status", "/stat", "/st"):
        await helper.send_private_message(cmd)
        helper.assert_reply_sent("机器人运行正常")
        helper.clear_history()
    
    await helper.send_private_message("non_prefix_hello")
    helper.assert_reply_sent("Hello, World!")
    helper.clear_history()

    await helper.send_private_message("!my_group my_group_hello")
    helper.assert_reply_sent("Hello, Group World!")
    helper.clear_history()
    print("\n✅ external_command 测试通过")


if __name__ == "__main__":
    asyncio.run(run_external_command_tests())


