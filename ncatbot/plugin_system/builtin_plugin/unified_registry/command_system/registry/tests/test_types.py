"""类型系统测试

测试类型转换、验证、联合类型等功能。
"""

import pytest
from typing import Union, List
from unittest.mock import Mock

from ..type_system import (
    UnionType, CommonUnionTypes, ParameterType, OptionType,
    TypeValidator, TypeConverter, BuiltinConverters, BuiltinValidators,
    TypeMeta, type_registry
)
from ..exceptions import ValidationError, TypeConversionError
from .conftest import MockMessageSegment
from ncatbot.core.event.message_segment.message_segment import MessageSegment


class TestUnionType:
    """联合类型测试"""
    
    def test_union_type_creation(self):
        """测试联合类型创建"""
        union = UnionType([str, int])
        assert len(union.types) == 2
        assert str in union.types
        assert int in union.types
        assert union.preferred_type == str
        assert union.conversion_order == [str, int]
    
    def test_union_type_with_preferred(self):
        """测试带优先类型的联合类型"""
        union = UnionType([str, int], preferred_type=int)
        assert union.preferred_type == int
    
    def test_union_type_with_custom_order(self):
        """测试自定义转换顺序"""
        union = UnionType([str, int, float], conversion_order=[int, str, float])
        assert union.conversion_order == [int, str, float]
    
    def test_contains_check(self):
        """测试类型包含检查"""
        union = UnionType([str, int])
        assert str in union
        assert int in union
        assert float not in union
    
    def test_type_names_generation(self):
        """测试友好类型名生成"""
        union = UnionType([str, int, bool])
        names = union.get_type_names()
        assert "文本" in names
        assert "整数" in names
        assert "是/否" in names
    
    def test_friendly_name_mapping(self):
        """测试友好名称映射"""
        union = UnionType([str])
        assert union._get_friendly_name(str) == "文本"
        assert union._get_friendly_name(int) == "整数"
        assert union._get_friendly_name(float) == "小数"
        assert union._get_friendly_name(bool) == "是/否"


class TestCommonUnionTypes:
    """预定义联合类型测试"""
    
    def test_user_identifier_type(self):
        """测试用户标识类型"""
        user_type = CommonUnionTypes.USER_IDENTIFIER
        assert MessageSegment in user_type.types
        assert str in user_type.types
        assert user_type.preferred_type == MessageSegment
    
    def test_str_or_at_type(self):
        """测试字符串或@用户类型"""
        str_at_type = CommonUnionTypes.STR_OR_AT
        assert str in str_at_type.types
        assert MessageSegment in str_at_type.types
        assert str_at_type.preferred_type == str
    
    def test_int_or_str_type(self):
        """测试整数或字符串类型"""
        int_str_type = CommonUnionTypes.INT_OR_STR
        assert int in int_str_type.types
        assert str in int_str_type.types
        assert int_str_type.preferred_type == int


class TestTypeConverter:
    """类型转换器测试"""
    
    def test_converter_creation(self):
        """测试转换器创建"""
        converter = TypeConverter(
            converter_func=lambda x: str(x),
            target_type=str,
            error_message="转换失败"
        )
        assert converter.target_type == str
        assert converter.error_message == "转换失败"
    
    def test_successful_conversion(self):
        """测试成功转换"""
        converter = TypeConverter(
            converter_func=lambda x: int(x),
            target_type=int
        )
        success, result, error = converter.convert("123")
        assert success is True
        assert result == 123
        assert error is None
    
    def test_failed_conversion(self):
        """测试转换失败"""
        converter = TypeConverter(
            converter_func=lambda x: int(x),
            target_type=int,
            error_message="无法转换为整数"
        )
        success, result, error = converter.convert("abc")
        assert success is False
        assert result is None
        assert "无法转换为整数" in error


