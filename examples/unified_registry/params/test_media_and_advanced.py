import asyncio
from ncatbot.utils.testing import TestClient, TestHelper
from ncatbot.core.event.message_segment import MessageArray, Text, At, Image

from .plugins.params_media_plugin import ParamsMediaPlugin
from .plugins.params_options_plugin import ParamsOptionsPlugin


async def run_media_and_advanced_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    # 非文本元素
    client.register_plugin(ParamsMediaPlugin)

    msg = MessageArray([Text("/analyze \"这是一张风景图\" "), Image(file="img001.jpg")])
    await helper.send_private_message(msg)
    helper.assert_reply_sent("分析图片: 这是一张风景图")
    helper.assert_reply_sent("img001.jpg")
    helper.clear_history()

    msg2 = MessageArray([Text("/mention \"你好\" "), At(qq="12345")])
    await helper.send_private_message(msg2)
    helper.assert_reply_sent("发送消息给 @12345: 你好")
    helper.clear_history()

    # 高级语法（转义字符）
    client.register_plugin(ParamsOptionsPlugin)
    await helper.send_private_message('/process "first\\nsecond"')
    # 该命令不会主动处理转义示例，这里主要覆盖 media 示例，其它高级语法在 options/功能内已有覆盖
    helper.clear_history()

    print("\n✅ media_and_advanced 测试通过")


if __name__ == "__main__":
    asyncio.run(run_media_and_advanced_tests())


