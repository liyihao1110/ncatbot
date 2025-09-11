"""
参数解析示例：来自 docs/plugin_system/UnifiedRegistry-参数解析.md

运行：python -m examples.unified_registry.params_examples
"""

import asyncio
from ncatbot.plugin_system.builtin_mixin import NcatBotPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry import command_registry
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry.decorators import option, param
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils.testing import TestClient, TestHelper


class ParamsDemo(NcatBotPlugin):
    name = "ParamsDemo"
    version = "1.0.0"

    async def on_load(self):
        pass

    @command_registry.command("echo")
    def echo_cmd(self, event: BaseMessageEvent, text: str):
        return f"你说的是: {text}"

    @command_registry.command("calc")
    def calc_cmd(self, event: BaseMessageEvent, a: int, op: str, b: int):
        if op == "add":
            return f"{a} + {b} = {a + b}"
        elif op == "sub":
            return f"{a} - {b} = {a - b}"
        else:
            return "支持的操作: add, sub"

    @command_registry.command("say")
    def say_cmd(self, event: BaseMessageEvent, message: str):
        return f"机器人说: {message}"

    @command_registry.command("list")
    @option(short_name="l", help="长格式显示")
    @option(short_name="a", help="显示隐藏文件")
    @option(short_name="h", help="人类可读格式")
    def list_cmd(self, event: BaseMessageEvent, path: str = ".", l: bool = False, a: bool = False, h: bool = False):
        result = f"列出目录: {path}"
        opts = []
        if l:
            opts.append("长格式")
        if a:
            opts.append("显示隐藏")
        if h:
            opts.append("人类可读")
        if opts:
            result += f" ({', '.join(opts)})"
        return result

    @command_registry.command("backup")
    @option(long_name="compress", help="压缩备份文件")
    @option(long_name="encrypt", help="加密备份文件")
    @option(long_name="verify", help="验证备份完整性")
    def backup_cmd(self, event: BaseMessageEvent, source: str, compress: bool = False, encrypt: bool = False, verify: bool = False):
        result = f"备份 {source}"
        feats = []
        if compress:
            feats.append("压缩")
        if encrypt:
            feats.append("加密")
        if verify:
            feats.append("验证")
        if feats:
            result += f" [{', '.join(feats)}]"
        return result

    @command_registry.command("deploy")
    @param(name="env", default="dev", help="部署环境")
    @param(name="port", default=8080, help="端口号")
    @param(name="workers", default=4, help="工作进程数")
    def deploy_cmd(self, event: BaseMessageEvent, app: str, env: str = "dev", port: int = 8080, workers: int = 4):
        return f"部署 {app}: 环境={env}, 端口={port}, 进程={workers}"

    @command_registry.command("process")
    @option(short_name="v", long_name="verbose", help="详细输出")
    @option(short_name="f", long_name="force", help="强制执行")
    @param(name="output", default="result.txt", help="输出文件")
    @param(name="format", default="json", help="输出格式")
    def process_cmd(self, event: BaseMessageEvent, input_file: str, output: str = "result.txt", format: str = "json", verbose: bool = False, force: bool = False):
        result = f"处理文件: {input_file} → {output} ({format}格式)"
        if verbose:
            result += " [详细模式]"
        if force:
            result += " [强制模式]"
        return result

    @command_registry.command("math")
    def math_cmd(self, event: BaseMessageEvent, a: int, b: float, c: bool):
        return f"整数: {a} (类型: {type(a).__name__})\n浮点数: {b} (类型: {type(b).__name__})\n布尔值: {c} (类型: {type(c).__name__})"

    @command_registry.command("toggle2")
    def toggle2_cmd(self, event: BaseMessageEvent, feature: str, enabled: bool):
        return f"功能 '{feature}' 已{'启用' if enabled else '禁用'}"

    @command_registry.command("divide")
    def divide_cmd(self, event: BaseMessageEvent, a: float, b: float):
        if b == 0:
            return "❌ 错误: 除数不能为0"
        return f"✅ {a} ÷ {b} = {a / b}"


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
    client.register_plugin(ParamsDemo)

    cases = [
        "/echo hello",
        "/calc 10 add 20",
        "/calc 100 sub 50",
        "/say \"hello world\"",
        "/list -la",
        "/list -lah /home",
        "/backup /data --compress --encrypt",
        "/deploy myapp --env=prod --port=9000 --workers=8",
        "/process data.csv -v --output=output.xml --format=xml",
        "/math 42 3.14 true",
        "/toggle2 debug false",
        "/divide 6 3",
    ]

    for cmd in cases:
        await helper.send_private_message(cmd)
        reply = helper.get_latest_reply()
        print(cmd, "->", extract_text(reply["message"]) if reply else None)
        helper.clear_history()

    print("✅ params 示例完成")


if __name__ == "__main__":
    asyncio.run(main())


