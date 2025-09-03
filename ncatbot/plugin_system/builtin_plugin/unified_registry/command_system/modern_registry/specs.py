"""参数和选项规格定义

定义命令参数、选项的详细规格，支持多类型、验证、默认值等。
"""

from typing import Union, List, Type, Any, Optional, Dict, Callable
from dataclasses import dataclass, field
import inspect

from .type_system import UnionType, TypeMeta, type_registry, ParameterType, OptionType
from .exceptions import ParameterError


MISSING = object()  # 表示参数没有默认值的特殊标记


@dataclass
class ParameterSpec:
    """参数规格定义
    
    描述命令的位置参数或命名参数的完整信息。
    """
    name: str
    type: Union[Type, UnionType, List[Type]]
    default: Any = MISSING
    required: Optional[bool] = None  # None表示自动判断
    description: str = ""
    
    # 多类型支持
    type_hints: Dict[Type, str] = field(default_factory=dict)
    type_examples: Dict[Type, List[str]] = field(default_factory=dict)
    type_validators: Dict[Type, Callable] = field(default_factory=dict)
    
    # 验证相关
    choices: Optional[List[Any]] = None
    validator: Optional[Callable] = None
    converter: Optional[Callable] = None
    
    # 提示相关
    error_messages: Dict[str, str] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    
    # 高级选项
    is_positional: bool = True  # 是否为位置参数
    is_named: bool = False      # 是否为命名参数
    is_varargs: bool = False    # 是否为可变参数 (*args)
    is_kwargs: bool = False     # 是否为关键字参数 (**kwargs)
    is_option: bool = False     # 是否为选项参数（通过@option装饰器定义）
    
    def __post_init__(self):
        """初始化后处理"""
        # 自动判断是否必需
        if self.required is None:
            self.required = (self.default is MISSING)
        
        # 规范化类型定义
        self._normalize_type()
        
        # 验证参数定义
        self._validate_spec()
    
    def _normalize_type(self):
        """规范化类型定义"""
        if isinstance(self.type, list):
            # 列表形式的多类型转换为UnionType
            self.type = UnionType(self.type)
        elif hasattr(self.type, '__origin__') and self.type.__origin__ is Union:
            # typing.Union转换为UnionType
            union_args = self.type.__args__
            self.type = UnionType(list(union_args))
    
    def _validate_spec(self):
        """验证参数规格的合理性"""
        # 检查必需参数不能有默认值
        if self.required and self.default is not MISSING:
            raise ParameterError(
                self.name, 
                "必需参数不能有默认值",
                suggestions=["将参数设为可选", "移除默认值"]
            )
        
        # 检查可选参数必须有默认值
        if not self.required and self.default is MISSING:
            raise ParameterError(
                self.name,
                "可选参数必须有默认值",
                suggestions=["设置default参数", "将参数设为必需"]
            )
        
        # 检查位置参数和命名参数不能同时为True
        if self.is_positional and self.is_named:
            raise ParameterError(
                self.name,
                "参数不能同时为位置参数和命名参数"
            )
    
    def get_union_type(self) -> Optional[UnionType]:
        """获取联合类型定义"""
        if isinstance(self.type, UnionType):
            return self.type
        return None
    
    def is_multi_type(self) -> bool:
        """是否为多类型参数"""
        return isinstance(self.type, UnionType)
    
    def get_type_list(self) -> List[Type]:
        """获取支持的类型列表"""
        if isinstance(self.type, UnionType):
            return self.type.types
        else:
            return [self.type]
    
    def get_friendly_type_name(self) -> str:
        """获取用户友好的类型名称"""
        if isinstance(self.type, UnionType):
            type_names = self.type.get_type_names()
            return " 或 ".join(type_names)
        else:
            # 使用类型注册表获取友好名称
            meta = type_registry.get_type_meta(self.type)
            if meta and meta.description:
                return meta.description
            return self.type.__name__
    
    def get_examples_for_type(self, target_type: Type) -> List[str]:
        """获取指定类型的示例"""
        # 首先查看自定义示例
        if target_type in self.type_examples:
            return self.type_examples[target_type]
        
        # 然后查看类型注册表
        meta = type_registry.get_type_meta(target_type)
        if meta and meta.examples:
            return meta.examples
        
        # 返回空列表
        return []
    
    def get_hint_for_type(self, target_type: Type) -> str:
        """获取指定类型的提示"""
        # 首先查看自定义提示
        if target_type in self.type_hints:
            return self.type_hints[target_type]
        
        # 然后查看类型注册表
        meta = type_registry.get_type_meta(target_type)
        if meta and meta.description:
            return meta.description
        
        return ""


