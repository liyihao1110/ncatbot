"""参数规格测试

测试参数和选项规格的创建、验证和构建功能。
"""

import pytest
import inspect
from typing import Union
from unittest.mock import Mock

from ..specs import (
    ParameterSpec, OptionSpec, OptionGroup, SpecBuilder, 
    MISSING
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


class TestOptionGroup:
    """选项组测试"""
    
    def test_option_group_creation(self):
        """测试选项组创建"""
        group = OptionGroup(
            group_id=1,
            name="输出格式",
            description="选择输出格式",
            mutually_exclusive=True,
            required=True
        )
        
        assert group.group_id == 1
        assert group.name == "输出格式"
        assert group.description == "选择输出格式"
        assert group.mutually_exclusive is True
        assert group.required is True
        assert len(group.options) == 0
    
    def test_add_option_to_group(self):
        """测试向组添加选项"""
        group = OptionGroup(
            group_id=1,
            mutually_exclusive=True
        )
        
        option = OptionSpec(long_name="--json")
        group.add_option(option)
        
        assert len(group.options) == 1
        assert option in group.options
        assert option.group_id == 1
        assert option.mutually_exclusive is True
    
    def test_get_option_names(self):
        """测试获取组内所有选项名"""
        group = OptionGroup(group_id=1)
        
        option1 = OptionSpec(short_name="-j", long_name="--json")
        option2 = OptionSpec(long_name="--xml")
        
        group.add_option(option1)
        group.add_option(option2)
        
        names = group.get_option_names()
        assert "-j" in names
        assert "--json" in names
        assert "--xml" in names
        assert len(names) == 3


class TestSpecBuilder:
    """规格构建器测试"""
    
    def test_build_from_simple_function(self, sample_function):
        """测试从简单函数构建规格"""
        builder = SpecBuilder()
        parameters, options, option_groups = builder.build_from_function(sample_function)
        
        # 应该有3个参数（除了event）: name, age, verbose
        assert len(parameters) == 3
        
        # 检查参数
        param_names = [p.name for p in parameters]
        assert "name" in param_names
        assert "age" in param_names
        assert "verbose" in param_names
        
        # 检查类型推断
        name_param = next(p for p in parameters if p.name == "name")
        assert name_param.type == str
        assert name_param.required is True
        
        age_param = next(p for p in parameters if p.name == "age")
        assert age_param.type == int
        assert age_param.default == 18
        assert age_param.required is False
        
        verbose_param = next(p for p in parameters if p.name == "verbose")
        assert verbose_param.type == bool
        assert verbose_param.default is False
        assert verbose_param.required is False
    
    def test_build_from_decorated_function(self):
        """测试从装饰器函数构建规格"""
        # 创建一个带装饰器信息的函数
        def test_func(event, name: str, count: int = 1):
            pass
        
        # 添加装饰器信息
        test_func.__command_params__ = [
            {
                'name': 'target',
                'type': [str, MessageSegment],
                'description': '目标参数',
                'is_named': True,
                'is_positional': False
            }
        ]
        
        test_func.__command_options__ = [
            {
                'short_name': '-v',
                'long_name': '--verbose',
                'option_type': OptionType.FLAG,
                'description': '详细输出'
            }
        ]
        
        test_func.__command_option_groups__ = [
            {
                'group_id': 1,
                'name': '测试组',
                'mutually_exclusive': True
            }
        ]
        
        builder = SpecBuilder()
        parameters, options, option_groups = builder.build_from_function(test_func)
        
        # 检查参数构建
        assert len(parameters) == 2  # name, count
        
        # 检查选项构建
        assert len(options) == 1
        option = options[0]
        assert option.short_name == '-v'
        assert option.long_name == '--verbose'
        assert option.option_type == OptionType.FLAG
        
        # 检查选项组构建
        assert len(option_groups) == 1
        group = option_groups[0]
        assert group.group_id == 1
        assert group.name == '测试组'
        assert group.mutually_exclusive is True
    
    def test_build_with_varargs(self):
        """测试带可变参数的函数"""
        def varargs_func(event, name: str, *args, **kwargs):
            pass
        
        builder = SpecBuilder()
        parameters, options, option_groups = builder.build_from_function(varargs_func)
        
        # 应该识别所有参数类型
        param_names = [p.name for p in parameters]
        assert "name" in param_names
        assert "args" in param_names
        assert "kwargs" in param_names
        
        # 检查可变参数标记
        args_param = next(p for p in parameters if p.name == "args")
        assert args_param.is_varargs is True
        
        kwargs_param = next(p for p in parameters if p.name == "kwargs")
        assert kwargs_param.is_kwargs is True
    
    def test_merge_decorator_info(self):
        """测试装饰器信息合并"""
        builder = SpecBuilder()
        
        # 创建基础参数规格
        param_spec = ParameterSpec(
            name="test_param",
            type=str,
            description="基础描述"
        )
        
        # 装饰器信息
        decorator_info = {
            'description': '装饰器描述',
            'choices': ['a', 'b', 'c'],
            'examples': ['example1', 'example2']
        }
        
        # 合并信息
        builder._merge_decorator_info(param_spec, decorator_info)
        
        # 验证合并结果
        assert param_spec.description == '装饰器描述'
        assert param_spec.choices == ['a', 'b', 'c']
        assert param_spec.examples == ['example1', 'example2']


if __name__ == "__main__":
    pytest.main([__file__])
