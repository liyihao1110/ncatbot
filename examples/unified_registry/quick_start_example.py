"""
快速开始示例：来自 docs/plugin_system/UnifiedRegistry-快速开始.md

运行：python -m examples.unified_registry.quick_start_example
"""

import asyncio
from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry import command_registry
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.decorators import (
    group_only,
    private_only,
    admin_only,
)
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry.decorators import (
    option,
    param,
)
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils.testing import TestClient, TestHelper


class HelloPlugin(NcatBotPlugin):
    name = "HelloPlugin"
    version = "1.0.0"
    author = "docs"
    description = "快速开始演示插件"

    async def on_load(self):
        pass

    # 简单问候命令
    @command_registry.command("hello")
    def hello_cmd(self, event: BaseMessageEvent):
        return "你好！我是机器人。"

    # ping 命令
    @command_registry.command("ping")
    def ping_cmd(self, event: BaseMessageEvent):
        return "pong!"

    # 带位置参数
    @command_registry.command("echo")
    def echo_cmd(self, event: BaseMessageEvent, text: str):
        return f"你说的是: {text}"

    @command_registry.command("add")
    def add_cmd(self, event: BaseMessageEvent, a: int, b: int):
        result = a + b
        return f"{a} + {b} = {result}"

    # 过滤器示例
    @group_only
    @command_registry.command("groupinfo")
    def group_info_cmd(self, event: BaseMessageEvent):
        return f"当前群聊ID: {event.group_id}"

    @private_only
    @command_registry.command("private")
    def private_cmd(self, event: BaseMessageEvent):
        return "这是一个私聊命令"

    @admin_only
    @command_registry.command("admin")
    def admin_cmd(self, event: BaseMessageEvent):
        return "你是管理员！"

    # 复杂参数和选项
    @command_registry.command("deploy", description="部署应用")
    @option(short_name="v", long_name="verbose", help="显示详细信息")
    @option(short_name="f", long_name="force", help="强制部署")
    @param(name="env", default="dev", help="部署环境")
    def deploy_cmd(
        self,
        event: BaseMessageEvent,
        app_name: str,
        env: str = "dev",
        verbose: bool = False,
        force: bool = False,
    ):
        result = f"正在部署 {app_name} 到 {env} 环境"
        if force:
            result += " (强制模式)"
        if verbose:
            result += "\n详细信息: 开始部署流程..."
        return result

    # 别名
    @command_registry.command("status", aliases=["stat", "st"], description="查看状态")
    def status_cmd(self, event: BaseMessageEvent):
        return "机器人运行正常"


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

    # 注册插件
    client.register_plugin(HelloPlugin)

    # 1) 基础命令
    await helper.send_private_message("/hello")
    print("/hello ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    await helper.send_private_message("/ping")
    print("/ping ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    # 2) 位置参数
    await helper.send_private_message("/echo 测试文本")
    print("/echo ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    await helper.send_private_message("/add 10 20")
    print("/add ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    # 3) 过滤器：群聊/私聊/管理员
    await helper.send_private_message("/groupinfo")
    print("/groupinfo (私聊) ->", helper.get_latest_reply())  # 预期 None 或无回复
    helper.clear_history()

    await helper.send_group_message("/groupinfo", group_id="10001")
    print("/groupinfo (群聊) ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    await helper.send_private_message("/private")
    print("/private (私聊) ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    # 注意：admin_only 需要权限系统支持，这里只演示指令发送
    await helper.send_private_message("/admin")
    print("/admin (私聊) ->", helper.get_latest_reply())
    helper.clear_history()

    # 4) 复杂参数/选项
    await helper.send_private_message("/deploy myapp")
    print("/deploy myapp ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    await helper.send_private_message("/deploy myapp --env=prod -v")
    print("/deploy env+v ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    await helper.send_private_message("/deploy myapp --force")
    print("/deploy force ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    # 5) 别名
    await helper.send_private_message("/st")
    print("/st ->", extract_text(helper.get_latest_reply()["message"]))
    helper.clear_history()

    print("✅ quick_start 示例完成")


if __name__ == "__main__":
    asyncio.run(main())


