"""
过滤器系统示例：来自 docs/plugin_system/UnifiedRegistry-过滤器系统.md

运行：python -m examples.unified_registry.filters_examples
"""

import asyncio
from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry import command_registry
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.decorators import (
    group_only,
    private_only,
    admin_only,
    root_only,
    on_message,
    admin_group_only,
    admin_private_only,
)
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils.testing import TestClient, TestHelper


class FiltersDemo(NcatBotPlugin):
    name = "FiltersDemo"
    version = "1.0.0"

    async def on_load(self):
        pass

    @group_only
    @command_registry.command("group_cmd")
    def group_cmd(self, event: BaseMessageEvent):
        return "这是群聊命令"

    @private_only
    @command_registry.command("private_cmd")
    def private_cmd(self, event: BaseMessageEvent):
        return "这是私聊命令"

    @admin_only
    @command_registry.command("admin_cmd")
    def admin_cmd(self, event: BaseMessageEvent):
        return "管理员命令"

    @root_only
    @command_registry.command("shutdown")
    def shutdown_cmd(self, event: BaseMessageEvent):
        return "正在关闭机器人..."

    @admin_group_only
    @command_registry.command("grouppromote")
    def grouppromote_cmd(self, event: BaseMessageEvent, user_id: str):
        return f"在群聊中提升用户权限: {user_id}"

    @admin_private_only
    @command_registry.command("adminpanel")
    def adminpanel_cmd(self, event: BaseMessageEvent):
        return "管理员私聊面板"


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
    client.register_plugin(FiltersDemo)

    # 群聊/私聊过滤
    await helper.send_private_message("/group_cmd")
    print("/group_cmd (私聊)", "->", helper.get_latest_reply())
    helper.clear_history()

    await helper.send_group_message("/group_cmd", group_id="20001")
    print("/group_cmd (群聊)", "->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    await helper.send_private_message("/private_cmd")
    print("/private_cmd (私聊)", "->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    # 管理员/Root 由于权限系统未在测试环境中配置，这里仅展示调用
    await helper.send_private_message("/admin_cmd")
    print("/admin_cmd ->", helper.get_latest_reply())
    helper.clear_history()

    await helper.send_private_message("/shutdown")
    print("/shutdown ->", helper.get_latest_reply())
    helper.clear_history()

    # 组合装饰器
    await helper.send_group_message("/grouppromote 12345", group_id="20001")
    print("/grouppromote (群聊)", "->", helper.get_latest_reply())
    helper.clear_history()

    await helper.send_private_message("/adminpanel")
    print("/adminpanel (私聊)", "->", helper.get_latest_reply())
    helper.clear_history()

    print("✅ filters 示例完成")


if __name__ == "__main__":
    asyncio.run(main())


