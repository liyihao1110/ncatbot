import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

from .plugins.cmd_complex_plugin import CmdComplexPlugin


async def run_complex_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(CmdComplexPlugin)

    await helper.send_private_message("/backup mydb")
    helper.assert_reply_sent("备份数据库 mydb 到 /backup")
    helper.clear_history()

    await helper.send_private_message("/backup mydb --path=/data/backup -c -e")
    helper.assert_reply_sent("备份数据库 mydb 到 /data/backup (压缩, 加密)")
    helper.clear_history()

    await helper.send_private_message("/backup mydb --exclude=logs")
    helper.assert_reply_sent("备份数据库 mydb 到 /backup (排除: logs)")
    helper.clear_history()

    await helper.send_private_message("/send hello")
    helper.assert_reply_sent("发送消息: hello (默认发送给当前用户)")
    helper.clear_history()

    await helper.send_private_message("/send \"你好\" tom")
    helper.assert_reply_sent("发送给 tom: 你好")
    helper.clear_history()

    await helper.send_private_message("/send \"广播\" -a")
    helper.assert_reply_sent("广播消息: 广播")
    helper.clear_history()

    print("\n✅ complex 测试通过")


if __name__ == "__main__":
    asyncio.run(run_complex_tests())