@dataclass
class OptionSpec:
    """选项规格定义
    
    描述命令选项的完整信息。
    """
    short_name: Optional[str] = None  # 短选项名 -v
    long_name: Optional[str] = None   # 长选项名 --verbose
    option_type: OptionType = OptionType.FLAG
    description: str = ""
    
    # 值选项相关
    value_type: Union[Type, UnionType, List[Type]] = str
    default_value: Any = None
    required: bool = False
    
    # 分组相关
    group_id: Optional[int] = None      # 选项组ID
    mutually_exclusive: bool = False    # 是否与组内其他选项互斥
    
    # 多值选项相关
    min_values: int = 0
    max_values: Optional[int] = None
    
    # 验证相关
    choices: Optional[List[Any]] = None
    validator: Optional[Callable] = None
    
    # 提示相关
    examples: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    error_messages: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        # 验证选项名
        if not self.short_name and not self.long_name:
            raise ParameterError("选项", "必须提供短选项名或长选项名")
        
        # 规范化类型定义
        self._normalize_type()
        
        # 设置默认值
        if self.option_type == OptionType.FLAG and self.default_value is None:
            self.default_value = False
    
    def _normalize_type(self):
        """规范化类型定义"""
        if isinstance(self.value_type, list):
            self.value_type = UnionType(self.value_type)
        elif hasattr(self.value_type, '__origin__') and self.value_type.__origin__ is Union:
            union_args = self.value_type.__args__
            self.value_type = UnionType(list(union_args))
    
    def get_option_names(self) -> List[str]:
        """获取选项名列表"""
        names = []
        if self.short_name:
            names.append(self.short_name)
        if self.long_name:
            names.append(self.long_name)
        return names
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        names = []
        if self.short_name:
            names.append(self.short_name)
        if self.long_name:
            names.append(self.long_name)
        return ", ".join(names)
    
    def is_flag(self) -> bool:
        """是否为标志选项"""
        return self.option_type == OptionType.FLAG
    
    def needs_value(self) -> bool:
        """是否需要值"""
        return self.option_type in (OptionType.VALUE, OptionType.MULTI_VALUE)
    
    def get_union_type(self) -> Optional[UnionType]:
        """获取值的联合类型定义"""
        if isinstance(self.value_type, UnionType):
            return self.value_type
        return None


@dataclass
class OptionGroup:
    """选项组定义
    
    用于管理互斥选项等。
    """
    group_id: int
    name: str = ""
    description: str = ""
    mutually_exclusive: bool = False
    required: bool = False  # 是否必须选择组内的一个选项
    options: List[OptionSpec] = field(default_factory=list)
    
    def add_option(self, option: OptionSpec):
        """添加选项到组"""
        option.group_id = self.group_id
        option.mutually_exclusive = self.mutually_exclusive
        self.options.append(option)
    
    def get_option_names(self) -> List[str]:
        """获取组内所有选项名"""
        names = []
        for option in self.options:
            names.extend(option.get_option_names())
        return names


