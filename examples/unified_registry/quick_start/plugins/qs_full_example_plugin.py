from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.plugin_system import group_only, admin_only
from ncatbot.plugin_system import option, param
from ncatbot.core.event import BaseMessageEvent


class QSFullExamplePlugin(NcatBotPlugin):
    name = "QSFullExamplePlugin"
    version = "1.0.0"
    author = "doc-verify"
    description = "快速开始-完整插件示例"

    async def on_load(self):
        pass

    @command_registry.command("hello", aliases=["hi"], description="问候命令")
    async def hello_cmd(self, event: BaseMessageEvent):
        await event.reply(f"你好！用户 {event.user_id}")

    @command_registry.command("calc", description="简单计算器")
    async def calc_cmd(self, event: BaseMessageEvent, a: int, op: str, b: int):
        if op == "add":
            await event.reply(f"{a} + {b} = {a + b}")
        elif op == "sub":
            await event.reply(f"{a} - {b} = {a - b}")
        elif op == "mul":
            await event.reply(f"{a} * {b} = {a * b}")
        elif op == "div":
            if b == 0:
                await event.reply("错误：除数不能为0")
            else:
                await event.reply(f"{a} / {b} = {a / b}")
        else:
            await event.reply("支持的操作: add, sub, mul, div")

    @group_only
    @admin_only
    @command_registry.command("announce", description="发布公告")
    @option(short_name="a", long_name="all", help="发送给所有群员")
    async def announce_cmd(self, event: BaseMessageEvent, message: str, all: bool = False):
        result = f"公告: {message}"
        if all:
            result += " [发送给所有群员]"
        await event.reply(result)

    @command_registry.command("greet", description="个性化问候")
    @param(name="name", default="朋友", help="要问候的名字")
    async def greet_cmd(self, event: BaseMessageEvent, name: str = "朋友"):
        await event.reply(f"你好，{name}！欢迎使用机器人。")


