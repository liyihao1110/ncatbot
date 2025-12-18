import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

from .plugins.qa_bot_plugin import QABotPlugin


async def run_qa_bot_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(QABotPlugin)

    await helper.send_private_message('/ask "你好呀"')
    helper.assert_reply_sent("你好！我是问答机器人")
    helper.clear_history()

    await helper.send_private_message('/ask "今天天气如何"')
    helper.assert_reply_sent("抱歉，我还不能查询天气")
    helper.clear_history()

    await helper.send_private_message('/add_qa "猫叫什么" "就叫小猫咪"')
    helper.assert_reply_sent("✅ 已添加问答")
    helper.clear_history()

    await helper.send_private_message("/list_qa")
    helper.assert_reply_sent("📚 问答库：")
    helper.clear_history()

    await helper.send_private_message("/time")
    helper.assert_reply_sent("🕐 当前时间：")
    helper.clear_history()

    print("\n✅ qa_bot 测试通过")


if __name__ == "__main__":
    asyncio.run(run_qa_bot_tests())
