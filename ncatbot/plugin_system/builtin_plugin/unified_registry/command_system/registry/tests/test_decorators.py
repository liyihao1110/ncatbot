"""装饰器测试

测试各种装饰器的功能和验证逻辑。
"""

import pytest
from typing import Union
from unittest.mock import Mock

from ..decorators import (
    option, param, option_group,
    str_param, int_param, bool_param, user_param,
    text_or_image_param, choice_param,
    DecoratorValidator
)
from ..type_system import CommonUnionTypes, OptionType
from ..exceptions import CommandRegistrationError
from .conftest import MockMessageSegment
from ncatbot.core.event.message_segment.message_segment import MessageSegment


class TestOptionDecorator:
    """选项装饰器测试"""
    
    def test_flag_option_decorator(self):
        """测试标志选项装饰器"""
        @option("-v", "--verbose", help="详细输出")
        def test_func(event):
            pass
        
        # 检查装饰器是否添加了选项信息
        assert hasattr(test_func, '__command_options__')
        assert len(test_func.__command_options__) == 1
        
        option_spec = test_func.__command_options__[0]
        assert option_spec['short_name'] == "-v"
        assert option_spec['long_name'] == "--verbose"
        assert option_spec['description'] == "详细输出"
        assert option_spec['option_type'] == OptionType.FLAG
        assert option_spec['default_value'] is False
    
    def test_value_option_decorator(self):
        """测试值选项装饰器"""
        @option(long_name="--port", type=int, default=8080, help="端口号")
        def test_func(event):
            pass
        
        option_spec = test_func.__command_options__[0]
        assert option_spec['long_name'] == "--port"
        assert option_spec['option_type'] == OptionType.VALUE
        assert option_spec['value_type'] == int
        assert option_spec['default_value'] == 8080
        assert option_spec['description'] == "端口号"
    
    def test_option_with_choices(self):
        """测试带选择值的选项"""
        @option(long_name="--format", choices=["json", "xml", "yaml"], help="输出格式")
        def test_func(event):
            pass
        
        option_spec = test_func.__command_options__[0]
        assert option_spec['choices'] == ["json", "xml", "yaml"]
    
    def test_option_with_group(self):
        """测试带组的选项"""
        @option(long_name="--json", group=1, help="JSON格式")
        def test_func(event):
            pass
        
        option_spec = test_func.__command_options__[0]
        assert option_spec['group_id'] == 1
    
    def test_multiple_options(self):
        """测试多个选项"""
        @option("-v", "--verbose", help="详细输出")
        @option("-q", "--quiet", help="静默模式")
        @option(long_name="--port", type=int, default=8080, help="端口")
        def test_func(event):
            pass
        
        assert len(test_func.__command_options__) == 3
        
        # 检查选项顺序（装饰器是从下到上执行的）
        options = test_func.__command_options__
        assert options[0]['long_name'] == "--port"
        assert options[1]['long_name'] == "--quiet"
        assert options[2]['long_name'] == "--verbose"


class TestParamDecorator:
    """参数装饰器测试"""
    
    def test_basic_param_decorator(self):
        """测试基础参数装饰器"""
        @param("target", type=str, help="目标参数")
        def test_func(event):
            pass
        
        assert hasattr(test_func, '__command_params__')
        assert len(test_func.__command_params__) == 1
        
        param_spec = test_func.__command_params__[0]
        assert param_spec['name'] == "target"
        assert param_spec['type'] == str
        assert param_spec['description'] == "目标参数"
        assert param_spec['is_named'] is True
        assert param_spec['is_positional'] is False
    
    def test_param_with_default(self):
        """测试带默认值的参数"""
        @param("count", type=int, default=5, help="数量")
        def test_func(event):
            pass
        
        param_spec = test_func.__command_params__[0]
        assert param_spec['default'] == 5
        assert param_spec['required'] is None  # 让系统自动判断
    
    def test_multi_type_param_decorator(self):
        """测试多类型参数装饰器"""
        @param("input", type=[str, MessageSegment], help="输入数据")
        def test_func(event):
            pass
        
        param_spec = test_func.__command_params__[0]
        assert param_spec['type'] == [str, MessageSegment]
    
    def test_param_with_choices(self):
        """测试带选择值的参数"""
        @param("env", choices=["dev", "test", "prod"], help="环境")
        def test_func(event):
            pass
        
        param_spec = test_func.__command_params__[0]
        assert param_spec['choices'] == ["dev", "test", "prod"]
    
    def test_param_with_validation(self):
        """测试带验证的参数"""
        validator = lambda x: x > 0
        
        @param("age", type=int, validator=validator, help="年龄")
        def test_func(event):
            pass
        
        param_spec = test_func.__command_params__[0]
        assert param_spec['validator'] is validator
    
    def test_param_with_examples(self):
        """测试带示例的参数"""
        @param("file", type=str, examples=["file1.txt", "file2.txt"], help="文件")
        def test_func(event):
            pass
        
        param_spec = test_func.__command_params__[0]
        assert param_spec['examples'] == ["file1.txt", "file2.txt"]
    
    def test_param_with_type_hints(self):
        """测试带类型提示的参数"""
        type_hints = {str: "文件路径", MessageSegment: "图片文件"}
        
        @param("input", type=[str, MessageSegment], 
               type_hints=type_hints, help="输入")
        def test_func(event):
            pass
        
        param_spec = test_func.__command_params__[0]
        assert param_spec['type_hints'] == type_hints
    
    def test_multiple_params(self):
        """测试多个参数"""
        @param("source", type=str, help="源")
        @param("target", type=str, help="目标")  
        @param("count", type=int, default=1, help="数量")
        def test_func(event):
            pass
        
        assert len(test_func.__command_params__) == 3
        
        # 检查参数顺序
        params = test_func.__command_params__
        assert params[0]['name'] == "count"
        assert params[1]['name'] == "target"
        assert params[2]['name'] == "source"


