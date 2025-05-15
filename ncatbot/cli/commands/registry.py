"""Command registry system for NcatBot CLI."""

from typing import Any, Callable, Dict, List, Optional, Tuple


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
    ):
        self.name = name
        self.func = func
        self.description = description
        self.usage = usage
        self.help_text = help_text or description
        self.aliases = aliases or []
        self.category = category or "General"


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
            print(f"不支持的命令: {command_name}")
            return None

        cmd = self.commands[command_name]
        return cmd.func(*args, **kwargs)

    def get_help(self, category: Optional[str] = None) -> str:
        """Generate help text for all commands or a specific category"""
        if category and category not in self.categories:
            return f"未知的分类: {category}"

        help_lines = []
        if category:
            help_lines.append(f"{category} 分类的命令:")
            commands = [
                (name, self.commands[name]) for name in self.categories[category]
            ]
        else:
            help_lines.append("支持的命令:")
            commands = sorted(self.commands.items())

        for i, (name, cmd) in enumerate(commands, 1):
            # Include aliases in the help text if they exist
            alias_text = f" (别名: {', '.join(cmd.aliases)})" if cmd.aliases else ""
            help_lines.append(f"{i}. '{cmd.usage}' - {cmd.description}{alias_text}")

        return "\n".join(help_lines)

    def get_categories(self) -> List[str]:
        """Get list of all command categories"""
        return sorted(self.categories.keys())

    def get_commands_by_category(self, category: str) -> List[Tuple[str, Command]]:
        """Get all commands in a specific category"""
        if category not in self.categories:
            return []
        return [(name, self.commands[name]) for name in self.categories[category]]


# Create a global command registry
registry = CommandRegistry()
