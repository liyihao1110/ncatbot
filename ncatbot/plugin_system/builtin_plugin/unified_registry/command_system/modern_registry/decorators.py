"""装饰器框架

提供直观的装饰器API，支持链式调用和参数验证。
"""

from typing import Callable, Any, List, Optional, Dict, Union, Type
from functools import wraps

from .specs import ParameterSpec, OptionSpec, OptionGroup, OptionType
from .type_system import UnionType, CommonUnionTypes
from .exceptions import CommandRegistrationError, ParameterError


def option(short_name: Optional[str] = None, 
          long_name: Optional[str] = None,
          help: str = "",
          type: Type = bool,
          default: Any = None,
          required: bool = False,
          choices: Optional[List[Any]] = None,
          group: Optional[int] = None):
    """选项装饰器
    
    用于添加命令选项（-v, --verbose等）。
    
    Args:
        short_name: 短选项名，如 "-v"
        long_name: 长选项名，如 "--verbose"
        help: 帮助文本
        type: 值类型（对于标志选项忽略）
        default: 默认值
        required: 是否必需
        choices: 可选值列表
        group: 选项组ID
    
    Examples:
        @option("-v", "--verbose", help="详细输出")
        @option("--port", type=int, default=8080, help="端口号")
        @option("--format", choices=["json", "xml"], help="输出格式")
    """
    def decorator(func: Callable) -> Callable:
        # 确保函数有选项列表属性
        if not hasattr(func, '__command_options__'):
            func.__command_options__ = []
        
        # 判断选项类型
        if type == bool and default in (None, False):
            option_type = OptionType.FLAG
            value_type = bool
            default_value = False
        else:
            option_type = OptionType.VALUE
            value_type = type
            default_value = default
        
        # 创建选项规格
        option_spec = {
            'short_name': short_name,
            'long_name': long_name,
            'option_type': option_type,
            'description': help,
            'value_type': value_type,
            'default_value': default_value,
            'required': required,
            'choices': choices,
            'group_id': group
        }
        
        func.__command_options__.append(option_spec)
        return func
    
    return decorator


def param(name: str,
         type: Union[Type, UnionType, List[Type]] = str,
         default: Any = None,
         required: Optional[bool] = None,
         help: str = "",
         choices: Optional[List[Any]] = None,
         validator: Optional[Callable] = None,
         examples: Optional[List[str]] = None,
         type_hints: Optional[Dict[Type, str]] = None,
         type_examples: Optional[Dict[Type, List[str]]] = None):
    """参数装饰器
    
    用于添加命名参数（--name=value）。
    
    Args:
        name: 参数名（不包含--前缀）
        type: 参数类型，支持单类型、联合类型、类型列表
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
        @param("target", type=CommonUnionTypes.USER_IDENTIFIER)
        @param("input", type=[str, MessageSegment], 
               type_hints={str: "文件路径", MessageSegment: "图片文件"})
    """
    def decorator(func: Callable) -> Callable:
        # 确保函数有参数列表属性
        if not hasattr(func, '__command_params__'):
            func.__command_params__ = []
        
        # 创建参数规格
        param_spec = {
            'name': name,
            'type': type,
            'default': default,
            'required': required,
            'description': help,
            'choices': choices,
            'validator': validator,
            'examples': examples or [],
            'type_hints': type_hints or {},
            'type_examples': type_examples or {},
            'is_named': True,
            'is_positional': False
        }
        
        func.__command_params__.append(param_spec)
        return func
    
    return decorator


def option_group(group_id: int,
                name: str = "",
                mutually_exclusive: bool = False,
                required: bool = False,
                description: str = ""):
    """选项组装饰器
    
    用于定义选项组，特别是互斥选项组。
    
    Args:
        group_id: 组ID
        name: 组名称
        mutually_exclusive: 是否互斥
        required: 是否必须选择组内的一个选项
        description: 组描述
    
    Examples:
        @option_group(1, mutually_exclusive=True, name="输出格式")
        @option("--json", group=1)
        @option("--xml", group=1)
        @option("--yaml", group=1)
    """
    def decorator(func: Callable) -> Callable:
        # 确保函数有选项组列表属性
        if not hasattr(func, '__command_option_groups__'):
            func.__command_option_groups__ = []
        
        # 创建选项组规格
        group_spec = {
            'group_id': group_id,
            'name': name,
            'description': description,
            'mutually_exclusive': mutually_exclusive,
            'required': required
        }
        
        func.__command_option_groups__.append(group_spec)
        return func
    
    return decorator



