"""命令系统异常定义

分层的异常系统，提供精确的错误信息和智能修正建议。
"""

from typing import Optional, List, Any, Dict
from dataclasses import dataclass


class CommandSystemError(Exception):
    """命令系统基础异常"""

    def __init__(
        self,
        message: str,
        details: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.details = details or ""
        self.suggestions = suggestions or []

    def __str__(self) -> str:
        result = self.message
        if self.details:
            result += f"\n详细信息: {self.details}"
        if self.suggestions:
            result += f"\n建议: {self.suggestions if isinstance(self.suggestions, str) else '; '.join(self.suggestions)}"
        return result


class CommandRegistrationError(CommandSystemError):
    """命令注册时错误 - 给开发者看的"""

    def __init__(self, command_name: str, message: str, **kwargs):
        self.command_name = command_name
        super().__init__(f"命令 '{command_name}' 注册失败: {message}", **kwargs)


class ParameterError(CommandSystemError):
    """参数定义错误"""

    def __init__(self, param_name: str, message: str, **kwargs):
        self.param_name = param_name
        super().__init__(f"参数 '{param_name}' 定义错误: {message}", **kwargs)


class ValidationError(CommandSystemError):
    """参数验证错误"""

    def __init__(self, param_name: str, value: Any, expected_type: str, **kwargs):
        self.param_name = param_name
        self.value = value
        self.expected_type = expected_type
        super().__init__(f"参数 '{param_name}' 验证失败", **kwargs)


class ArgumentError(CommandSystemError):
    """命令参数错误 - 给用户看的"""

    def __init__(self, command_name: str, message: str, **kwargs):
        self.command_name = command_name
        super().__init__(f"命令 '{command_name}' 参数错误: {message}", **kwargs)


class OptionError(CommandSystemError):
    """选项错误"""

    def __init__(self, option_name: str, message: str, **kwargs):
        self.option_name = option_name
        super().__init__(f"选项 '{option_name}' 错误: {message}", **kwargs)


class CommandNotFoundError(CommandSystemError):
    """命令不存在错误"""

    def __init__(self, command_name: str, available_commands: List[str], **kwargs):
        self.command_name = command_name
        self.available_commands = available_commands

        # 生成相似命令建议
        similar_commands = self._find_similar_commands(command_name, available_commands)
        suggestions = []
        if similar_commands:
            suggestions.append(f"你可能想要: {', '.join(similar_commands[:3])}")
        suggestions.append("输入 /help 查看所有可用命令")

        super().__init__(
            f"未知命令 '{command_name}'",
            details=f"可用命令: {', '.join(available_commands[:5])}{'...' if len(available_commands) > 5 else ''}",
            suggestions=suggestions,
            **kwargs,
        )

    def _find_similar_commands(self, target: str, commands: List[str]) -> List[str]:
        """查找相似的命令名"""
        import difflib

        return difflib.get_close_matches(target, commands, n=3, cutoff=0.6)


class TypeConversionError(ValidationError):
    """类型转换错误"""

    def __init__(
        self,
        param_name: str,
        value: Any,
        target_type: str,
        conversion_errors: List[str],
        **kwargs,
    ):
        self.conversion_errors = conversion_errors

        details = (
            f"值 '{value}' (类型: {type(value).__name__}) 无法转换为 {target_type}"
        )
        if conversion_errors:
            details += f"\n转换失败原因: {'; '.join(conversion_errors)}"

        super().__init__(param_name, value, target_type, details=details, **kwargs)


class MultiTypeConversionError(TypeConversionError):
    """多类型转换错误"""

    def __init__(
        self,
        param_name: str,
        value: Any,
        supported_types: List[str],
        type_errors: Dict[str, str],
        type_hints: Dict[str, str] = None,
        **kwargs,
    ):
        self.supported_types = supported_types
        self.type_errors = type_errors
        self.type_hints = type_hints or {}

        # 构建详细的错误信息
        details = f"值 '{value}' 无法转换为任何支持的类型\n"
        details += f"支持的类型: {', '.join(supported_types)}\n\n"

        details += "各类型转换失败原因:\n"
        for type_name, error in type_errors.items():
            details += f"  • {type_name}: {error}\n"

        if self.type_hints:
            details += "\n类型说明:\n"
            for type_name, hint in self.type_hints.items():
                details += f"  • {type_name}: {hint}\n"

        suggestions = ["请检查输入格式是否正确", "查看命令帮助了解正确的参数格式"]

        # 先调用父类构造函数
        super().__init__(
            param_name,
            value,
            f"({' 或 '.join(supported_types)})",
            list(type_errors.values()),
            **kwargs,
        )

        # 然后覆盖详细信息和建议
        if "details" not in kwargs:
            self.details = details
        if "suggestions" not in kwargs:
            self.suggestions = suggestions


class MutuallyExclusiveError(OptionError):
    """互斥选项错误"""

    def __init__(self, conflicting_options: List[str], **kwargs):
        self.conflicting_options = conflicting_options
        options_str = " 和 ".join(conflicting_options)
        super().__init__(
            options_str,
            f"选项 {options_str} 不能同时使用",
            suggestions=[f"请只选择其中一个: {', '.join(conflicting_options)}"],
            **kwargs,
        )


class MissingRequiredParameterError(ArgumentError):
    """缺少必需参数错误"""

    def __init__(self, command_name: str, param_name: str, param_type: str, **kwargs):
        self.param_name = param_name
        self.param_type = param_type

        super().__init__(
            command_name,
            f"缺少必需参数 '{param_name}'",
            details=f"参数类型: {param_type}",
            suggestions=[
                f"请提供 {param_name} 参数",
                f"输入 /{command_name} --help 查看详细用法",
            ],
            **kwargs,
        )


class TooManyArgumentsError(ArgumentError):
    """参数过多错误"""

    def __init__(
        self, command_name: str, expected_count: int, actual_count: int, **kwargs
    ):
        self.expected_count = expected_count
        self.actual_count = actual_count

        super().__init__(
            command_name,
            "参数过多",
            details=f"期望 {expected_count} 个参数，实际收到 {actual_count} 个",
            suggestions=[
                "检查是否有多余的参数",
                "使用引号包围包含空格的参数",
                f"输入 /{command_name} --help 查看正确用法",
            ],
            **kwargs,
        )


@dataclass
class ErrorContext:
    """错误上下文信息"""

    command_name: str
    input_text: str
    current_position: int
    available_commands: List[str]
    similar_commands: List[str]
    expected_parameters: List[str]
    provided_parameters: List[str]


class ErrorHandler:
    """统一错误处理器"""

    def __init__(self):
        self.error_formatters = {
            CommandNotFoundError: self._format_command_not_found,
            ArgumentError: self._format_argument_error,
            ValidationError: self._format_validation_error,
            MultiTypeConversionError: self._format_multi_type_error,
        }

    def format_error(
        self, error: CommandSystemError, context: Optional[ErrorContext] = None
    ) -> str:
        """格式化错误信息为用户友好的格式"""
        formatter = self.error_formatters.get(type(error), self._format_default)
        return formatter(error, context)

    def _format_command_not_found(
        self, error: CommandNotFoundError, context: Optional[ErrorContext]
    ) -> str:
        """格式化命令不存在错误"""
        msg = f"❌ {error.message}\n"

        if error.available_commands:
            # 显示相似命令
            similar = [
                cmd
                for cmd in error.available_commands
                if self._calculate_similarity(error.command_name, cmd) > 0.5
            ][:3]
            if similar:
                msg += f"💡 你可能想要: {', '.join(similar)}\n"

            # 显示部分可用命令
            msg += f"📋 可用命令: {', '.join(error.available_commands[:5])}"
            if len(error.available_commands) > 5:
                msg += "..."
            msg += "\n"

        msg += "❓ 输入 /help 查看所有命令"
        return msg

    def _format_argument_error(
        self, error: ArgumentError, context: Optional[ErrorContext]
    ) -> str:
        """格式化参数错误"""
        msg = f"❌ {error.message}\n"
        if error.details:
            msg += f"📝 {error.details}\n"
        if error.suggestions:
            msg += f"💡 建议: {'; '.join(error.suggestions)}"
        return msg

    def _format_validation_error(
        self, error: ValidationError, context: Optional[ErrorContext]
    ) -> str:
        """格式化验证错误"""
        msg = "❌ 参数验证失败\n"
        msg += f"📝 参数: {error.param_name}\n"
        msg += f"📝 输入值: {error.value}\n"
        msg += f"📝 期望类型: {error.expected_type}\n"
        if error.suggestions:
            msg += f"💡 {'; '.join(error.suggestions)}"
        return msg

    def _format_multi_type_error(
        self, error: MultiTypeConversionError, context: Optional[ErrorContext]
    ) -> str:
        """格式化多类型转换错误"""
        msg = f"❌ 参数 '{error.param_name}' 类型错误\n\n"
        msg += f"📝 您的输入: {error.value} ({type(error.value).__name__})\n\n"

        msg += "✅ 支持的类型:\n"
        for i, type_name in enumerate(error.supported_types, 1):
            msg += f"  {i}. {type_name}"
            if type_name in error.type_hints:
                msg += f" - {error.type_hints[type_name]}"
            msg += "\n"

        if error.suggestions:
            msg += f"\n💡 {'; '.join(error.suggestions)}"

        return msg

    def _format_default(
        self, error: CommandSystemError, context: Optional[ErrorContext]
    ) -> str:
        """默认错误格式化"""
        return f"❌ {error.message}"

    def _calculate_similarity(self, a: str, b: str) -> float:
        """计算字符串相似度"""
        import difflib

        return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()
