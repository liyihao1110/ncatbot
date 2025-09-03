"""类型系统定义

支持基础类型、联合类型、自定义类型等，提供强大的类型转换和验证功能。
"""

from typing import Union, List, Type, Any, Optional, Dict, Callable
from dataclasses import dataclass, field
from enum import Enum
from ncatbot.core.event.message_segment.message_segment import MessageSegment


class ParameterType(Enum):
    """基础参数类型枚举"""
    STR = "str"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    JSON = "json"
    REGEX = "regex"
    
    # 消息段类型
    IMAGE = "image"        # 图片
    AT = "at"             # @用户
    FILE = "file"         # 文件
    VOICE = "voice"       # 语音
    VIDEO = "video"       # 视频
    FACE = "face"         # 表情
    REPLY = "reply"       # 回复
    
    # 复合类型
    MESSAGE_SEGMENT = "message_segment"  # 任意消息段
    TEXT_OR_SEGMENT = "text_or_segment"  # 文本或消息段


class OptionType(Enum):
    """选项类型枚举"""
    FLAG = "flag"         # 标志选项（无值）
    VALUE = "value"       # 值选项（有值）
    MULTI_VALUE = "multi_value"  # 多值选项


@dataclass
class UnionType:
    """联合类型定义
    
    支持一个参数接受多种类型的值，系统会按优先级尝试转换。
    """
    types: List[Type]
    preferred_type: Optional[Type] = None  # 优先类型
    conversion_order: Optional[List[Type]] = None  # 转换优先级
    strict_mode: bool = False  # 严格模式（失败时不尝试其他类型）
    
    def __post_init__(self):
        if self.conversion_order is None:
            self.conversion_order = self.types.copy()
        if self.preferred_type is None:
            self.preferred_type = self.types[0]
    
    def __contains__(self, type_obj: Type) -> bool:
        """检查类型是否在联合类型中"""
        return type_obj in self.types
    
    def get_type_names(self) -> List[str]:
        """获取类型名称列表"""
        return [self._get_friendly_name(t) for t in self.types]
    
    def _get_friendly_name(self, type_obj: Type) -> str:
        """获取用户友好的类型名称"""
        if type_obj == str:
            return "文本"
        elif type_obj == int:
            return "整数"
        elif type_obj == float:
            return "小数"
        elif type_obj == bool:
            return "是/否"
        elif type_obj == MessageSegment:
            return "消息元素"
        else:
            return type_obj.__name__


class CommonUnionTypes:
    """预定义的常用联合类型"""
    
    # 用户标识：可以是用户名(str)或@用户(MessageSegment)
    USER_IDENTIFIER = UnionType([MessageSegment, str], preferred_type=MessageSegment)
    
    # 文本或@用户
    STR_OR_AT = UnionType([str, MessageSegment], preferred_type=str)
    
    # 文本或图片
    STR_OR_IMAGE = UnionType([str, MessageSegment], preferred_type=str)
    
    # 数字或文本
    INT_OR_STR = UnionType([int, str], preferred_type=int)
    FLOAT_OR_STR = UnionType([float, str], preferred_type=float)
    
    # 文本或任意消息段
    TEXT_OR_SEGMENT = UnionType([str, MessageSegment], preferred_type=str)
    
    # 多媒体类型：图片、视频、文件
    MEDIA = UnionType([MessageSegment], preferred_type=MessageSegment)
    
    # 用户输入：文本、图片、文件等
    USER_INPUT = UnionType([str, MessageSegment], preferred_type=str)


