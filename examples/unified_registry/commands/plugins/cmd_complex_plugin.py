from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.plugin_system import option, param
from ncatbot.core.event import BaseMessageEvent


class CmdComplexPlugin(NcatBotPlugin):
    name = "CmdComplexPlugin"
    version = "1.0.0"

    async def on_load(self):
        pass

    @command_registry.command("backup", description="数据备份")
    @option(short_name="c", long_name="compress", help="压缩备份")
    @option(short_name="e", long_name="encrypt", help="加密备份")
    @param(name="path", default="/backup", help="备份路径")
    @param(name="exclude", default="", help="排除文件")
    async def backup_cmd(
        self,
        event: BaseMessageEvent,
        database: str,
        path: str = "/backup",
        exclude: str = "",
        compress: bool = False,
        encrypt: bool = False,
    ):
        result = f"备份数据库 {database} 到 {path}"
        features = []
        if compress:
            features.append("压缩")
        if encrypt:
            features.append("加密")
        if exclude:
            features.append(f"排除: {exclude}")
        if features:
            result += f" ({', '.join(features)})"
        await event.reply(result)

    @command_registry.command("send", description="发送消息")
    @option(short_name="a", long_name="all", help="发送给所有人")
    async def send_cmd(
        self, event: BaseMessageEvent, message: str, target: str = "", all: bool = False
    ):
        if all:
            await event.reply(f"广播消息: {message}")
        elif target:
            await event.reply(f"发送给 {target}: {message}")
        else:
            await event.reply(f"发送消息: {message} (默认发送给当前用户)")
