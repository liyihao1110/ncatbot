import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

from .plugins.cmd_groups_plugin import CmdGroupsPlugin


async def run_groups_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(CmdGroupsPlugin)

    await helper.send_private_message("/user list")
    helper.assert_reply_sent("用户列表: user1, user2, user3")
    helper.clear_history()

    await helper.send_private_message("/user info 123")
    helper.assert_reply_sent("用户 123 的信息")
    helper.clear_history()

    await helper.send_private_message("/admin user ban 123")
    helper.assert_reply_sent("已封禁用户: 123")
    helper.clear_history()

    await helper.send_private_message("/admin user unban 123")
    helper.assert_reply_sent("已解封用户: 123")
    helper.clear_history()

    # 别名直达端点
    await helper.send_private_message("/ul")
    helper.assert_reply_sent("用户列表: user1, user2, user3")
    helper.clear_history()

    await helper.send_private_message("/ui 456")
    helper.assert_reply_sent("用户 456 的信息")
    helper.clear_history()

    await helper.send_private_message("/aub 789")
    helper.assert_reply_sent("已封禁用户: 789")
    helper.clear_history()

    await helper.send_private_message("/aun 789")
    helper.assert_reply_sent("已解封用户: 789")
    helper.clear_history()

    print("\n✅ groups 测试通过")


if __name__ == "__main__":
    asyncio.run(run_groups_tests())
