"""异常系统测试

测试各种异常类型、错误处理和格式化功能。
"""

import pytest
from typing import List, Dict
from unittest.mock import Mock

from ..exceptions import (
    CommandSystemError, CommandRegistrationError, ParameterError,
    ValidationError, ArgumentError, OptionError, CommandNotFoundError,
    TypeConversionError, MultiTypeConversionError, MutuallyExclusiveError,
    MissingRequiredParameterError, TooManyArgumentsError,
    ErrorContext, ErrorHandler
)


class TestCommandSystemError:
    """基础异常类测试"""
    
    def test_basic_error_creation(self):
        """测试基础错误创建"""
        error = CommandSystemError("测试错误")
        assert str(error) == "测试错误"
        assert error.message == "测试错误"
        assert error.details == ""
        assert error.suggestions == []
    
    def test_error_with_details(self):
        """测试带详细信息的错误"""
        error = CommandSystemError(
            "测试错误",
            details="详细信息",
            suggestions=["建议1", "建议2"]
        )
        
        error_str = str(error)
        assert "测试错误" in error_str
        assert "详细信息: 详细信息" in error_str
        assert "建议: 建议1; 建议2" in error_str
    
    def test_error_with_only_suggestions(self):
        """测试只有建议的错误"""
        error = CommandSystemError(
            "测试错误",
            suggestions=["建议1"]
        )
        
        error_str = str(error)
        assert "测试错误" in error_str
        assert "建议: 建议1" in error_str


class TestCommandRegistrationError:
    """命令注册错误测试"""
    
    def test_registration_error_creation(self):
        """测试注册错误创建"""
        error = CommandRegistrationError("test_command", "注册失败")
        
        assert error.command_name == "test_command"
        assert "命令 'test_command' 注册失败" in str(error)
        assert "注册失败" in str(error)
    
    def test_registration_error_with_suggestions(self):
        """测试带建议的注册错误"""
        error = CommandRegistrationError(
            "test_command",
            "参数冲突",
            suggestions=["检查参数名", "修改装饰器"]
        )
        
        error_str = str(error)
        assert "检查参数名" in error_str
        assert "修改装饰器" in error_str


class TestParameterError:
    """参数错误测试"""
    
    def test_parameter_error_creation(self):
        """测试参数错误创建"""
        error = ParameterError("test_param", "类型无效")
        
        assert error.param_name == "test_param"
        assert "参数 'test_param' 定义错误" in str(error)
        assert "类型无效" in str(error)


class TestValidationError:
    """验证错误测试"""
    
    def test_validation_error_creation(self):
        """测试验证错误创建"""
        error = ValidationError("age", 150, "int")
        
        assert error.param_name == "age"
        assert error.value == 150
        assert error.expected_type == "int"
        assert "参数 'age' 验证失败" in str(error)


class TestArgumentError:
    """参数错误测试"""
    
    def test_argument_error_creation(self):
        """测试参数错误创建"""
        error = ArgumentError("deploy", "缺少必需参数")
        
        assert error.command_name == "deploy"
        assert "命令 'deploy' 参数错误" in str(error)
        assert "缺少必需参数" in str(error)


class TestOptionError:
    """选项错误测试"""
    
    def test_option_error_creation(self):
        """测试选项错误创建"""
        error = OptionError("--verbose", "未知选项")
        
        assert error.option_name == "--verbose"
        assert "选项 '--verbose' 错误" in str(error)
        assert "未知选项" in str(error)


class TestCommandNotFoundError:
    """命令不存在错误测试"""
    
    def test_command_not_found_creation(self):
        """测试命令不存在错误创建"""
        available_commands = ["deploy", "backup", "status"]
        error = CommandNotFoundError("deploi", available_commands)
        
        assert error.command_name == "deploi"
        assert error.available_commands == available_commands
        assert "未知命令 'deploi'" in str(error)
    
    def test_similar_commands_suggestion(self):
        """测试相似命令建议"""
        available_commands = ["deploy", "backup", "status", "debug"]
        error = CommandNotFoundError("deploi", available_commands)
        
        # 应该建议相似的命令
        error_str = str(error)
        assert "deploy" in error_str  # deploi 和 deploy 很相似
    
    def test_no_similar_commands(self):
        """测试没有相似命令的情况"""
        available_commands = ["backup", "status"]
        error = CommandNotFoundError("xyz", available_commands)
        
        error_str = str(error)
        # 应该显示可用命令列表
        assert "backup" in error_str
        assert "status" in error_str
    
    def test_find_similar_commands(self):
        """测试相似命令查找算法"""
        available_commands = ["deploy", "backup", "status", "debug"]
        error = CommandNotFoundError("test", available_commands)
        
        similar = error._find_similar_commands("deploy", available_commands)
        assert "deploy" in similar
        
        similar = error._find_similar_commands("deploi", available_commands)
        assert "deploy" in similar
        
        similar = error._find_similar_commands("xyz", available_commands)
        assert len(similar) == 0  # 没有相似的


