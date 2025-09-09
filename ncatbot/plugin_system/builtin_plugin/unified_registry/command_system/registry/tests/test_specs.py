"""参数规格测试

测试参数和选项规格的创建、验证和构建功能。
"""

import pytest
import inspect
from typing import Union
from unittest.mock import Mock

from ..utils.specs import (
    ParameterSpec, OptionSpec, OptionGroupSpec, CommandSpec
)
from ..type_system import UnionType, CommonUnionTypes, OptionType
from ..exceptions import ParameterError
from .conftest import MockMessageSegment
from ncatbot.core.event.message_segment.message_segment import MessageSegment


class TestParameterSpec:
    """参数规格测试"""
    
    def test_basic_parameter_creation(self):
        """测试基础参数创建"""
        param = ParameterSpec(
            name="test_param",
            type=str,
            description="测试参数"
        )
        
        assert param.name == "test_param"
        assert param.type == str
        assert param.description == "测试参数"
        assert param.required is True  # 默认必需
        assert param.default is MISSING
        assert param.is_positional is True
        assert param.is_named is False
    
    def test_parameter_with_default(self):
        """测试带默认值的参数"""
        param = ParameterSpec(
            name="test_param",
            type=int,
            default=42,
            description="测试参数"
        )
        
        assert param.default == 42
        assert param.required is False  # 有默认值时不必需
    
    def test_multi_type_parameter(self):
        """测试多类型参数"""
        # 测试列表形式的多类型
        param = ParameterSpec(
            name="multi_param",
            type=[str, int],
            description="多类型参数"
        )
        
        assert param.is_multi_type()
        union_type = param.get_union_type()
        assert union_type is not None
        assert str in union_type.types
        assert int in union_type.types
    
    def test_union_type_parameter(self):
        """测试联合类型参数"""
        union = UnionType([str, MessageSegment])
        param = ParameterSpec(
            name="union_param",
            type=union,
            description="联合类型参数"
        )
        
        assert param.is_multi_type()
        assert param.get_union_type() is union
    
    def test_typing_union_parameter(self):
        """测试typing.Union类型参数"""
        param = ParameterSpec(
            name="typing_union_param",
            type=Union[str, int],
            description="typing联合类型参数"
        )
        
        # 应该被转换为UnionType
        assert param.is_multi_type()
        union_type = param.get_union_type()
        assert union_type is not None
        assert str in union_type.types
        assert int in union_type.types
    
    def test_parameter_validation_required_with_default(self):
        """测试必需参数不能有默认值的验证"""
        with pytest.raises(ParameterError) as exc_info:
            ParameterSpec(
                name="invalid_param",
                type=str,
                required=True,
                default="default_value"
            )
        
        assert "必需参数不能有默认值" in str(exc_info.value)
    
    def test_parameter_validation_optional_without_default(self):
        """测试可选参数必须有默认值的验证"""
        with pytest.raises(ParameterError) as exc_info:
            ParameterSpec(
                name="invalid_param",
                type=str,
                required=False,
                default=MISSING
            )
        
        assert "可选参数必须有默认值" in str(exc_info.value)
    
    def test_parameter_validation_position_and_named_conflict(self):
        """测试位置参数和命名参数冲突的验证"""
        with pytest.raises(ParameterError) as exc_info:
            ParameterSpec(
                name="invalid_param",
                type=str,
                is_positional=True,
                is_named=True
            )
        
        assert "不能同时为位置参数和命名参数" in str(exc_info.value)
    
    def test_get_type_list(self):
        """测试获取类型列表"""
        # 单类型
        param1 = ParameterSpec(name="param1", type=str)
        assert param1.get_type_list() == [str]
        
        # 多类型
        param2 = ParameterSpec(name="param2", type=[str, int])
        type_list = param2.get_type_list()
        assert str in type_list
        assert int in type_list
    
    def test_get_friendly_type_name(self):
        """测试获取友好类型名称"""
        # 单类型
        param1 = ParameterSpec(name="param1", type=str)
        assert "文本" in param1.get_friendly_type_name()
        
        # 多类型
        param2 = ParameterSpec(name="param2", type=[str, int])
        type_name = param2.get_friendly_type_name()
        assert "文本" in type_name
        assert "整数" in type_name
        assert "或" in type_name
    
    def test_get_examples_for_type(self):
        """测试获取指定类型的示例"""
        param = ParameterSpec(
            name="param",
            type=[str, int],
            type_examples={
                str: ["hello", "world"],
                int: [1, 2, 3]
            }
        )
        
        str_examples = param.get_examples_for_type(str)
        assert str_examples == ["hello", "world"]
        
        int_examples = param.get_examples_for_type(int)
        assert int_examples == [1, 2, 3]
        
        # 没有自定义示例的类型（但可能从类型注册表获取）
        float_examples = param.get_examples_for_type(float)
        # 由于类型注册表可能有 float 的示例，我们只检查它是一个列表
        assert isinstance(float_examples, list)
    
    def test_get_hint_for_type(self):
        """测试获取指定类型的提示"""
        param = ParameterSpec(
            name="param",
            type=[str, MessageSegment],
            type_hints={
                str: "文本内容",
                MessageSegment: "非文本元素"
            }
        )
        
        str_hint = param.get_hint_for_type(str)
        assert str_hint == "文本内容"
        
        segment_hint = param.get_hint_for_type(MessageSegment)
        assert segment_hint == "非文本元素"


