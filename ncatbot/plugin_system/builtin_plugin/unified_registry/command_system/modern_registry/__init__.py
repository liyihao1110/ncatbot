"""现代化命令注册系统

提供直观、类型安全的命令注册API，支持：
- 多重装饰器组合
- 多类型参数支持（Union types）
- 自动类型转换和验证
- 智能错误提示和帮助生成
- 位置参数默认值
- 选项和命名参数
- 非文本元素支持

使用示例：
    from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.modern_registry import registry
    
    @registry.command("hello")
    def hello_command(event):
        return "Hello, World!"
    
    @registry.command("greet")
    @registry.option("-v", "--verbose", help="详细输出")
    @registry.param("target", type=CommonUnionTypes.USER_IDENTIFIER, help="目标用户")
    def greet_command(event, name: str, target, verbose=False):
        return f"Hello {name}!"
"""

from .registry import ModernRegistry, CommandGroup, CommandDefinition
from .decorators import (
    option, param, option_group,
    str_param, int_param, bool_param, user_param,
    text_or_image_param, choice_param
)
from .exceptions import (
    CommandRegistrationError, ParameterError, ValidationError,
    CommandNotFoundError, ArgumentError, OptionError,
    TypeConversionError, MultiTypeConversionError,
    MutuallyExclusiveError, MissingRequiredParameterError,
    TooManyArgumentsError, ErrorHandler
)
from .type_system import (
    ParameterType, OptionType, UnionType, CommonUnionTypes,
    TypeValidator, TypeConverter, BuiltinConverters, BuiltinValidators,
    TypeMeta, type_registry
)
from .specs import ParameterSpec, OptionSpec, OptionGroup, SpecBuilder
from .help_system import HelpGenerator, format_error_with_help

# 创建全局注册实例
registry = ModernRegistry()

__all__ = [
    # 主要注册实例
    "registry",
    
    # 核心类
    "ModernRegistry", "CommandGroup", "CommandDefinition",
    
    # 装饰器
    "option", "param", "option_group",
    "str_param", "int_param", "bool_param", "user_param",
    "text_or_image_param", "choice_param",
    
    # 异常类
    "CommandRegistrationError", "ParameterError", "ValidationError",
    "CommandNotFoundError", "ArgumentError", "OptionError",
    "TypeConversionError", "MultiTypeConversionError",
    "MutuallyExclusiveError", "MissingRequiredParameterError",
    "TooManyArgumentsError", "ErrorHandler",
    
    # 类型系统
    "ParameterType", "OptionType", "UnionType", "CommonUnionTypes",
    "TypeValidator", "TypeConverter", "BuiltinConverters", "BuiltinValidators",
    "TypeMeta", "type_registry",
    
    # 规格系统
    "ParameterSpec", "OptionSpec", "OptionGroup", "SpecBuilder",
    
    # 帮助系统
    "HelpGenerator", "format_error_with_help",
]
