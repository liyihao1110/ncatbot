import asyncio
from ncatbot.utils.testing import TestClient, TestHelper
from ncatbot.utils import status

from .plugins.qs_external_funcs import QSExternalFuncsPlugin


async def run_external_funcs_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(QSExternalFuncsPlugin)

    await helper.send_private_message("/outside")
    helper.assert_reply_sent("这是在插件类外定义的命令")
    helper.clear_history()

    # 非管理员不可执行 external_admin
    original_manager = status.global_access_manager

    class _MockManager:
        def user_has_role(self, user_id, role):
            return False

    status.global_access_manager = _MockManager()
    try:
        await helper.send_private_message("/external_admin do")
        helper.assert_no_reply()
        helper.clear_history()

        class _AdminManager:
            def user_has_role(self, user_id, role):
                return True

        status.global_access_manager = _AdminManager()

        await helper.send_private_message("/external_admin do")
        helper.assert_reply_sent("执行管理员操作: do")
        helper.clear_history()
    finally:
        status.global_access_manager = original_manager

    await helper.send_private_message("/inside")
    helper.assert_reply_sent("这是类内的命令")
    helper.clear_history()

    print("\n✅ external_funcs 测试通过")


if __name__ == "__main__":
    asyncio.run(run_external_funcs_tests())