class SpecBuilder:
    """规格构建器
    
    从函数签名和装饰器信息构建参数和选项规格。
    """
    
    def __init__(self):
        self.parameters: List[ParameterSpec] = []
        self.options: List[OptionSpec] = []
        self.option_groups: List[OptionGroup] = []
    
    def build_from_function(self, func: Callable) -> tuple[List[ParameterSpec], List[OptionSpec], List[OptionGroup]]:
        """从函数构建规格
        
        Args:
            func: 目标函数
            
        Returns:
            tuple: (参数列表, 选项列表, 选项组列表)
        """
        # 分析函数签名
        signature = inspect.signature(func)
        
        # 跳过第一个参数（通常是event）
        params = list(signature.parameters.values())[1:]
        
        # 从装饰器获取额外信息
        decorator_params = getattr(func, '__command_params__', [])
        decorator_options = getattr(func, '__command_options__', [])
        decorator_groups = getattr(func, '__command_option_groups__', [])
        
        # 构建选项规格（先构建选项，这样参数构建时可以引用）
        self._build_options(decorator_options)

        # 构建参数规格
        self._build_parameters(params, decorator_params)

        # 构建选项组
        self._build_option_groups(decorator_groups)

        # 将选项关联到选项组
        self._associate_options_with_groups()

        return self.parameters, self.options, self.option_groups
    
    def _build_parameters(self, sig_params: List[inspect.Parameter], decorator_params: List[Dict]):
        """构建参数规格"""
        # 创建装饰器参数和选项的映射
        param_decorator_map = {p['name']: p for p in decorator_params}
        option_decorator_map = {}

        # 收集所有选项参数名
        for option_spec in self.options:
            # 选项参数通常是 long_name 去掉 -- 前缀，并将 - 转换为 _
            if option_spec.long_name:
                param_name = option_spec.long_name.lstrip('-').replace('-', '_')
                option_decorator_map[param_name] = option_spec
            elif option_spec.short_name:
                # 如果只有短选项名，也尝试映射（去掉 - 前缀）
                param_name = option_spec.short_name.lstrip('-').replace('-', '_')
                option_decorator_map[param_name] = option_spec

        for param in sig_params:
            # 获取基本信息
            param_spec = ParameterSpec(
                name=param.name,
                type=param.annotation if param.annotation != inspect.Parameter.empty else str,
                default=param.default if param.default != inspect.Parameter.empty else MISSING,
                is_positional=param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD),
                is_named=param.kind == param.KEYWORD_ONLY,
                is_varargs=param.kind == param.VAR_POSITIONAL,
                is_kwargs=param.kind == param.VAR_KEYWORD
            )

            # 检查是否为选项参数
            if param.name in option_decorator_map:
                param_spec.is_option = True
                # 选项参数通常不应该是位置参数
                param_spec.is_positional = False

            # 合并装饰器信息
            if param.name in param_decorator_map:
                decorator_info = param_decorator_map[param.name]
                # @param 装饰器定义的参数应该是命名参数
                param_spec.is_positional = False
                param_spec.is_named = True
                self._merge_decorator_info(param_spec, decorator_info)

            self.parameters.append(param_spec)
    
    def _build_options(self, decorator_options: List[Dict]):
        """构建选项规格"""
        for option_info in decorator_options:
            option_spec = OptionSpec(**option_info)
            self.options.append(option_spec)
    
    def _build_option_groups(self, decorator_groups: List[Dict]):
        """构建选项组"""
        for group_info in decorator_groups:
            group = OptionGroup(**group_info)
            self.option_groups.append(group)
    
    def _associate_options_with_groups(self):
        """将选项关联到对应的选项组"""
        # 创建选项组的映射
        group_map = {group.group_id: group for group in self.option_groups}

        # 将选项添加到对应的组中
        for option in self.options:
            if option.group_id is not None and option.group_id in group_map:
                group = group_map[option.group_id]
                group.add_option(option)

    def _merge_decorator_info(self, param_spec: ParameterSpec, decorator_info: Dict):
        """合并装饰器信息到参数规格"""
        for key, value in decorator_info.items():
            if hasattr(param_spec, key) and value is not None:
                setattr(param_spec, key, value)

        # 如果更新了类型，需要重新规范化
        if 'type' in decorator_info and decorator_info['type'] is not None:
            param_spec._normalize_type()