# 便捷的类型装饰器
def str_param(name: str, **kwargs):
    """字符串参数装饰器"""
    return param(name, type=str, **kwargs)


def int_param(name: str, **kwargs):
    """整数参数装饰器"""
    return param(name, type=int, **kwargs)


def bool_param(name: str, **kwargs):
    """布尔参数装饰器"""
    return param(name, type=bool, **kwargs)


def user_param(name: str, **kwargs):
    """用户参数装饰器（支持用户名或@用户）"""
    return param(name, type=CommonUnionTypes.USER_IDENTIFIER, **kwargs)


def text_or_image_param(name: str, **kwargs):
    """文本或图片参数装饰器"""
    return param(name, type=CommonUnionTypes.STR_OR_IMAGE, **kwargs)


def choice_param(name: str, choices: List[Any], **kwargs):
    """选择参数装饰器"""
    return param(name, choices=choices, **kwargs)


class DecoratorValidator:
    """装饰器验证器
    
    验证装饰器的合理性和一致性。
    """
    
    @staticmethod
    def validate_function_decorators(func: Callable):
        """验证函数上的装饰器"""
        errors = []
        
        # 获取装饰器信息
        options = getattr(func, '__command_options__', [])
        params = getattr(func, '__command_params__', [])
        groups = getattr(func, '__command_option_groups__', [])
        
        # 验证选项名冲突
        option_names = []
        for option in options:
            names = []
            if option.get('short_name'):
                names.append(option['short_name'])
            if option.get('long_name'):
                names.append(option['long_name'])
            
            for name in names:
                if name in option_names:
                    errors.append(f"选项名冲突: {name}")
                option_names.append(name)
        
        # 验证参数名冲突
        param_names = []
        for param in params:
            name = param['name']
            if name in param_names:
                errors.append(f"参数名冲突: {name}")
            param_names.append(name)
        
        # 验证选项组
        group_ids = [g['group_id'] for g in groups]
        if len(group_ids) != len(set(group_ids)):
            errors.append("选项组ID重复")
        
        # 验证选项的组引用
        referenced_groups = set()
        for option in options:
            if option.get('group_id') is not None:
                referenced_groups.add(option['group_id'])
        
        defined_groups = set(group_ids)
        undefined_groups = referenced_groups - defined_groups
        if undefined_groups:
            errors.append(f"引用了未定义的选项组: {undefined_groups}")
        
        if errors:
            raise CommandRegistrationError(
                func.__name__,
                f"装饰器验证失败: {'; '.join(errors)}"
            )
    
    @staticmethod
    def validate_function_signature(func: Callable):
        """验证函数签名与装饰器的一致性"""
        import inspect
        
        signature = inspect.signature(func)
        params = list(signature.parameters.values())
        
        # 跳过第一个参数（event）
        if not params or params[0].name != 'event':
            raise CommandRegistrationError(
                func.__name__,
                "命令函数必须以'event'作为第一个参数"
            )
        
        func_params = params[1:]  # 除了event之外的参数
        decorator_params = getattr(func, '__command_params__', [])
        decorator_options = getattr(func, '__command_options__', [])
        
        # 获取所有装饰器定义的参数名
        decorator_names = set()
        for param in decorator_params:
            decorator_names.add(param['name'])
        for option in decorator_options:
            # 选项对应的参数名通常是long_name去掉--前缀
            if option.get('long_name'):
                name = option['long_name'].lstrip('-').replace('-', '_')
                decorator_names.add(name)

        # 特殊参数白名单（不需要装饰器定义）
        special_params = {'args', 'kwargs'}

        # 检查函数参数是否都有对应的装饰器
        for param in func_params:
            # 跳过特殊参数
            if param.name in special_params:
                continue
            # 跳过私有参数（以_开头）
            if param.name.startswith('_'):
                continue

            if param.name not in decorator_names:
                # 位置参数可能没有装饰器定义（用于简单命令）
                if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
                    continue
                # 关键字参数必须有装饰器定义（除非是特殊参数）
                elif param.kind == param.KEYWORD_ONLY:
                    raise CommandRegistrationError(
                        func.__name__,
                        f"关键字参数 '{param.name}' 没有对应的装饰器定义，请使用 @param 或 @option 装饰器"
                    )
                else:
                    raise CommandRegistrationError(
                        func.__name__,
                        f"参数 '{param.name}' 没有对应的装饰器定义"
                    )
