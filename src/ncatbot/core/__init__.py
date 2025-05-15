"""NcatBot core components."""

from ncatbot.core.client import BotClient
from ncatbot.core.install import install_napcat
from ncatbot.core.message import (
    At,
    BaseMessage,
    GroupMessage,
    MessageChain,
    PrivateMessage,
    Text,
)

__all__ = [
    # Client
    "BotClient",
    # Installation utilities
    "install_napcat",
    # Message types
    "BaseMessage",
    "GroupMessage",
    "PrivateMessage",
    "MessageChain",
    "Text",
    "At",
]
