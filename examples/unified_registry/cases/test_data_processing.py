import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

from .plugins.data_processing_plugin import DataProcessingPlugin


async def run_data_processing_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(DataProcessingPlugin)

    await helper.send_private_message('/text_stats "hello world\nline2"')
    helper.assert_reply_sent("文本统计:")
    helper.clear_history()

    print("\n✅ data_processing 测试通过")


if __name__ == "__main__":
    asyncio.run(run_data_processing_tests())
