"""Help and information commands for NcatBot CLI."""

import os
import sys
from typing import Optional

from ncatbot.cli.commands.registry import registry
from ncatbot.utils import ncatbot_config as config


@registry.register(
    "help",
    "显示命令帮助信息",
    "help [命令名|分类名]",
    aliases=["h", "?"],
    category="Information",
)
def show_command_help(command_name: Optional[str] = None) -> None:
    """Show detailed help for a specific command, category, or all commands."""
    if command_name is None:
        # Show general help
        show_help(config.bt_uin)
        return

    # Check if it's a category
    if command_name in registry.get_categories():
        print(registry.get_help(command_name))
        return

    # Show help for a specific command
    if command_name not in registry.commands:
        print(f"不支持的命令: {command_name}")
        return

    cmd = registry.commands[command_name]
    print(f"命令: {cmd.name}")
    print(f"分类: {cmd.category}")
    print(f"用法: {cmd.usage}")
    print(f"描述: {cmd.description}")
    if cmd.help_text and cmd.help_text != cmd.description:
        print(f"详细说明: {cmd.help_text}")
    if cmd.aliases:
        print(f"别名: {', '.join(cmd.aliases)}")


@registry.register(
    "meta",
    "显示 NcatBot 元信息",
    "meta",
    aliases=["info", "version", "v"],
    category="Information",
)
def show_meta() -> None:
    """Show the version of NcatBot."""
    try:
        import pkg_resources

        version = pkg_resources.get_distribution("ncatbot").version
        print(f"NcatBot 版本: {version}")
        print(f"Python 版本: {sys.version}")
        print(f"操作系统: {sys.platform}")
        print(f"工作目录: {os.getcwd()}")
        print(f"QQ 号: {config.bt_uin or '未设置'}")
    except (ImportError, pkg_resources.DistributionNotFound):
        print("无法获取 NcatBot 版本信息")


@registry.register(
    "categories",
    "显示所有命令分类",
    "categories",
    aliases=["cat"],
    category="Information",
)
def show_categories() -> None:
    """Show all command categories."""
    categories = registry.get_categories()
    if not categories:
        print("没有可用的命令分类")
        return

    print("可用的命令分类:")
    for i, category in enumerate(categories, 1):
        commands = registry.get_commands_by_category(category)
        print(f"{i}. {category} ({len(commands)} 个命令)")


def show_help(qq: str) -> None:
    """Show general help information."""
    print("欢迎使用 NcatBot CLI!")
    print(f"当前 QQ 号为: {qq}")
    print("\n使用 'help <分类名>' 查看特定分类的命令")
    print("使用 'help <命令名>' 查看特定命令的详细帮助")
    print("\n" + registry.get_help())
