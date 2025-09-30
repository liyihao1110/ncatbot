from ncatbot.plugin_system import NcatBotPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.plugin_system import option, param, option_group
from ncatbot.core.event import BaseMessageEvent


class ParamsOptionsPlugin(NcatBotPlugin):
    name = "ParamsOptionsPlugin"
    version = "1.0.0"

    async def on_load(self):
        pass

    @command_registry.command("list")
    @option(short_name="l", help="长格式显示")
    @option(short_name="a", help="显示隐藏文件")
    @option(short_name="h", help="人类可读格式")
    async def list_cmd(
        self,
        event: BaseMessageEvent,
        path: str = ".",
        l: bool = False,
        a: bool = False,
        h: bool = False,
    ):
        result = f"列出目录: {path}"
        options = []
        if l:
            options.append("长格式")
        if a:
            options.append("显示隐藏")
        if h:
            options.append("人类可读")
        if options:
            result += f" ({', '.join(options)})"
        await event.reply(result)

    @command_registry.command("backup")
    @option(long_name="compress", help="压缩备份文件")
    @option(long_name="encrypt", help="加密备份文件")
    @option(long_name="verify", help="验证备份完整性")
    async def backup_cmd(
        self,
        event: BaseMessageEvent,
        source: str,
        compress: bool = False,
        encrypt: bool = False,
        verify: bool = False,
    ):
        result = f"备份 {source}"
        features = []
        if compress:
            features.append("压缩")
        if encrypt:
            features.append("加密")
        if verify:
            features.append("验证")
        if features:
            result += f" [{', '.join(features)}]"
        await event.reply(result)

    @command_registry.command("deploy")
    @param(name="env", default="dev", help="部署环境")
    @param(name="port", default=8080, help="端口号")
    @param(name="workers", default=4, help="工作进程数")
    async def deploy_cmd(
        self,
        event: BaseMessageEvent,
        app: str,
        env: str = "dev",
        port: int = 8080,
        workers: int = 4,
    ):
        await event.reply(f"部署 {app}: 环境={env}, 端口={port}, 进程={workers}")

    @command_registry.command("process")
    @option(short_name="v", long_name="verbose", help="详细输出")
    @option(short_name="f", long_name="force", help="强制执行")
    @param(name="output", default="result.txt", help="输出文件")
    @param(name="format", default="json", help="输出格式")
    async def process_cmd(
        self,
        event: BaseMessageEvent,
        input_file: str,
        output: str = "result.txt",
        format: str = "json",
        verbose: bool = False,
        force: bool = False,
    ):
        result = f"处理文件: {input_file} → {output} ({format}格式)"
        if verbose:
            result += " [详细模式]"
        if force:
            result += " [强制模式]"
        await event.reply(result)

    @command_registry.command("export")
    @option_group(
        choices=["json", "csv", "xml"], name="format", default="json", help="输出格式"
    )
    async def export_cmd(
        self, event: BaseMessageEvent, data_type: str, format: str = "json"
    ):
        await event.reply(f"导出 {data_type} 数据为 {format} 格式")
