"""Help and information commands for NcatBot CLI."""

import os
import sys
from typing import Optional

from ncatbot.cli.commands.registry import registry
from ncatbot.cli.utils.colors import (
    alias,
    category,
    command,
    description,
    error,
    header,
    info,
    title,
    usage,
    warning,
)
from ncatbot.utils import ncatbot_config as config


@registry.register(
    "help",
    "显示命令帮助信息",
    "help [命令名|分类名]",
    aliases=["h", "?"],
    category="info",
)
def show_command_help(command_name: Optional[str] = None) -> None:
    """Show detailed help for a specific command, category, or all commands."""
    if command_name is None:
        # Show simplified help with only important commands
        show_help(config.bt_uin)
        return

    # Check if it's a category
    if command_name in registry.get_categories():
        print(registry.get_help(command_name))
        return

    # Check if command_name is an alias
    cmd_name = command_name
    if command_name in registry.aliases:
        cmd_name = registry.aliases[command_name]
        print(f"'{command(command_name)}' 是 '{command(cmd_name)}' 的别名")

    # Show help for a specific command
    if cmd_name not in registry.commands:
        print(error(f"不支持的命令: {command_name}"))
        return

    cmd = registry.commands[cmd_name]
    print(f"{header('命令:')} {command(cmd.name)}")
    print(f"{header('分类:')} {category(cmd.category)}")
    print(f"{header('用法:')} {usage(cmd.usage)}")
    print(f"{header('描述:')} {description(cmd.description)}")
    if cmd.help_text and cmd.help_text != cmd.description:
        print(f"{header('详细说明:')} {description(cmd.help_text)}")
    if cmd.aliases:
        print(f"{header('别名:')} {', '.join([alias(a) for a in cmd.aliases])}")


@registry.register(
    "meta",
    "显示 NcatBot 元信息",
    "meta",
    aliases=["info", "version", "v"],
    category="info",
    show_in_help=False,
)
def show_meta() -> None:
    """Show the version of NcatBot."""
    try:
        import pkg_resources

        version = pkg_resources.get_distribution("ncatbot").version
        print(f"{header('NcatBot 版本:')} {info(version)}")
        print(f"{header('Python 版本:')} {info(sys.version)}")
        print(f"{header('操作系统:')} {info(sys.platform)}")
        print(f"{header('工作目录:')} {info(os.getcwd())}")
        print(f"{header('QQ 号:')} {info(config.bt_uin or '未设置')}")
    except (ImportError, pkg_resources.DistributionNotFound):
        print(error("无法获取 NcatBot 版本信息"))


@registry.register(
    "categories",
    "显示所有命令分类",
    "categories [分类名]",
    aliases=["cat"],
    category="info",
    show_in_help=True,
)
def show_categories(filter_category: str = None) -> None:
    """Show all command categories or commands in a specific category.

    Args:
        filter_category: Optional category to filter by (info, plg, sys)
    """
    categories = registry.get_categories()
    if not categories:
        print(warning("没有可用的命令分类"))
        return

    # Filter by category if specified
    if filter_category:
        # Check if the filter is valid
        valid_filters = ["info", "plg", "sys"]
        if filter_category.lower() not in valid_filters:
            print(warning(f"未知的分类: {filter_category}"))
            print(
                info(f"可用的分类: {', '.join([category(c) for c in valid_filters])}")
            )
            return

        # Show commands in the specified category
        filter_cat = filter_category.lower()
        commands = registry.get_commands_by_category(filter_cat)
        if not commands:
            print(warning(f"分类 {category(filter_cat)} 中没有命令"))
            return

        print(header(f"分类 {category(filter_cat)} 中的命令:"))
        for i, (cmd_name, cmd) in enumerate(commands, 1):
            alias_text = ""
            if cmd.aliases:
                aliases = [alias(a) for a in cmd.aliases]
                alias_text = f" (别名: {', '.join(aliases)})"
            print(
                f"{i}. {command(cmd.usage)} - {description(cmd.description)}{alias_text}"
            )
        return

    # Show all categories
    print(header("可用的命令分类:"))
    for i, cat_name in enumerate(categories, 1):
        commands = registry.get_commands_by_category(cat_name)
        print(f"{i}. {category(cat_name)} ({info(str(len(commands)))} 个命令)")


def show_help(qq: str) -> None:
    """Show simplified general help information."""
    print(title("欢迎使用 NcatBot CLI!"))
    print(f"{header('当前 QQ 号为:')} {info(qq)}")
    print("")
    print(f"使用 {command('help <命令名>')} 查看特定命令的详细帮助")
    print(f"使用 {command('help <分类名>')} 查看特定分类的命令")
    print(f"使用 {command('cat')} 查看所有命令分类")
    print(
        f"使用 {command('cat <分类名>')} 查看特定分类下的命令，如 {command('cat info')}"
    )
    print("")
    print(header("常用命令:"))

    # Get the most important commands to display
    print(registry.get_help(only_important=True))