class TestOptionGroupDecorator:
    """选项组装饰器测试"""
    
    def test_option_group_decorator(self):
        """测试选项组装饰器"""
        @option_group(1, name="输出格式", mutually_exclusive=True, 
                     description="选择输出格式")
        def test_func(event):
            pass
        
        assert hasattr(test_func, '__command_option_groups__')
        assert len(test_func.__command_option_groups__) == 1
        
        group_spec = test_func.__command_option_groups__[0]
        assert group_spec['group_id'] == 1
        assert group_spec['name'] == "输出格式"
        assert group_spec['mutually_exclusive'] is True
        assert group_spec['description'] == "选择输出格式"
    
    def test_multiple_option_groups(self):
        """测试多个选项组"""
        @option_group(1, name="格式组", mutually_exclusive=True)
        @option_group(2, name="模式组", required=True)
        def test_func(event):
            pass
        
        assert len(test_func.__command_option_groups__) == 2
        
        groups = test_func.__command_option_groups__
        assert groups[0]['group_id'] == 2  # 装饰器从下到上执行
        assert groups[1]['group_id'] == 1


class TestConvenienceDecorators:
    """便捷装饰器测试"""
    
    def test_str_param(self):
        """测试字符串参数装饰器"""
        @str_param("name", help="用户名")
        def test_func(event):
            pass
        
        param_spec = test_func.__command_params__[0]
        assert param_spec['type'] == str
        assert param_spec['name'] == "name"
    
    def test_int_param(self):
        """测试整数参数装饰器"""
        @int_param("age", default=18, help="年龄")
        def test_func(event):
            pass
        
        param_spec = test_func.__command_params__[0]
        assert param_spec['type'] == int
        assert param_spec['default'] == 18
    
    def test_bool_param(self):
        """测试布尔参数装饰器"""
        @bool_param("active", default=True, help="是否激活")
        def test_func(event):
            pass
        
        param_spec = test_func.__command_params__[0]
        assert param_spec['type'] == bool
        assert param_spec['default'] is True
    
    def test_user_param(self):
        """测试用户参数装饰器"""
        @user_param("target", help="目标用户")
        def test_func(event):
            pass
        
        param_spec = test_func.__command_params__[0]
        assert param_spec['type'] == CommonUnionTypes.USER_IDENTIFIER
    
    def test_text_or_image_param(self):
        """测试文本或图片参数装饰器"""
        @text_or_image_param("input", help="输入内容")
        def test_func(event):
            pass
        
        param_spec = test_func.__command_params__[0]
        assert param_spec['type'] == CommonUnionTypes.STR_OR_IMAGE
    
    def test_choice_param(self):
        """测试选择参数装饰器"""
        @choice_param("level", choices=["low", "medium", "high"], help="级别")
        def test_func(event):
            pass
        
        param_spec = test_func.__command_params__[0]
        assert param_spec['choices'] == ["low", "medium", "high"]