class TestOptionSpec:
    """选项规格测试"""
    
    def test_flag_option_creation(self):
        """测试标志选项创建"""
        option = OptionSpec(
            short_name="-v",
            long_name="--verbose",
            description="详细输出"
        )
        
        assert option.short_name == "-v"
        assert option.long_name == "--verbose"
        assert option.description == "详细输出"
        assert option.option_type == OptionType.FLAG
        assert option.default_value is False
        assert option.is_flag()
        assert not option.needs_value()
    
    def test_value_option_creation(self):
        """测试值选项创建"""
        option = OptionSpec(
            long_name="--port",
            option_type=OptionType.VALUE,
            value_type=int,
            default_value=8080,
            description="端口号"
        )
        
        assert option.option_type == OptionType.VALUE
        assert option.value_type == int
        assert option.default_value == 8080
        assert not option.is_flag()
        assert option.needs_value()
    
    def test_option_with_type_inference(self):
        """测试类型推断的选项"""
        # 非布尔类型默认值应该创建值选项
        option = OptionSpec(
            long_name="--count",
            value_type=int,
            default_value=5,
            option_type=OptionType.VALUE
        )
        
        assert option.option_type == OptionType.VALUE
        assert option.value_type == int
        assert option.default_value == 5
    
    def test_option_validation_no_names(self):
        """测试选项必须有名称的验证"""
        with pytest.raises(ParameterError) as exc_info:
            OptionSpec(description="无名选项")
        
        assert "必须提供短选项名或长选项名" in str(exc_info.value)
    
    def test_option_with_choices(self):
        """测试带选择值的选项"""
        option = OptionSpec(
            long_name="--format",
            option_type=OptionType.VALUE,
            value_type=str,
            choices=["json", "xml", "yaml"],
            description="输出格式"
        )
        
        assert option.choices == ["json", "xml", "yaml"]
    
    def test_option_group_assignment(self):
        """测试选项组分配"""
        option = OptionSpec(
            long_name="--json",
            group_id=1,
            mutually_exclusive=True
        )
        
        assert option.group_id == 1
        assert option.mutually_exclusive is True
    
    def test_multi_value_option(self):
        """测试多值选项"""
        option = OptionSpec(
            long_name="--include",
            option_type=OptionType.MULTI_VALUE,
            value_type=str,
            min_values=1,
            max_values=5
        )
        
        assert option.option_type == OptionType.MULTI_VALUE
        assert option.min_values == 1
        assert option.max_values == 5
        assert option.needs_value()
    
    def test_get_option_names(self):
        """测试获取选项名列表"""
        option = OptionSpec(
            short_name="-v",
            long_name="--verbose"
        )
        
        names = option.get_option_names()
        assert "-v" in names
        assert "--verbose" in names
        assert len(names) == 2
    
    def test_get_display_name(self):
        """测试获取显示名称"""
        option = OptionSpec(
            short_name="-h",
            long_name="--help"
        )
        
        display_name = option.get_display_name()
        assert "-h" in display_name
        assert "--help" in display_name
        assert "," in display_name
    
    def test_union_type_option(self):
        """测试联合类型选项"""
        option = OptionSpec(
            long_name="--target",
            option_type=OptionType.VALUE,
            value_type=[str, MessageSegment]
        )
        
        union_type = option.get_union_type()
        assert union_type is not None
        assert str in union_type.types
        assert MessageSegment in union_type.types


class TestOptionGroupSpec:
    """选项组规格测试"""

    def test_option_group_spec_creation(self):
        """测试选项组规格创建"""
        group_spec = OptionGroupSpec(
            choices=["xml", "yaml", "json"],
            name="format",
            default="json",
            description="输出格式"
        )

        assert group_spec.name == "format"
        assert group_spec.description == "输出格式"
        assert group_spec.choices == ["xml", "yaml", "json"]
        assert group_spec.default == "json"
        assert group_spec.is_required is False

    def test_option_group_spec_option_names(self):
        """测试选项组规格的选项名称"""
        group_spec = OptionGroupSpec(
            choices=["xml", "yaml", "json"],
            name="format"
        )

        expected_names = ["--xml", "--yaml", "--json"]
        assert group_spec.option_names == expected_names

    def test_option_group_spec_validation(self):
        """测试选项组规格验证"""
        # 有效的选项组
        valid_group = OptionGroupSpec(
            choices=["xml", "yaml"],
            name="format",
            default="xml"
        )
        assert valid_group.name == "format"

        # 无效的选项组（缺少名称）
        with pytest.raises(ValueError):
            OptionGroupSpec(choices=["xml", "yaml"])

        # 无效的选项组（默认值不在选项中）
        with pytest.raises(ValueError):
            OptionGroupSpec(
                choices=["xml", "yaml"],
                name="format",
                default="invalid"
            )


# 移除了过时的 TestSpecBuilder 类，因为 SpecBuilder 类已不存在


if __name__ == "__main__":
    pytest.main([__file__])
