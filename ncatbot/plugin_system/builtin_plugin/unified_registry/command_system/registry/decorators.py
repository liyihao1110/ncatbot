"""装饰器框架

提供直观的装饰器API，支持链式调用和参数验证。
"""

from typing import Callable, Any, List, Optional, Dict, Type

from ..utils import CommandRegistrationError, OptionSpec, OptionGroupSpec, ParameterSpec

# TODO: 融合 option、param 以及函数签名自检测
# TODO: 支持类型系统


def check_is_command(func: Callable):
    if hasattr(func, "__is_command__"):
        raise CommandRegistrationError(
            func.__name__,
            "必须注册完参数后才能注册命令",
            details="必须注册完参数后才能注册命令",
            suggestions="将注册命令的装饰器移到最上方",
        )


def option(
    short_name: Optional[str] = None, long_name: Optional[str] = None, help: str = ""
):
    # TODO: 通过注解明确行为
    """选项装饰器

    用于添加命令选项（-v, --verbose等）。

    Args:
        short_name: 短选项名，如 "v"
        long_name: 长选项名，如 "verbose"
        help: 帮助文本
        default: 默认值
        group: 选项组ID

    Examples:
        @option("v", "verbose", help="详细输出")
    """

    def decorator(func: Callable) -> Callable:
        check_is_command(func)
        # 确保函数有选项列表属性
        if not hasattr(func, "__command_options__"):
            func.__command_options__ = []

        # 创建选项规格
        option_spec = OptionSpec(
            short_name=short_name, long_name=long_name, description=help
        )

        func.__command_options__.append(option_spec)
        return func

    return decorator


def option_group(
    choices: List[str],
    name: str,
    default: str,
    help: str = "",
):
    # 用于指定基于字符串值选项
    # 仅 --xml, --yaml 格式等
    # TODO: 通过注解明确行为
    """选项组装饰器

    Args:
        choices (List[str]): 选项列表
        name: 选项组名称
        default (str): 默认选项
        help (str, optional): 帮助文本. Defaults to "".

    Examples:
        @exclusive_option_group(choices=["xml", "yaml"], default="xml", help="输出格式")
    """

    def decorator(func: Callable) -> Callable:
        # 确保函数有选项列表属性
        check_is_command(func)
        if not hasattr(func, "__command_option_groups__"):
            func.__command_option_groups__ = []

        # 创建选项规格
        option_spec = OptionGroupSpec(
            choices=choices, name=name, default=default, description=help
        )

        func.__command_option_groups__.append(option_spec)
        return func

    return decorator


def param(
    name: str,
    default: Any = None,
    required: Optional[bool] = False,
    help: str = "",
    choices: Optional[List[Any]] = None,
    validator: Optional[Callable] = None,
    examples: Optional[List[str]] = None,
    type_hints: Optional[Dict[Type, str]] = None,
    type_examples: Optional[Dict[Type, List[str]]] = None,
):
    """参数装饰器

    用于添加命名参数（--name=value）。

    Args:
        name: 参数名（不包含--前缀）
        default: 默认值
        required: 是否必需（None表示自动判断）
        help: 帮助文本
        choices: 可选值列表
        validator: 自定义验证器
        examples: 使用示例
        type_hints: 各类型的提示文本
        type_examples: 各类型的示例

    Examples:
        @param("env", type=str, choices=["dev", "test", "prod"])
        @param("port", type=int, default=8080)
        @param("input", type=[str, MessageSegment],
               type_hints={str: "文件路径", MessageSegment: "图片文件"})
    """

    def decorator(func: Callable) -> Callable:
        # 确保函数有参数列表属性
        check_is_command(func)

        if not hasattr(func, "__command_params__"):
            func.__command_params__ = []

        # 创建参数规格
        param_spec = ParameterSpec(
            name=name,
            default=default,
            required=required,
            description=help,
            choices=choices,
            validator=validator,
            examples=examples or [],
            type_hints=type_hints or {},
            type_examples=type_examples or {},
            is_named=True,
            is_positional=False,
        )

        func.__command_params__.append(param_spec)
        return func

    return decorator
