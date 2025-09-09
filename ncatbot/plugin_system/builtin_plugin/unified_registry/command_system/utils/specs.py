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

    def __post_init__(self):
        if self.examples is None:
            self.examples = []
        if self.type_hints is None:
            self.type_hints = {}
        if self.type_examples is None:
            self.type_examples = {}


@dataclass
class CommandSpec:
    """命令完整规格数据类

    包含命令的所有配置信息，包括选项、选项组和参数。
    """
    name: str = ""
    description: str = ""
    options: List[OptionSpec] = field(default_factory=list)
    option_groups: List[OptionGroupSpec] = field(default_factory=list)
    parameters: List[ParameterSpec] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)
    category: str = "general"
    hidden: bool = False
    examples: List[str] = field(default_factory=list)

class CommonadSpec:
    # 彻底分析函数后得到的命令标识器，用于指导参数传递
    def __init__(self, options: List[OptionSpec], option_groups: List[OptionGroupSpec], params: List[ParameterSpec], args_types: List[type], func: Callable):
        self.options = options
        self.option_groups = option_groups
        self.params = params
        self.args_types = args_types
        self.func = func

        # 必须外部重新设置的属性
        self.alias = None
        self.description = None
        self.basename = None

    def get_kw_binding(self, option: str) -> dict:
        for value in self.options:
            if value.name == option:
                return {option: True}
        for value in self.option_groups:
            if option in value.choices:
                return {value.name: option}
        return None