class TestTypeConversionError:
    """类型转换错误测试"""
    
    def test_type_conversion_error_creation(self):
        """测试类型转换错误创建"""
        error = TypeConversionError(
            "age", "abc", "int", ["无法解析为整数"]
        )
        
        assert error.param_name == "age"
        assert error.value == "abc"
        assert error.expected_type == "int"
        assert error.conversion_errors == ["无法解析为整数"]
        
        error_str = str(error)
        assert "值 'abc'" in error_str
        assert "无法转换为 int" in error_str


class TestMultiTypeConversionError:
    """多类型转换错误测试"""
    
    def test_multi_type_conversion_error_creation(self):
        """测试多类型转换错误创建"""
        type_errors = {
            "str": "不是有效字符串",
            "int": "无法解析为整数"
        }
        type_hints = {
            "str": "文本内容",
            "int": "整数值"
        }
        
        error = MultiTypeConversionError(
            "input", "invalid", ["str", "int"], 
            type_errors, type_hints
        )
        
        assert error.param_name == "input"
        assert error.value == "invalid"
        assert error.supported_types == ["str", "int"]
        assert error.type_errors == type_errors
        assert error.type_hints == type_hints
        
        error_str = str(error)
        assert "无法转换为任何支持的类型" in error_str
        assert "str: 不是有效字符串" in error_str
        assert "int: 无法解析为整数" in error_str
        assert "str: 文本内容" in error_str


class TestMutuallyExclusiveError:
    """互斥选项错误测试"""
    
    def test_mutually_exclusive_error_creation(self):
        """测试互斥选项错误创建"""
        error = MutuallyExclusiveError(["--json", "--xml"])
        
        assert error.conflicting_options == ["--json", "--xml"]
        error_str = str(error)
        assert "--json 和 --xml 不能同时使用" in error_str
        assert "请只选择其中一个" in error_str


class TestMissingRequiredParameterError:
    """缺少必需参数错误测试"""
    
    def test_missing_required_parameter_error_creation(self):
        """测试缺少必需参数错误创建"""
        error = MissingRequiredParameterError("deploy", "app_name", "str")
        
        assert error.command_name == "deploy"
        assert error.param_name == "app_name"
        assert error.param_type == "str"
        
        error_str = str(error)
        assert "缺少必需参数 'app_name'" in error_str
        assert "参数类型: str" in error_str
        assert "请提供 app_name 参数" in error_str


class TestTooManyArgumentsError:
    """参数过多错误测试"""
    
    def test_too_many_arguments_error_creation(self):
        """测试参数过多错误创建"""
        error = TooManyArgumentsError("greet", 2, 5)
        
        assert error.command_name == "greet"
        assert error.expected_count == 2
        assert error.actual_count == 5
        
        error_str = str(error)
        assert "参数过多" in error_str
        assert "期望 2 个参数，实际收到 5 个" in error_str
        assert "检查是否有多余的参数" in error_str


class TestErrorContext:
    """错误上下文测试"""
    
    def test_error_context_creation(self):
        """测试错误上下文创建"""
        context = ErrorContext(
            command_name="deploy",
            input_text="/deploy myapp --env=prod",
            current_position=10,
            available_commands=["deploy", "backup"],
            similar_commands=["deploy"],
            expected_parameters=["app_name"],
            provided_parameters=["myapp"]
        )
        
        assert context.command_name == "deploy"
        assert context.input_text == "/deploy myapp --env=prod"
        assert context.current_position == 10
        assert context.available_commands == ["deploy", "backup"]
        assert context.similar_commands == ["deploy"]
        assert context.expected_parameters == ["app_name"]
        assert context.provided_parameters == ["myapp"]


