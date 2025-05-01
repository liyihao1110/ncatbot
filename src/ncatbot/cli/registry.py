"""Command registry system for NcatBot CLI."""

from typing import Any, Callable, Dict, List, Optional


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
    ):
        self.name = name
        self.func = func
        self.description = description
        self.usage = usage
        self.help_text = help_text or description
        self.aliases = aliases or []


class CommandRegistry:
    """Registry for CLI commands"""

    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.aliases: Dict[str, str] = {}

    def register(
        self,
        name: str,
        description: str,
        usage: str,
        help_text: Optional[str] = None,
        aliases: Optional[List[str]] = None,
    ):
        """Decorator to register a command"""

        def decorator(func: Callable) -> Callable:
            cmd = Command(name, func, description, usage, help_text, aliases)
            self.commands[name] = cmd

            # Register aliases
            if aliases:
                for alias in aliases:
                    self.aliases[alias] = name

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

        return self.commands[command_name].func(*args, **kwargs)

    def get_help(self) -> str:
        """Generate help text for all commands"""
        help_lines = ["支持的命令:"]
        for i, (name, cmd) in enumerate(sorted(self.commands.items()), 1):
            # Include aliases in the help text if they exist
            alias_text = f" (别名: {', '.join(cmd.aliases)})" if cmd.aliases else ""
            help_lines.append(f"{i}. '{cmd.usage}' - {cmd.description}{alias_text}")
        return "\n".join(help_lines)


# Create a global command registry
registry = CommandRegistry()
