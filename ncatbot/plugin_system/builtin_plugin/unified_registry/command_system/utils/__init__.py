"""命令系统工具模块

提供各种工具类和规格定义。
"""

from .specs import CommandSpec, OptionSpec, OptionGroupSpec, ParameterSpec, FuncSpec
from .exceptions import (
    CommandSystemError,
    CommandRegistrationError,
    ParameterError,
    ValidationError,
    ArgumentError,
    OptionError,
    CommandNotFoundError,
    TypeConversionError,
    MultiTypeConversionError,
    MutuallyExclusiveError,
    MissingRequiredParameterError,
    TooManyArgumentsError,
    ErrorHandler,
)

__all__ = [
    "CommandSpec",
    "OptionSpec",
    "OptionGroupSpec",
    "ParameterSpec",
    "FuncSpec",
    "CommandSystemError",
    "CommandRegistrationError",
    "ParameterError",
    "ValidationError",
    "ArgumentError",
    "OptionError",
    "CommandNotFoundError",
    "TypeConversionError",
    "MultiTypeConversionError",
    "MutuallyExclusiveError",
    "MissingRequiredParameterError",
    "TooManyArgumentsError",
    "ErrorHandler",
]
