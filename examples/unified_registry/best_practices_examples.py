"""
最佳实践部分的基础命令验证：来自 docs/plugin_system/UnifiedRegistry-最佳实践.md

运行：python -m examples.unified_registry.best_practices_examples
"""

import asyncio
from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry import command_registry
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.decorators import admin_only
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils.testing import TestClient, TestHelper


class WellOrganizedPlugin(NcatBotPlugin):
    name = "WellOrganizedPlugin"
    version = "1.0.0"
    author = "docs"
    description = "结构良好的插件示例"

    async def on_load(self):
        self.stats = {"command_count": 0}
        self.config = {"max_users": 100}

    @command_registry.command("hello", description="基础问候命令")
    def hello_cmd(self, event: BaseMessageEvent):
        self.stats["command_count"] += 1
        return "你好！"

    @admin_only
    @command_registry.command("stats", description="查看统计信息")
    def stats_cmd(self, event: BaseMessageEvent):
        return f"命令使用次数: {self.stats['command_count']}"

    @command_registry.command("calc", description="简单计算器")
    def calc_cmd(self, event: BaseMessageEvent, a: int, b: int):
        return f"结果: {a + b}"


def extract_text(message_segments):
    text = ""
    for seg in message_segments:
        if isinstance(seg, dict) and seg.get("type") == "text":
            text += seg.get("data", {}).get("text", "")
    return text


async def main():
    client = TestClient()
    helper = TestHelper(client)
    client.start()
    client.register_plugin(WellOrganizedPlugin)

    await helper.send_private_message("/hello")
    print("/hello ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    await helper.send_private_message("/calc 2 3")
    print("/calc ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    await helper.send_private_message("/stats")
    print("/stats ->", helper.get_latest_reply())  # 需要管理员权限
    helper.clear_history()

    print("✅ best_practices 示例完成")


if __name__ == "__main__":
    asyncio.run(main())