class TestDecoratorValidator:
    """装饰器验证器测试"""
    
    def test_validate_function_decorators_success(self):
        """测试装饰器验证成功"""
        @option("-v", "--verbose", help="详细输出")
        @option("-q", "--quiet", help="静默模式")
        @param("target", type=str, help="目标")
        def test_func(event):
            pass
        
        # 应该不抛出异常
        DecoratorValidator.validate_function_decorators(test_func)
    
    def test_validate_conflicting_option_names(self):
        """测试选项名冲突检测"""
        @option("-v", "--verbose", help="详细输出")
        @option("-v", "--debug", help="调试模式")  # 冲突的短选项名
        def test_func(event):
            pass
        
        with pytest.raises(CommandRegistrationError) as exc_info:
            DecoratorValidator.validate_function_decorators(test_func)
        
        assert "选项名冲突" in str(exc_info.value)
        assert "-v" in str(exc_info.value)
    
    def test_validate_conflicting_param_names(self):
        """测试参数名冲突检测"""
        @param("target", type=str, help="目标1")
        @param("target", type=int, help="目标2")  # 冲突的参数名
        def test_func(event):
            pass
        
        with pytest.raises(CommandRegistrationError) as exc_info:
            DecoratorValidator.validate_function_decorators(test_func)
        
        assert "参数名冲突" in str(exc_info.value)
        assert "target" in str(exc_info.value)
    
    def test_validate_option_group_reference(self):
        """测试选项组引用验证"""
        @option("--json", group=1, help="JSON格式")  # 引用未定义的组
        def test_func(event):
            pass
        
        with pytest.raises(CommandRegistrationError) as exc_info:
            DecoratorValidator.validate_function_decorators(test_func)
        
        assert "引用了未定义的选项组" in str(exc_info.value)
    
    def test_validate_function_signature_success(self):
        """测试函数签名验证成功"""
        def valid_func(event, name: str, age: int = 18):
            pass
        
        # 应该不抛出异常
        DecoratorValidator.validate_function_signature(valid_func)
    
    def test_validate_function_signature_no_event(self):
        """测试函数签名验证 - 缺少event参数"""
        def invalid_func(name: str):
            pass
        
        with pytest.raises(CommandRegistrationError) as exc_info:
            DecoratorValidator.validate_function_signature(invalid_func)
        
        assert "必须以'event'作为第一个参数" in str(exc_info.value)
    
    def test_validate_function_signature_wrong_first_param(self):
        """测试函数签名验证 - 第一个参数名错误"""
        def invalid_func(ctx, name: str):
            pass
        
        with pytest.raises(CommandRegistrationError) as exc_info:
            DecoratorValidator.validate_function_signature(invalid_func)
        
        assert "必须以'event'作为第一个参数" in str(exc_info.value)


class TestDecoratorCombinations:
    """装饰器组合测试"""
    
    def test_complex_decorator_combination(self):
        """测试复杂的装饰器组合"""
        @option("-v", "--verbose", help="详细输出")
        @option("-f", "--force", help="强制执行")
        @param("source", type=str, help="源路径")
        @param("target", type=str, help="目标路径")
        @param("count", type=int, default=1, help="数量")
        @option_group(1, name="模式", mutually_exclusive=True)
        @option("--json", group=1, help="JSON模式")
        @option("--xml", group=1, help="XML模式")
        def complex_func(event):
            pass
        
        # 验证所有装饰器信息都被正确添加
        assert len(complex_func.__command_options__) == 4
        assert len(complex_func.__command_params__) == 3
        assert len(complex_func.__command_option_groups__) == 1
        
        # 验证不会抛出异常
        DecoratorValidator.validate_function_decorators(complex_func)
    
    def test_decorator_order_independence(self):
        """测试装饰器顺序独立性"""
        # 第一种顺序
        @param("target", type=str, help="目标")
        @option("-v", "--verbose", help="详细输出")
        def func1(event):
            pass
        
        # 第二种顺序
        @option("-v", "--verbose", help="详细输出")
        @param("target", type=str, help="目标")
        def func2(event):
            pass
        
        # 两个函数应该都能通过验证
        DecoratorValidator.validate_function_decorators(func1)
        DecoratorValidator.validate_function_decorators(func2)
    
    def test_empty_decorators(self):
        """测试没有装饰器的函数"""
        def simple_func(event):
            pass
        
        # 应该能正常验证
        DecoratorValidator.validate_function_decorators(simple_func)
        DecoratorValidator.validate_function_signature(simple_func)


class TestDecoratorErrorHandling:
    """装饰器错误处理测试"""
    
    def test_option_decorator_preserves_function(self):
        """测试选项装饰器保持函数不变"""
        def original_func(event):
            """原始函数"""
            return "test"
        
        decorated_func = option("-v", "--verbose")(original_func)
        
        # 函数本身应该没有改变
        assert decorated_func is original_func
        assert decorated_func.__name__ == "original_func"
        assert decorated_func.__doc__ == "原始函数"
        assert decorated_func(None) == "test"
    
    def test_param_decorator_preserves_function(self):
        """测试参数装饰器保持函数不变"""
        def original_func(event, name: str):
            return f"Hello {name}"
        
        decorated_func = param("target", type=str)(original_func)
        
        assert decorated_func is original_func
        assert decorated_func.__name__ == "original_func"
    
    def test_decorator_attribute_initialization(self):
        """测试装饰器属性初始化"""
        def test_func(event):
            pass
        
        # 在添加装饰器之前，函数不应该有这些属性
        assert not hasattr(test_func, '__command_options__')
        assert not hasattr(test_func, '__command_params__')
        
        # 添加装饰器后应该有属性
        decorated_func = option("-v")(test_func)
        assert hasattr(decorated_func, '__command_options__')
        
        decorated_func = param("test")(decorated_func)
        assert hasattr(decorated_func, '__command_params__')


if __name__ == "__main__":
    pytest.main([__file__])
