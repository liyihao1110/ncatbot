import asyncio
from ncatbot.utils.testing import TestClient, TestHelper
from ncatbot.utils import status

from .plugins.group_management_plugin import GroupManagementPlugin


async def run_group_management_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(GroupManagementPlugin)

    # 管理员权限模拟
    original_manager = status.global_access_manager

    class _AdminManager:
        def user_has_role(self, user_id, role):
            return True

    status.global_access_manager = _AdminManager()
    try:
        await helper.send_group_message("/mute 10086 --duration=120", group_id="g1")
        helper.assert_reply_sent("🔇 已禁言用户 10086，时长 120 秒")
        helper.clear_history()

        await helper.send_group_message("/unmute 10086", group_id="g1")
        helper.assert_reply_sent("🔊 已解除用户 10086 的禁言")
        helper.clear_history()

        await helper.send_group_message("/kick 10086 -b", group_id="g1")
        helper.assert_reply_sent("👢 已踢出并拉黑用户 10086")
        helper.clear_history()

        await helper.send_group_message("/group_info", group_id="g1")
        helper.assert_reply_sent("📊 群信息 (ID: g1)")
        helper.clear_history()
    finally:
        status.global_access_manager = original_manager

    print("\n✅ group_management 测试通过")


if __name__ == "__main__":
    asyncio.run(run_group_management_tests())
