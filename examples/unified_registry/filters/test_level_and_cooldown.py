import asyncio
from ncatbot.utils.testing import TestClient, TestHelper

from .plugins.filters_level_and_cooldown_plugin import LevelAndCooldownPlugin


async def run_level_and_cooldown_tests():
    client = TestClient()
    helper = TestHelper(client)
    client.start()

    client.register_plugin(LevelAndCooldownPlugin)

    # LevelFilter(min_level=1) 恒通过（演示实现返回 1）
    await helper.send_private_message("任意文本触发高等级消息")
    helper.assert_reply_sent("收到一条高等级用户的消息")
    helper.clear_history()

    # 冷却命令：首次通过，立即再次调用应被限制（1秒门槛）
    await helper.send_private_message("/limited")
    helper.assert_reply_sent("有冷却限制的命令")
    helper.clear_history()

    await helper.send_private_message("/limited")
    helper.assert_no_reply()
    helper.clear_history()

    print("\n✅ level_and_cooldown 测试通过")


if __name__ == "__main__":
    asyncio.run(run_level_and_cooldown_tests())


