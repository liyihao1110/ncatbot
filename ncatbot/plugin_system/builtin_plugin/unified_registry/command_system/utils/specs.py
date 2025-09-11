"""命令规格数据类定义

提供类型安全的数据结构，替代字典存储选项、选项组和参数配置。
"""

from dataclasses import dataclass, field
from typing import Callable, Any, List, Optional, Dict, Type


@dataclass
class OptionSpec:
    """选项规格数据类

    替代原有的选项字典存储。
    """
    short_name: Optional[str] = None
    long_name: Optional[str] = None
    description: str = ""
    @property
    def name(self) -> str:
        return self.long_name if self.long_name else self.short_name


@dataclass
class OptionGroupSpec:
    """选项组规格数据类

    替代原有的选项组字典存储。
    """
    choices: List[str]
    name: str
    default: str
    description: str = ""


@dataclass
class ParameterSpec:
    """参数规格数据类

    替代原有的参数字典存储。
    """
    name: str
    default: Any = None
    required: Optional[bool] = False
    description: str = ""
    choices: Optional[List[Any]] = None
    validator: Optional[Callable] = None
    examples: List[str] = None
    type_hints: Dict[Type, str] = None
    type_examples: Dict[Type, List[str]] = None
    is_named: bool = True
    is_positional: bool = False
    index: int = -1 # 用于确认参数位置（args_types 中），由分析器设置

    def __post_init__(self):
        if self.examples is None:
            self.examples = []
        if self.type_hints is None:
            self.type_hints = {}
        if self.type_examples is None:
            self.type_examples = {}

class CommandSpec:
    # 彻底分析函数后得到的命令标识器，用于指导参数传递
    def __init__(self, options: List[OptionSpec], option_groups: List[OptionGroupSpec], params: List[ParameterSpec], args_types: List[type], func: Callable):
        self.options: List[OptionSpec] = options
        self.option_groups: List[OptionGroupSpec] = option_groups
        self.params: List[ParameterSpec] = params
        self.args_types: List[type] = args_types
        self.func: Callable = func

        # 必须外部重新设置的属性
        self.aliases = []  # 默认为空列表而不是None
        self.description = None
        self.name = None

    def get_kw_binding(self, option: str) -> dict:
        for value in self.options:
            if value.name == option or value.short_name == option:
                return {value.name: True}
        for value in self.option_groups:
            if option in value.choices:
                return {value.name: option}
        return None
    
    def get_param_binding(self, param: str, value: Any) -> dict:
        for param_spec in self.params:
            if param_spec.name == param:
                target_type = self.args_types[param_spec.index]
                if target_type == bool:
                    return {param_spec.name: value.lower() not in ["false", "0"]}
                else:
                    return {param_spec.name: target_type(value)}                
        return None