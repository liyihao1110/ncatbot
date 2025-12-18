from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent


class ParamsBasicPlugin(NcatBotPlugin):
    name = "ParamsBasicPlugin"
    version = "1.0.0"

    async def on_load(self):
        pass

    @command_registry.command("echo")
    async def echo_cmd(self, event: BaseMessageEvent, text: str):
        await event.reply(f"你说的是: {text}")

    @command_registry.command("calc")
    async def calc_cmd(self, event: BaseMessageEvent, a: int, op: str, b: int):
        if op == "add":
            await event.reply(f"{a} + {b} = {a + b}")
        elif op == "sub":
            await event.reply(f"{a} - {b} = {a - b}")
        else:
            await event.reply("支持的操作: add, sub")

    @command_registry.command("say")
    async def say_cmd(self, event: BaseMessageEvent, message: str):
        await event.reply(f"机器人说: {message}")