class TestBuiltinConverters:
    """内置转换器测试"""
    
    def test_str_converter(self):
        """测试字符串转换器"""
        converter = BuiltinConverters.str_converter()
        
        # 测试各种输入
        success, result, _ = converter.convert(123)
        assert success and result == "123"
        
        success, result, _ = converter.convert("hello")
        assert success and result == "hello"
        
        success, result, _ = converter.convert(True)
        assert success and result == "True"
    
    def test_int_converter(self):
        """测试整数转换器"""
        converter = BuiltinConverters.int_converter()
        
        # 测试正常整数
        success, result, _ = converter.convert("123")
        assert success and result == 123
        
        # 测试浮点数转整数
        success, result, _ = converter.convert("123.7")
        assert success and result == 123
        
        # 测试转换失败
        success, result, error = converter.convert("abc")
        assert success is False
        assert "需要整数" in error
    
    def test_bool_converter(self):
        """测试布尔转换器"""
        converter = BuiltinConverters.bool_converter()
        
        # 测试真值
        for true_val in ["true", "1", "yes", "on", "是", "真", True]:
            success, result, _ = converter.convert(true_val)
            assert success and result is True
        
        # 测试假值
        for false_val in ["false", "0", "no", "off", "否", "假", False]:
            success, result, _ = converter.convert(false_val)
            assert success and result is False
        
        # 测试无效值
        success, result, error = converter.convert("maybe")
        assert success is False
        assert "需要是/否值" in error
    
    def test_message_segment_converter(self):
        """测试消息段转换器"""
        converter = BuiltinConverters.message_segment_converter()
        
        # 测试消息段输入 - 需要真正的MessageSegment实例
        # 由于MockMessageSegment不是MessageSegment的实例，这里跳过直接测试
        # 或者我们可以模拟一个真正的MessageSegment
        
        # 测试字符串输入（应该失败）
        success, result, error = converter.convert("test")
        assert success is False
        assert "需要非文本元素" in error


class TestTypeValidator:
    """类型验证器测试"""
    
    def test_validator_creation(self):
        """测试验证器创建"""
        validator = TypeValidator(
            validator_func=lambda x: x > 0,
            error_message="必须大于0"
        )
        assert validator.error_message == "必须大于0"
    
    def test_successful_validation(self):
        """测试验证成功"""
        validator = TypeValidator(
            validator_func=lambda x: x > 0,
            error_message="必须大于0"
        )
        valid, error = validator.validate(5)
        assert valid is True
        assert error is None
    
    def test_failed_validation(self):
        """测试验证失败"""
        validator = TypeValidator(
            validator_func=lambda x: x > 0,
            error_message="必须大于0"
        )
        valid, error = validator.validate(-1)
        assert valid is False
        assert error == "必须大于0"
    
    def test_validation_exception(self):
        """测试验证异常"""
        def bad_validator(x):
            raise ValueError("验证器错误")
        
        validator = TypeValidator(
            validator_func=bad_validator,
            error_message="验证失败"
        )
        valid, error = validator.validate("test")
        assert valid is False
        assert "验证失败: 验证器错误" in error


class TestBuiltinValidators:
    """内置验证器测试"""
    
    def test_range_validator(self):
        """测试范围验证器"""
        # 测试最小值
        validator = BuiltinValidators.range_validator(min_val=0)
        valid, error = validator.validate(5)
        assert valid is True
        valid, error = validator.validate(-1)
        assert valid is False
        assert "大于等于 0" in error
        
        # 测试最大值
        validator = BuiltinValidators.range_validator(max_val=10)
        valid, error = validator.validate(5)
        assert valid is True
        valid, error = validator.validate(15)
        assert valid is False
        assert "小于等于 10" in error
        
        # 测试范围
        validator = BuiltinValidators.range_validator(min_val=0, max_val=10)
        valid, error = validator.validate(5)
        assert valid is True
        valid, error = validator.validate(-1)
        assert valid is False
        valid, error = validator.validate(15)
        assert valid is False
    
    def test_length_validator(self):
        """测试长度验证器"""
        validator = BuiltinValidators.length_validator(min_len=2, max_len=5)
        
        valid, _ = validator.validate("abc")
        assert valid is True
        
        valid, error = validator.validate("a")
        assert valid is False
        assert "2 到 5 个字符之间" in error
        
        valid, error = validator.validate("abcdef")
        assert valid is False
        assert "2 到 5 个字符之间" in error
    
    def test_choices_validator(self):
        """测试选择值验证器"""
        validator = BuiltinValidators.choices_validator(["red", "green", "blue"])
        
        valid, _ = validator.validate("red")
        assert valid is True
        
        valid, error = validator.validate("yellow")
        assert valid is False
        assert "red, green, blue" in error
    
    def test_regex_validator(self):
        """测试正则验证器"""
        # 测试邮箱格式
        validator = BuiltinValidators.regex_validator(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "邮箱格式不正确"
        )
        
        valid, _ = validator.validate("test@example.com")
        assert valid is True
        
        valid, error = validator.validate("invalid-email")
        assert valid is False
        assert "邮箱格式不正确" in error


