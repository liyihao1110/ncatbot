import asyncio
from ncatbot.utils.testing import TestClient, TestHelper
from ncatbot.utils import status

from .plugins.filters_combo_plugin import ComboFiltersPlugin


async def run_combo_filters_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(ComboFiltersPlugin)

    # 管理员 + 群聊
    original_manager = status.global_access_manager

    class _AdminManager:
        def user_has_role(self, user_id, role):
            return True

    status.global_access_manager = _AdminManager()
    try:
        await helper.send_group_message("/grouppromote 10010")
        helper.assert_reply_sent("在群聊中提升用户权限: 10010")
        helper.clear_history()

        # 管理员 + 私聊
        await helper.send_private_message("/adminpanel")
        helper.assert_reply_sent("管理员私聊面板")
        helper.clear_history()

        # 手动组合：管理员 + 群聊（非命令）
        await helper.send_group_message("任意文本")
        helper.assert_reply_sent("收到一条管理员发送的群聊消息")
        helper.clear_history()
    finally:
        status.global_access_manager = original_manager

    # filters("admin_filter", "group_filter") + 命令
    original_manager = status.global_access_manager

    class _AdminManager2:
        def user_has_role(self, user_id, role):
            return True

    status.global_access_manager = _AdminManager2()
    try:
        await helper.send_group_message("/order")
        helper.assert_reply_sent("多重过滤器命令")
        helper.clear_history()
    finally:
        status.global_access_manager = original_manager

    print("\n✅ combo_filters 测试通过")


if __name__ == "__main__":
    asyncio.run(run_combo_filters_tests())
