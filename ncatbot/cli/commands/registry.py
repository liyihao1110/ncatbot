"""Command registry system for NcatBot CLI."""

from typing import Any, Callable, Dict, List, Optional, Tuple

from ncatbot.cli.utils.colors import (
    Colors,
)
from ncatbot.cli.utils.colors import alias as alias_color
from ncatbot.cli.utils.colors import category as cat_color
from ncatbot.cli.utils.colors import command as cmd_color
from ncatbot.cli.utils.colors import description as desc_color
from ncatbot.cli.utils.colors import (
    get_category_color,
)
from ncatbot.cli.utils.colors import header as header_color


class Command:
    """Command class to represent a CLI command"""

    def __init__(
        self,
        name: str,
        func: Callable,
        description: str,
        usage: str,
        help_text: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        category: Optional[str] = None,
        show_in_help: bool = True,
    ):
        self.name = name
        self.func = func
        self.description = description
        self.usage = usage
        self.help_text = help_text or description
        self.aliases = aliases or []
        self.category = category or "General"
        self.show_in_help = show_in_help


class CommandRegistry:
    """Registry for CLI commands"""

    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.aliases: Dict[str, str] = {}
        self.categories: Dict[str, List[str]] = {}

    def register(
        self,
        name: str,
        description: str,
        usage: str,
        help_text: Optional[str] = None,
        aliases: Optional[List[str]] = None,
        category: Optional[str] = None,
        requires_qq: bool = False,
        show_in_help: bool = True,
    ):
        """Decorator to register a command"""

        def decorator(func: Callable) -> Callable:
            cmd = Command(
                name=name,
                func=func,
                description=description,
                usage=usage,
                help_text=help_text,
                aliases=aliases,
                category=category,
                show_in_help=show_in_help,
            )
            # Store requires_qq as an attribute of the command
            self.commands[name] = cmd

            # Register aliases
            if aliases:
                for alias in aliases:
                    self.aliases[alias] = name

            # Register category
            if category:
                if category not in self.categories:
                    self.categories[category] = []
                self.categories[category].append(name)

            return func

        return decorator

    def execute(self, command_name: str, *args, **kwargs) -> Any:
        """Execute a command by name"""
        # Check if the command is an alias
        if command_name in self.aliases:
            command_name = self.aliases[command_name]

        if command_name not in self.commands:
            print(f"不支持的命令: {cmd_color(command_name)}")
            return None

        cmd = self.commands[command_name]
        return cmd.func(*args, **kwargs)

    def get_help(
        self, category: Optional[str] = None, only_important: bool = False
    ) -> str:
        """Generate help text for all commands or a specific category

        Args:
            category: Optional category to filter commands by
            only_important: If True, only show commands with show_in_help=True
        """
        if category and category not in self.categories:
            return f"未知的分类: {cat_color(category)}"

        help_lines = []
        if category:
            cat_title = cat_color(category)
            help_lines.append(f"{cat_title} 分类的命令:")
            commands = [
                (name, self.commands[name])
                for name in self.categories[category]
                if not only_important or self.commands[name].show_in_help
            ]
        else:
            all_commands = sorted(self.commands.items())
            if only_important:
                commands = [
                    (name, cmd) for name, cmd in all_commands if cmd.show_in_help
                ]
            else:
                commands = all_commands

            if commands:
                help_lines.append(header_color("支持的命令:"))

        for i, (name, cmd) in enumerate(commands, 1):
            # Include aliases in the help text if they exist
            alias_text = ""
            if cmd.aliases:
                aliases = [alias_color(a) for a in cmd.aliases]
                alias_text = f" (别名: {', '.join(aliases)})"

            # Get category color for this command
            cat_color_code = get_category_color(cmd.category)
            # Format the command with its category's color
            colored_usage = f"{Colors.BOLD}{cat_color_code}{cmd.usage}{Colors.RESET}"

            help_lines.append(
                f"{i}. '{colored_usage}' - {desc_color(cmd.description)}{alias_text}"
            )

        return "\n".join(help_lines)

    def get_categories(self) -> List[str]:
        """Get list of all command categories"""
        return sorted(self.categories.keys())

    def get_commands_by_category(
        self, category: str, only_important: bool = False
    ) -> List[Tuple[str, Command]]:
        """Get all commands in a specific category

        Args:
            category: The category to get commands for
            only_important: If True, only return commands with show_in_help=True
        """
        if category not in self.categories:
            return []
        commands = [(name, self.commands[name]) for name in self.categories[category]]
        if only_important:
            return [(name, cmd) for name, cmd in commands if cmd.show_in_help]
        return commands


# Create a global command registry
registry = CommandRegistry()
