from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent


class ParamsTypesPlugin(NcatBotPlugin):
    name = "ParamsTypesPlugin"
    version = "1.0.0"

    async def on_load(self):
        pass

    @command_registry.command("math")
    async def math_cmd(self, event: BaseMessageEvent, a: int, b: float, c: bool):
        result = f"整数: {a} (类型: {type(a).__name__})\n"
        result += f"浮点数: {b} (类型: {type(b).__name__})\n"
        result += f"布尔值: {c} (类型: {type(c).__name__})"
        await event.reply(result)

    @command_registry.command("toggle")
    async def toggle_cmd(self, event: BaseMessageEvent, feature: str, enabled: bool):
        status = "启用" if enabled else "禁用"
        await event.reply(f"功能 '{feature}' 已{status}")

    @command_registry.command("divide")
    async def divide_cmd(self, event: BaseMessageEvent, a: float, b: float):
        try:
            if b == 0:
                await event.reply("❌ 错误: 除数不能为0")
                return
            result = a / b
            await event.reply(f"✅ {a} ÷ {b} = {result}")
        except Exception as e:
            await event.reply(f"❌ 计算错误: {e}")
