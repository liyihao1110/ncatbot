"""词法分析器模块

支持现代命令行参数解析，包括：
- 短选项：-v, -xvf
- 长选项：--verbose, --help
- 参数赋值：-p=1234, --para=value
- 转义字符串："有 空格 的 字符串"
"""

from .tokenizer import (
    StringTokenizer,
    Token,
    TokenType,
    QuoteState,
    QuoteMismatchError,
    InvalidEscapeSequenceError,
    Element,
    ParsedCommand,
    AdvancedCommandParser,
    NonTextToken,
)
from .message_tokenizer import MessageTokenizer, parse_message_command

__all__ = [
    "StringTokenizer",
    "Token",
    "TokenType",
    "QuoteState",
    "QuoteMismatchError",
    "InvalidEscapeSequenceError",
    "Element",
    "ParsedCommand",
    "AdvancedCommandParser",
    "NonTextToken",
    "MessageTokenizer",
    "parse_message_command",
]
