import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

from .plugins.web_api_plugin import WebAPIPlugin


async def run_web_api_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(WebAPIPlugin)

    await helper.send_private_message("/random_quote")
    helper.assert_reply_sent("今日名言")
    helper.clear_history()

    await helper.send_private_message("/mock_api")
    helper.assert_reply_sent("API响应 (users)")
    helper.clear_history()

    await helper.send_private_message("/mock_api --endpoint=stats")
    helper.assert_reply_sent("API响应 (stats)")
    helper.clear_history()

    await helper.send_private_message("/mock_api --endpoint=unknown")
    helper.assert_reply_sent("❌ 未知的API端点")
    helper.clear_history()

    print("\n✅ web_api 测试通过")


if __name__ == "__main__":
    asyncio.run(run_web_api_tests())
