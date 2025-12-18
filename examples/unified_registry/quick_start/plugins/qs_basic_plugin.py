from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.plugin_system import option, param
from ncatbot.core.event import BaseMessageEvent


class QSBasicPlugin(NcatBotPlugin):
    name = "QSBasicPlugin"
    version = "1.0.0"
    author = "doc-verify"
    description = "快速开始-基础、简单命令、参数命令、选项、别名"

    async def on_load(self):
        pass

    # 简单命令
    @command_registry.command("hello")
    async def hello_cmd(self, event: BaseMessageEvent):
        await event.reply("你好！我是机器人。")

    @command_registry.command("ping")
    async def ping_cmd(self, event: BaseMessageEvent):
        await event.reply("pong!")

    # 带参数
    @command_registry.command("echo")
    async def echo_cmd(self, event: BaseMessageEvent, text: str):
        await event.reply(f"你说的是: {text}")

    @command_registry.command("add")
    async def add_cmd(self, event: BaseMessageEvent, a: int, b: int):
        result = a + b
        await event.reply(f"{a} + {b} = {result}")

    # 复杂参数和选项
    @command_registry.command("deploy", description="部署应用")
    @option(short_name="v", long_name="verbose", help="显示详细信息")
    @option(short_name="f", long_name="force", help="强制部署")
    @param(name="env", default="dev", help="部署环境")
    async def deploy_cmd(
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
        await event.reply(result)

    # 别名
    @command_registry.command("status", aliases=["stat", "st"], description="查看状态")
    async def status_cmd(self, event: BaseMessageEvent):
        await event.reply("机器人运行正常")
