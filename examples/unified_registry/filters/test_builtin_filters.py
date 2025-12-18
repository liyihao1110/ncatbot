import asyncio
from ncatbot.utils.testing import TestClient, TestHelper
from ncatbot.utils import status

from .plugins.filters_builtin_plugin import BuiltinFiltersPlugin


async def run_builtin_filters_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(BuiltinFiltersPlugin)

    # group_filter 触发（任意群聊文本即可）
    await helper.send_group_message("任意群聊消息")
    helper.assert_reply_sent("收到一条群聊消息")
    helper.clear_history()

    # private_filter 触发
    await helper.send_private_message("任意私聊消息")
    helper.assert_reply_sent("收到一条私聊消息")
    helper.clear_history()

    # admin_filter 命令（ban）
    original_manager = status.global_access_manager

    class _MockManager:
        def user_has_role(self, user_id, role):
            return False

    status.global_access_manager = _MockManager()
    try:
        await helper.send_private_message("/ban 10086")
        helper.assert_no_reply()
        helper.clear_history()

        class _AdminManager:
            def user_has_role(self, user_id, role):
                return True

        status.global_access_manager = _AdminManager()

        await helper.send_private_message("/ban 10086")
        helper.assert_reply_sent("已封禁用户: 10086")
        helper.clear_history()
    finally:
        status.global_access_manager = original_manager

    # admin_filter 纯过滤函数
    original_manager = status.global_access_manager

    class _AdminManager2:
        def user_has_role(self, user_id, role):
            return True

    status.global_access_manager = _AdminManager2()
    try:
        await helper.send_private_message("任意消息")
        helper.assert_reply_sent("收到一条管理员消息")
        helper.clear_history()
    finally:
        status.global_access_manager = original_manager

    # root_filter 命令
    # 将当前用户模拟为 root（沿用权限接口，直接返回 True）
    original_manager = status.global_access_manager

    class _RootManager:
        def user_has_role(self, user_id, role):
            return True

    status.global_access_manager = _RootManager()
    try:
        await helper.send_private_message("/shutdown")
        helper.assert_reply_sent("正在关闭机器人...")
        helper.clear_history()
    finally:
        status.global_access_manager = original_manager

    print("\n✅ builtin_filters 测试通过")


if __name__ == "__main__":
    asyncio.run(run_builtin_filters_tests())
