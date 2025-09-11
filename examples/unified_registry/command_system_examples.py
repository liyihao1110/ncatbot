"""
命令系统示例：来自 docs/plugin_system/UnifiedRegistry-命令系统.md

运行：python -m examples.unified_registry.command_system_examples
"""

import asyncio
from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry import command_registry
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry.decorators import option, param, option_group
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils.testing import TestClient, TestHelper


class CommandSystemDemo(NcatBotPlugin):
    name = "CommandSystemDemo"
    version = "1.0.0"

    async def on_load(self):
        pass

    # 基础命令
    @command_registry.command("hello")
    def hello_cmd(self, event: BaseMessageEvent):
        return "Hello, World!"

    @command_registry.command("ping")
    def ping_cmd(self, event: BaseMessageEvent):
        return "pong!"

    # 带描述
    @command_registry.command("info", description="获取机器人信息")
    def info_cmd(self, event: BaseMessageEvent):
        return "这是一个示例机器人"

    # 别名
    @command_registry.command("status", aliases=["stat", "st"], description="查看状态")
    def status_cmd(self, event: BaseMessageEvent):
        return "机器人运行正常"

    # 参数类型
    @command_registry.command("echo")
    def echo_cmd(self, event: BaseMessageEvent, text: str):
        return f"你说的是: {text}"

    @command_registry.command("add")
    def add_cmd(self, event: BaseMessageEvent, a: int, b: int):
        return f"{a} + {b} = {a + b}"

    @command_registry.command("calculate")
    def calculate_cmd(self, event: BaseMessageEvent, x: float, y: float):
        return f"{x} * {y} = {x * y}"

    @command_registry.command("toggle")
    def toggle_cmd(self, event: BaseMessageEvent, enabled: bool):
        return f"功能已{'开启' if enabled else '关闭'}"

    # 选项与参数
    @command_registry.command("deploy", description="部署应用")
    @option(short_name="v", long_name="verbose", help="详细信息")
    @option(short_name="f", long_name="force", help="强制部署")
    def deploy_cmd(self, event: BaseMessageEvent, app_name: str, verbose: bool = False, force: bool = False):
        result = f"部署应用: {app_name}"
        if force:
            result += " (强制模式)"
        if verbose:
            result += "\n详细信息: 开始部署流程..."
        return result

    @command_registry.command("config", description="配置设置")
    @param(name="env", default="dev", help="运行环境")
    @param(name="port", default=8080, help="端口号")
    def config_cmd(self, event: BaseMessageEvent, env: str = "dev", port: int = 8080):
        return f"配置: 环境={env}, 端口={port}"

    @command_registry.command("export", description="导出数据")
    @option_group(choices=["json", "csv", "xml"], name="format", default="json", help="输出格式")
    def export_cmd(self, event: BaseMessageEvent, data_type: str, format: str = "json"):
        return f"导出 {data_type} 数据为 {format} 格式"


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
    client.register_plugin(CommandSystemDemo)

    commands = [
        "/hello",
        "/ping",
        "/info",
        "/status",
        "/echo 文本",
        "/add 3 5",
        "/calculate 3.0 2.5",
        "/toggle true",
        "/deploy myapp -v -f",
        "/config --env=prod --port=9000",
        "/export users --csv",
    ]

    for cmd in commands:
        await helper.send_private_message(cmd)
        reply = helper.get_latest_reply()
        print(cmd, "->", extract_text(reply["message"]) if reply else None)
        helper.clear_history()

    print("✅ command_system 示例完成")


if __name__ == "__main__":
    asyncio.run(main())


