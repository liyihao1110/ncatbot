"""命令子系统

现代化的命令行参数解析系统，支持：
- 短选项：-v, -xvf
- 长选项：--verbose, --help
- 参数赋值：-p=1234, --para=value
- 转义字符串："有 空格 的 字符串"

使用示例：
    from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system import StringTokenizer, AdvancedCommandParser

    tokenizer = StringTokenizer('deploy app --env=prod -v "config file"')
    tokens = tokenizer.tokenize()
    parser = AdvancedCommandParser()
    result = parser.parse(tokens)
"""

from .analyzer import FuncAnalyser, get_subclass_recursive
from .registry import command_registry
from .lexer import (
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
    MessageTokenizer,
    parse_message_command,
)

__all__ = [
    # 分析器
    "FuncAnalyser",
    "get_subclass_recursive",
    # 命令相关
    "CommandGroup",
    "CommandRouter",
    # 词法分析器
    "StringTokenizer",
    "Token",
    "TokenType",
    "QuoteState",
    "QuoteMismatchError",
    "InvalidEscapeSequenceError",
    # 命令解析器
    "Element",
    "ParsedCommand",
    "AdvancedCommandParser",
    "NonTextToken",
    # 消息级别解析器
    "MessageTokenizer",
    "parse_message_command",
    # 注册器实例
    "command_registry",
]
