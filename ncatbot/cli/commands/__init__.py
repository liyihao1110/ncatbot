from ncatbot.cli.commands.config_commands import set_qq
from ncatbot.cli.commands.info_commands import show_meta
from ncatbot.cli.commands.plugin_commands import (
    create_plugin_template,
    install,
    list_plugins,
    list_remote_plugins,
    remove_plugin,
)
from ncatbot.cli.commands.registry import registry
from ncatbot.cli.commands.system_commands import exit_cli, start, update

__all__ = [
    "registry",
    "show_meta",
    "set_qq",
    "install",
    "create_plugin_template",
    "remove_plugin",
    "list_plugins",
    "list_remote_plugins",
    "start",
    "update",
    "exit_cli",
]
