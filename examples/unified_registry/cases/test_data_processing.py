import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

from .plugins.data_processing_plugin import DataProcessingPlugin


async def run_data_processing_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(DataProcessingPlugin)

    csv_data = "col1,col2\n1,2\n3,4"
    await helper.send_private_message(f"/csv_analyze '{csv_data}' --header")
    helper.assert_reply_sent("CSV数据分析:")
    helper.assert_reply_sent("总行数: 2")
    helper.clear_history()

    await helper.send_private_message("/json_format '{""a"":1}'")
    helper.assert_reply_sent("JSON格式化完成")
    helper.clear_history()

    await helper.send_private_message("/text_stats 'hello world'\n'line2'")
    helper.assert_reply_sent("文本统计:")
    helper.clear_history()

    print("\n✅ data_processing 测试通过")


if __name__ == "__main__":
    asyncio.run(run_data_processing_tests())