class TestErrorHandler:
    """错误处理器测试"""
    
    def test_error_handler_creation(self):
        """测试错误处理器创建"""
        handler = ErrorHandler()
        assert handler.error_formatters is not None
        assert len(handler.error_formatters) > 0
    
    def test_format_command_not_found_error(self):
        """测试格式化命令不存在错误"""
        handler = ErrorHandler()
        error = CommandNotFoundError("deploi", ["deploy", "backup", "status"])
        
        formatted = handler.format_error(error)
        
        assert "❌" in formatted
        assert "deploi" in formatted
        assert "💡" in formatted  # 应该有建议
        assert "📋" in formatted  # 应该有命令列表
        assert "❓" in formatted  # 应该有帮助提示
    
    def test_format_argument_error(self):
        """测试格式化参数错误"""
        handler = ErrorHandler()
        error = ArgumentError("deploy", "缺少参数", 
                            details="需要应用名称",
                            suggestions=["添加应用名称"])
        
        formatted = handler.format_error(error)
        
        assert "❌" in formatted
        assert "缺少参数" in formatted
        assert "📝 需要应用名称" in formatted
        assert "💡 建议: 添加应用名称" in formatted
    
    def test_format_validation_error(self):
        """测试格式化验证错误"""
        handler = ErrorHandler()
        error = ValidationError("age", 150, "int (0-120)")
        
        formatted = handler.format_error(error)
        
        assert "❌" in formatted
        assert "参数验证失败" in formatted
        assert "📝 参数: age" in formatted
        assert "📝 输入值: 150" in formatted
        assert "📝 期望类型: int (0-120)" in formatted
    
    def test_format_multi_type_error(self):
        """测试格式化多类型转换错误"""
        handler = ErrorHandler()
        
        type_errors = {"str": "不是字符串", "int": "不是整数"}
        type_hints = {"str": "文本内容", "int": "整数值"}
        
        error = MultiTypeConversionError(
            "input", "invalid", ["str", "int"],
            type_errors, type_hints
        )
        
        formatted = handler.format_error(error)
        
        assert "❌" in formatted
        assert "类型错误" in formatted
        assert "📝 您的输入: invalid" in formatted
        assert "✅ 支持的类型:" in formatted
        assert "1. str - 文本内容" in formatted
        assert "2. int - 整数值" in formatted
        assert "💡" in formatted
    
    def test_format_default_error(self):
        """测试格式化默认错误"""
        handler = ErrorHandler()
        error = CommandSystemError("未知错误")
        
        formatted = handler.format_error(error)
        assert "❌ 未知错误" in formatted
    
    def test_calculate_similarity(self):
        """测试相似度计算"""
        handler = ErrorHandler()
        
        # 完全相同
        similarity = handler._calculate_similarity("deploy", "deploy")
        assert similarity == 1.0
        
        # 相似
        similarity = handler._calculate_similarity("deploy", "deploi")
        assert similarity > 0.5
        
        # 不相似
        similarity = handler._calculate_similarity("deploy", "xyz")
        assert similarity < 0.5
    
    def test_format_error_with_context(self):
        """测试带上下文的错误格式化"""
        handler = ErrorHandler()
        error = ArgumentError("deploy", "参数错误")
        
        context = ErrorContext(
            command_name="deploy",
            input_text="/deploy",
            current_position=0,
            available_commands=["deploy", "backup"],
            similar_commands=[],
            expected_parameters=["app_name"],
            provided_parameters=[]
        )
        
        formatted = handler.format_error(error, context)
        assert "❌" in formatted
        assert "deploy" in formatted


class TestErrorInheritance:
    """错误继承关系测试"""
    
    def test_error_inheritance(self):
        """测试错误继承关系"""
        # 所有错误应该继承自 CommandSystemError
        assert issubclass(CommandRegistrationError, CommandSystemError)
        assert issubclass(ParameterError, CommandSystemError)
        assert issubclass(ValidationError, CommandSystemError)
        assert issubclass(ArgumentError, CommandSystemError)
        assert issubclass(OptionError, CommandSystemError)
        assert issubclass(CommandNotFoundError, CommandSystemError)
        assert issubclass(TypeConversionError, ValidationError)
        assert issubclass(MultiTypeConversionError, TypeConversionError)
        assert issubclass(MutuallyExclusiveError, OptionError)
        assert issubclass(MissingRequiredParameterError, ArgumentError)
        assert issubclass(TooManyArgumentsError, ArgumentError)
    
    def test_exception_catching(self):
        """测试异常捕获"""
        # 应该能用基类捕获子类异常
        try:
            raise TypeConversionError("test", "value", "int", ["error"])
        except CommandSystemError as e:
            assert isinstance(e, TypeConversionError)
            assert isinstance(e, ValidationError)
            assert isinstance(e, CommandSystemError)
        
        try:
            raise MutuallyExclusiveError(["--a", "--b"])
        except CommandSystemError as e:
            assert isinstance(e, MutuallyExclusiveError)
            assert isinstance(e, OptionError)
            assert isinstance(e, CommandSystemError)


if __name__ == "__main__":
    pytest.main([__file__])