@dataclass
class TypeValidator:
    """类型验证器"""
    validator_func: Callable[[Any], bool]
    error_message: str
    suggestions: List[str] = field(default_factory=list)
    
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """验证值
        
        Returns:
            tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        try:
            if self.validator_func(value):
                return True, None
            return False, self.error_message
        except Exception as e:
            return False, f"验证失败: {str(e)}"


@dataclass
class TypeConverter:
    """类型转换器"""
    converter_func: Callable[[Any], Any]
    target_type: Type
    error_message: str = ""
    
    def convert(self, value: Any) -> tuple[bool, Any, Optional[str]]:
        """转换值
        
        Returns:
            tuple[bool, Any, Optional[str]]: (是否成功, 转换后的值, 错误信息)
        """
        try:
            converted = self.converter_func(value)
            return True, converted, None
        except Exception as e:
            error_msg = self.error_message or f"转换为 {self.target_type.__name__} 失败: {str(e)}"
            return False, None, error_msg


class BuiltinConverters:
    """内置类型转换器"""
    
    @staticmethod
    def str_converter() -> TypeConverter:
        return TypeConverter(
            converter_func=lambda x: str(x),
            target_type=str,
            error_message="无法转换为字符串"
        )
    
    @staticmethod
    def int_converter() -> TypeConverter:
        return TypeConverter(
            converter_func=lambda x: int(x) if isinstance(x, (int, str)) and str(x).isdigit() else int(float(x)),
            target_type=int,
            error_message="需要整数，如: 1, 42, -5"
        )
    
    @staticmethod
    def float_converter() -> TypeConverter:
        return TypeConverter(
            converter_func=lambda x: float(x),
            target_type=float,
            error_message="需要数字，如: 1.5, 3.14, -2.0"
        )
    
    @staticmethod
    def bool_converter() -> TypeConverter:
        def convert_bool(x):
            if isinstance(x, bool):
                return x
            if isinstance(x, str):
                x = x.lower()
                if x in ('true', '1', 'yes', 'on', '是', '真'):
                    return True
                elif x in ('false', '0', 'no', 'off', '否', '假'):
                    return False
            raise ValueError("无效的布尔值")
        
        return TypeConverter(
            converter_func=convert_bool,
            target_type=bool,
            error_message="需要是/否值，如: true/false, 1/0, 是/否"
        )
    
    @staticmethod
    def message_segment_converter() -> TypeConverter:
        def convert_segment(x):
            if isinstance(x, MessageSegment):
                return x
            # 如果是字符串，尝试解析为特定类型的MessageSegment
            raise ValueError("需要非文本元素（如图片、@用户等）")
        
        return TypeConverter(
            converter_func=convert_segment,
            target_type=MessageSegment,
            error_message="需要非文本元素，如图片、@用户、文件等"
        )


class BuiltinValidators:
    """内置验证器"""
    
    @staticmethod
    def range_validator(min_val: Optional[float] = None, max_val: Optional[float] = None) -> TypeValidator:
        """数值范围验证器"""
        def validate_range(value):
            if min_val is not None and value < min_val:
                return False
            if max_val is not None and value > max_val:
                return False
            return True
        
        error_msg = "数值超出范围"
        if min_val is not None and max_val is not None:
            error_msg = f"数值必须在 {min_val} 到 {max_val} 之间"
        elif min_val is not None:
            error_msg = f"数值必须大于等于 {min_val}"
        elif max_val is not None:
            error_msg = f"数值必须小于等于 {max_val}"
        
        return TypeValidator(
            validator_func=validate_range,
            error_message=error_msg
        )
    
    @staticmethod
    def length_validator(min_len: Optional[int] = None, max_len: Optional[int] = None) -> TypeValidator:
        """字符串长度验证器"""
        def validate_length(value):
            length = len(str(value))
            if min_len is not None and length < min_len:
                return False
            if max_len is not None and length > max_len:
                return False
            return True
        
        error_msg = "长度不符合要求"
        if min_len is not None and max_len is not None:
            error_msg = f"长度必须在 {min_len} 到 {max_len} 个字符之间"
        elif min_len is not None:
            error_msg = f"长度必须至少 {min_len} 个字符"
        elif max_len is not None:
            error_msg = f"长度不能超过 {max_len} 个字符"
        
        return TypeValidator(
            validator_func=validate_length,
            error_message=error_msg
        )
    
    @staticmethod
    def choices_validator(choices: List[Any]) -> TypeValidator:
        """选择值验证器"""
        def validate_choice(value):
            return value in choices
        
        return TypeValidator(
            validator_func=validate_choice,
            error_message=f"必须是以下值之一: {', '.join(map(str, choices))}",
            suggestions=[f"可选值: {', '.join(map(str, choices))}"]
        )
    
    @staticmethod
    def regex_validator(pattern: str, error_message: str = "格式不正确") -> TypeValidator:
        """正则表达式验证器"""
        import re
        compiled_pattern = re.compile(pattern)
        
        def validate_regex(value):
            return bool(compiled_pattern.match(str(value)))
        
        return TypeValidator(
            validator_func=validate_regex,
            error_message=error_message
        )
    
    @staticmethod
    def message_segment_type_validator(segment_type: str) -> TypeValidator:
        """消息段类型验证器"""
        def validate_segment_type(value):
            if not isinstance(value, MessageSegment):
                return False
            return value.msg_seg_type == segment_type
        
        return TypeValidator(
            validator_func=validate_segment_type,
            error_message=f"需要 {segment_type} 类型的消息元素"
        )


@dataclass
class TypeMeta:
    """类型元数据
    
    包含类型的所有信息：转换器、验证器、提示等。
    """
    target_type: Type
    converter: Optional[TypeConverter] = None
    validators: List[TypeValidator] = field(default_factory=list)
    description: str = ""
    examples: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        # 如果没有提供转换器，使用默认转换器
        if self.converter is None:
            self.converter = self._get_default_converter()
    
    def _get_default_converter(self) -> TypeConverter:
        """获取默认转换器"""
        if self.target_type == str:
            return BuiltinConverters.str_converter()
        elif self.target_type == int:
            return BuiltinConverters.int_converter()
        elif self.target_type == float:
            return BuiltinConverters.float_converter()
        elif self.target_type == bool:
            return BuiltinConverters.bool_converter()
        elif self.target_type == MessageSegment:
            return BuiltinConverters.message_segment_converter()
        else:
            # 默认转换器：直接返回值
            return TypeConverter(
                converter_func=lambda x: x,
                target_type=self.target_type
            )
    
    def convert_and_validate(self, value: Any) -> tuple[bool, Any, List[str]]:
        """转换并验证值
        
        Returns:
            tuple[bool, Any, List[str]]: (是否成功, 转换后的值, 错误信息列表)
        """
        errors = []
        
        # 1. 类型转换
        success, converted_value, convert_error = self.converter.convert(value)
        if not success:
            errors.append(convert_error)
            return False, None, errors
        
        # 2. 验证
        for validator in self.validators:
            valid, error_msg = validator.validate(converted_value)
            if not valid:
                errors.append(error_msg)
        
        if errors:
            return False, None, errors
        
        return True, converted_value, []


class TypeRegistry:
    """类型注册表
    
    管理所有可用的类型转换器和验证器。
    """
    
    def __init__(self):
        self._type_metas: Dict[Type, TypeMeta] = {}
        self._init_builtin_types()
    
    def _init_builtin_types(self):
        """初始化内置类型"""
        # 基础类型
        self.register_type(str, TypeMeta(
            target_type=str,
            description="文本字符串",
            examples=["hello", "用户名", "文件路径"],
            hints=["可以包含任意字符", "使用引号包围包含空格的文本"]
        ))
        
        self.register_type(int, TypeMeta(
            target_type=int,
            description="整数",
            examples=["1", "42", "-5", "0"],
            hints=["不包含小数点", "可以是负数"]
        ))
        
        self.register_type(float, TypeMeta(
            target_type=float,
            description="小数",
            examples=["1.5", "3.14", "-2.0", "0.1"],
            hints=["可以包含小数点", "支持科学计数法"]
        ))
        
        self.register_type(bool, TypeMeta(
            target_type=bool,
            description="是/否值",
            examples=["true", "false", "1", "0", "是", "否"],
            hints=["支持多种格式: true/false, 1/0, 是/否"]
        ))
        
        self.register_type(MessageSegment, TypeMeta(
            target_type=MessageSegment,
            description="消息元素",
            examples=["[@用户]", "[图片]", "[文件]"],
            hints=["包括@用户、图片、文件等非文本元素"]
        ))
    
    def register_type(self, type_obj: Type, meta: TypeMeta):
        """注册类型"""
        self._type_metas[type_obj] = meta
    
    def get_type_meta(self, type_obj: Type) -> Optional[TypeMeta]:
        """获取类型元数据"""
        return self._type_metas.get(type_obj)
    
    def create_union_meta(self, union_type: UnionType) -> Dict[Type, TypeMeta]:
        """为联合类型创建元数据映射"""
        return {t: self.get_type_meta(t) for t in union_type.types if self.get_type_meta(t)}


# 全局类型注册表实例
type_registry = TypeRegistry()
