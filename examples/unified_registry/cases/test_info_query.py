import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

from .plugins.info_query_plugin import InfoQueryPlugin


async def run_info_query_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(InfoQueryPlugin)

    await helper.send_private_message("/weather 北京")
    helper.assert_reply_sent("北京 天气")
    helper.clear_history()

    await helper.send_private_message("/weather 北京")
    helper.assert_reply_sent("来自缓存")
    helper.clear_history()

    await helper.send_private_message("/translate 你好 --target=en")
    helper.assert_reply_sent("Hello")
    helper.clear_history()

    await helper.send_private_message("/translate 你好 --target=ja")
    helper.assert_reply_sent("こんにちは")
    helper.clear_history()

    await helper.send_private_message("/translate 你好 --target=zz")
    helper.assert_reply_sent("❌ 不支持的目标语言")
    helper.clear_history()

    await helper.send_private_message("/search golang")
    helper.assert_reply_sent("搜索 'golang' 的结果")
    helper.clear_history()

    await helper.send_private_message("/search python -l")
    helper.assert_reply_sent("搜索 'python' 的结果")
    helper.clear_history()

    print("\n✅ info_query 测试通过")


if __name__ == "__main__":
    asyncio.run(run_info_query_tests())
