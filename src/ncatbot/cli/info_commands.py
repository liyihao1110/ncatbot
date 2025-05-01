"""Help and information commands for NcatBot CLI."""

from typing import Optional

from ncatbot.cli.registry import registry
from ncatbot.cli.utils import get_qq


@registry.register("help", "显示命令帮助信息", "help [命令名]", aliases=["h", "?"])
def show_command_help(command_name: Optional[str] = None) -> None:
    """Show detailed help for a specific command or all commands."""
    if command_name is None:
        # Show general help
        qq = get_qq()
        show_help(qq)
        return

    # Show help for a specific command
    if command_name not in registry.commands:
        print(f"不支持的命令: {command_name}")
        return

    cmd = registry.commands[command_name]
    print(f"命令: {cmd.name}")
    print(f"用法: {cmd.usage}")
    print(f"描述: {cmd.description}")
    if cmd.help_text and cmd.help_text != cmd.description:
        print(f"详细说明: {cmd.help_text}")


@registry.register("version", "显示 NcatBot 版本", "version", aliases=["v", "ver"])
def show_version() -> None:
    """Show the version of NcatBot."""
    try:
        import pkg_resources

        version = pkg_resources.get_distribution("ncatbot").version
        print(f"NcatBot 版本: {version}")
    except (ImportError, pkg_resources.DistributionNotFound):
        print("无法获取 NcatBot 版本信息")


def show_help(qq: str) -> None:
    """Show general help information."""
    print("欢迎使用 NcatBot CLI!")
    print(f"当前 QQ 号为: {qq}")
    print(registry.get_help())
