import asyncio
from ncatbot.utils.testing import TestClient, TestHelper
from ncatbot.utils import status

from .plugins.qs_permissions_plugin import QSPermissionsPlugin
from .plugins.qs_pure_filters import QSPureFilterPlugin


async def run_permissions_and_filters_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(QSPermissionsPlugin)

    # group_filter: 群聊可用
    await helper.send_group_message("/groupinfo", group_id="10001")
    helper.assert_reply_sent("当前群聊ID: 10001")
    helper.clear_history()
    # 私聊不可用
    await helper.send_private_message("/groupinfo")
    helper.assert_no_reply()
    helper.clear_history()

    # private_filter: 私聊可用
    await helper.send_private_message("/private")
    helper.assert_reply_sent("这是一个私聊命令")
    helper.clear_history()
    # 群聊不可用
    await helper.send_group_message("/private")
    helper.assert_no_reply()
    helper.clear_history()

    # admin_filter: 仅管理员
    original_manager = status.global_access_manager
    class _MockManager:
        def user_has_role(self, user_id, role):
            return False
    status.global_access_manager = _MockManager()
    try:
        await helper.send_private_message("/admin", user_id="normal")
        helper.assert_no_reply()
        helper.clear_history()

        class _AdminManager:
            def user_has_role(self, user_id, role):
                return True
        status.global_access_manager = _AdminManager()

        await helper.send_private_message("/admin", user_id="admin")
        helper.assert_reply_sent("你是管理员！")
        helper.clear_history()
    finally:
        status.global_access_manager = original_manager

    # 纯过滤器
    client.register_plugin(QSPureFilterPlugin)
    await helper.send_group_message("任意群聊文本")
    helper.assert_reply_sent("收到一条群聊消息")
    helper.clear_history()
    await helper.send_private_message("任意私聊文本")
    helper.assert_no_reply()
    helper.clear_history()

    print("\n✅ permissions_and_filters 测试通过")


if __name__ == "__main__":
    asyncio.run(run_permissions_and_filters_tests())


