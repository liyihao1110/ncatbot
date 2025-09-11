"""
测试指南示例：来自 docs/plugin_system/UnifiedRegistry-测试指南.md

运行：python -m examples.unified_registry.testing_guide_examples
"""

import asyncio
from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry import command_registry
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils.testing import TestClient, TestHelper


class TestPlugin(NcatBotPlugin):
    name = "TestPlugin"
    version = "1.0.0"

    async def on_load(self):
        pass

    @command_registry.command("hello")
    def hello_cmd(self, event: BaseMessageEvent):
        return "你好！"

    @command_registry.command("echo")
    def echo_cmd(self, event: BaseMessageEvent, text: str):
        return f"回声: {text}"

    @command_registry.command("calc")
    def calc_cmd(self, event: BaseMessageEvent, a: int, b: int, op: str = "add"):
        if op == "add":
            return f"结果: {a + b}"
        return f"不支持的操作: {op}"


def extract_text(message_segments):
    return "".join(
        seg.get("data", {}).get("text", "")
        for seg in message_segments
        if seg.get("type") == "text"
    )


async def main():
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(TestPlugin)

    # 基础命令
    await helper.send_private_message("/hello")
    print("/hello ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    # 带参数
    await helper.send_private_message("/echo 测试文本")
    print("/echo ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    # 复杂参数
    await helper.send_private_message("/calc 5 3")
    print("/calc ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    # 错误处理
    await helper.send_private_message("/calc 5")  # 缺少参数
    print("/calc 缺参 ->", helper.get_latest_reply())
    helper.clear_history()

    await helper.send_private_message("/calc abc def")  # 类型错误
    print("/calc 类型错误 ->", helper.get_latest_reply())
    helper.clear_history()

    print("✅ testing_guide 示例完成")


if __name__ == "__main__":
    asyncio.run(main())


