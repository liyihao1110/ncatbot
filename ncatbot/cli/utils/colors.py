"""Color utilities for NcatBot CLI."""

import os
import sys
from typing import Dict


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""

    # Text colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Text styles
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"

    # Reset
    RESET = "\033[0m"


# Semantic color scheme
class ColorScheme:
    """Semantic color scheme for NcatBot CLI."""

    HEADER = Colors.BOLD + Colors.CYAN
    TITLE = Colors.BOLD + Colors.BLUE
    COMMAND = Colors.BOLD + Colors.GREEN
    CATEGORY = Colors.BOLD + Colors.YELLOW
    DESCRIPTION = Colors.WHITE
    USAGE = Colors.CYAN
    ALIAS = Colors.MAGENTA
    ERROR = Colors.RED
    SUCCESS = Colors.GREEN
    WARNING = Colors.YELLOW
    INFO = Colors.BLUE
    RESET = Colors.RESET


# Check if colors should be enabled (can be disabled for non-ANSI terminals)
def is_color_supported() -> bool:
    """Check if the terminal supports ANSI color codes."""
    # Check if FORCE_COLOR is set to disable colors
    if os.environ.get("FORCE_COLOR", "").lower() in ("0", "false", "no"):
        return False

    # Check if NO_COLOR is set (standard for disabling colors)
    if os.environ.get("NO_COLOR") is not None:
        return False

    # Check if it's Windows without colorama
    if sys.platform == "win32" and not (
        "ANSICON" in os.environ or "WT_SESSION" in os.environ
    ):
        try:
            import colorama

            colorama.init()
            return True
        except ImportError:
            return False

    # Most Unix terminals support colors
    return True


# Get color function based on terminal support
_color_enabled = is_color_supported()


def colorize(text: str, color: str, always: bool = False) -> str:
    """Colorize text string with ANSI color codes if colors are enabled.

    Args:
        text: Text to colorize
        color: ANSI color code
        always: If True, always apply color even if colors are disabled

    Returns:
        Colorized text string
    """
    if _color_enabled or always:
        return f"{color}{text}{Colors.RESET}"
    return text


# Generate convenient color functions
def command(text: str) -> str:
    """Format text as a command."""
    return colorize(text, ColorScheme.COMMAND)


def category(text: str) -> str:
    """Format text as a category."""
    return colorize(text, ColorScheme.CATEGORY)


def description(text: str) -> str:
    """Format text as a description."""
    return colorize(text, ColorScheme.DESCRIPTION)


def usage(text: str) -> str:
    """Format text as a usage example."""
    return colorize(text, ColorScheme.USAGE)


def alias(text: str) -> str:
    """Format text as an alias."""
    return colorize(text, ColorScheme.ALIAS)


def error(text: str) -> str:
    """Format text as an error message."""
    return colorize(text, ColorScheme.ERROR)


def success(text: str) -> str:
    """Format text as a success message."""
    return colorize(text, ColorScheme.SUCCESS)


def warning(text: str) -> str:
    """Format text as a warning message."""
    return colorize(text, ColorScheme.WARNING)


def info(text: str) -> str:
    """Format text as an info message."""
    return colorize(text, ColorScheme.INFO)


def header(text: str) -> str:
    """Format text as a header."""
    return colorize(text, ColorScheme.HEADER)


def title(text: str) -> str:
    """Format text as a title."""
    return colorize(text, ColorScheme.TITLE)


# Category-specific colors
CATEGORY_COLORS: Dict[str, str] = {
    "sys": Colors.YELLOW,
    "info": Colors.CYAN,
    "plg": Colors.GREEN,
}


def get_category_color(category_name: str) -> str:
    """Get color for a specific category.

    Args:
        category_name: Name of the category

    Returns:
        ANSI color code for the category
    """
    return CATEGORY_COLORS.get(category_name.lower(), Colors.WHITE)