class TestTypeMeta:
    """类型元数据测试"""
    
    def test_type_meta_creation(self):
        """测试类型元数据创建"""
        meta = TypeMeta(
            target_type=int,
            description="整数类型",
            examples=["1", "42", "-5"]
        )
        assert meta.target_type == int
        assert meta.description == "整数类型"
        assert len(meta.examples) == 3
        assert meta.converter is not None  # 应该有默认转换器
    
    def test_type_meta_with_custom_converter(self):
        """测试带自定义转换器的类型元数据"""
        custom_converter = TypeConverter(
            converter_func=lambda x: int(x) * 2,
            target_type=int
        )
        meta = TypeMeta(
            target_type=int,
            converter=custom_converter
        )
        assert meta.converter is custom_converter
    
    def test_convert_and_validate_success(self):
        """测试转换和验证成功"""
        validator = BuiltinValidators.range_validator(min_val=0, max_val=100)
        meta = TypeMeta(
            target_type=int,
            validators=[validator]
        )
        
        success, result, errors = meta.convert_and_validate("42")
        assert success is True
        assert result == 42
        assert len(errors) == 0
    
    def test_convert_and_validate_conversion_failure(self):
        """测试转换失败"""
        meta = TypeMeta(target_type=int)
        success, result, errors = meta.convert_and_validate("abc")
        assert success is False
        assert result is None
        assert len(errors) > 0
    
    def test_convert_and_validate_validation_failure(self):
        """测试验证失败"""
        validator = BuiltinValidators.range_validator(min_val=0, max_val=100)
        meta = TypeMeta(
            target_type=int,
            validators=[validator]
        )
        
        success, result, errors = meta.convert_and_validate("150")
        assert success is False
        assert result is None
        assert len(errors) > 0
        assert any("100" in error for error in errors)


class TestTypeRegistry:
    """类型注册表测试"""
    
    def test_builtin_types_registration(self):
        """测试内置类型注册"""
        # 检查基础类型是否已注册
        assert type_registry.get_type_meta(str) is not None
        assert type_registry.get_type_meta(int) is not None
        assert type_registry.get_type_meta(bool) is not None
        assert type_registry.get_type_meta(float) is not None
    
    def test_custom_type_registration(self):
        """测试自定义类型注册"""
        class CustomType:
            pass
        
        custom_meta = TypeMeta(
            target_type=CustomType,
            description="自定义类型"
        )
        
        type_registry.register_type(CustomType, custom_meta)
        retrieved_meta = type_registry.get_type_meta(CustomType)
        
        assert retrieved_meta is custom_meta
        assert retrieved_meta.description == "自定义类型"
    
    def test_union_meta_creation(self):
        """测试联合类型元数据创建"""
        union = UnionType([str, int])
        meta_map = type_registry.create_union_meta(union)
        
        assert str in meta_map
        assert int in meta_map
        assert meta_map[str] is not None
        assert meta_map[int] is not None
    
    def test_nonexistent_type_meta(self):
        """测试不存在的类型元数据"""
        class NonExistentType:
            pass
        
        meta = type_registry.get_type_meta(NonExistentType)
        assert meta is None


if __name__ == "__main__":
    pytest.main([__file__])
