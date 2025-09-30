import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

from .plugins.params_types_plugin import ParamsTypesPlugin


async def run_types_and_errors_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(ParamsTypesPlugin)

    await helper.send_private_message("/math 42 3.14 true")
    helper.assert_reply_sent("整数: 42")
    helper.assert_reply_sent("浮点数: 3.14")
    helper.assert_reply_sent("布尔值: True")
    helper.clear_history()

    await helper.send_private_message("/math 100 2.5 false")
    helper.assert_reply_sent("整数: 100")
    helper.assert_reply_sent("浮点数: 2.5")
    helper.assert_reply_sent("布尔值: False")
    helper.clear_history()

    await helper.send_private_message("/toggle logging true")
    helper.assert_reply_sent("功能 'logging' 已启用")
    helper.clear_history()

    await helper.send_private_message("/toggle debug false")
    helper.assert_reply_sent("功能 'debug' 已禁用")
    helper.clear_history()

    await helper.send_private_message("/toggle cache 1")
    helper.assert_reply_sent("功能 'cache' 已启用")
    helper.clear_history()

    await helper.send_private_message("/divide 3 0")
    helper.assert_reply_sent("❌ 错误: 除数不能为0")
    helper.clear_history()

    await helper.send_private_message("/divide 4 2")
    helper.assert_reply_sent("✅ 4.0 ÷ 2.0 = 2.0")
    helper.clear_history()

    print("\n✅ types_and_errors 测试通过")


if __name__ == "__main__":
    asyncio.run(run_types_and_errors_tests())
