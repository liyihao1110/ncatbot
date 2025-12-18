import asyncio
from ncatbot.utils.testing import TestClient, TestHelper
from ncatbot.utils import status

from .plugins.qs_full_example_plugin import QSFullExamplePlugin


async def run_full_example_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(QSFullExamplePlugin)

    await helper.send_private_message("/hello", user_id="u1")
    helper.assert_reply_sent("你好！用户 u1")
    helper.clear_history()

    await helper.send_private_message("/calc 1 add 2")
    helper.assert_reply_sent("1 + 2 = 3")
    helper.clear_history()

    await helper.send_private_message("/calc 5 div 0")
    helper.assert_reply_sent("错误：除数不能为0")
    helper.clear_history()

    # announce 需要管理员+群聊
    original_manager = status.global_access_manager

    class _AdminManager:
        def user_has_role(self, user_id, role):
            return True

    status.global_access_manager = _AdminManager()
    try:
        await helper.send_group_message("/announce 大家好")
        helper.assert_reply_sent("公告: 大家好")
        helper.clear_history()

        await helper.send_group_message("/announce 欢迎 -a")
        helper.assert_reply_sent("公告: 欢迎 [发送给所有群员]")
        helper.clear_history()
    finally:
        status.global_access_manager = original_manager

    await helper.send_private_message("/greet")
    helper.assert_reply_sent("你好，朋友！欢迎使用机器人。")
    helper.clear_history()

    await helper.send_private_message("/greet 张三")
    helper.assert_reply_sent("你好，张三！欢迎使用机器人。")
    helper.clear_history()

    print("\n✅ full_example 测试通过")


if __name__ == "__main__":
    asyncio.run(run_full_example_tests())
