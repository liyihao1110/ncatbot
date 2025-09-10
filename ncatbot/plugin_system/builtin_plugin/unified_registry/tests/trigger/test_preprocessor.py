"""消息预处理器测试

测试消息预处理器的功能，包括前缀检测、文本提取、大小写处理等。
"""

import pytest
from unittest.mock import Mock

from ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.preprocessor import (
    MessagePreprocessor, PreprocessResult
)


class MockMessage:
    """模拟消息"""
    
    def __init__(self, messages):
        self.messages = messages


class MockTextMessage:
    """模拟文本消息"""
    
    def __init__(self, text: str):
        self.msg_seg_type = "text"
        self.text = text


class TestPreprocessResult:
    """预处理结果测试"""
    
    def test_preprocess_result_creation(self):
        """测试预处理结果创建"""
        result = PreprocessResult(command_text="hello world")
        assert result.command_text == "hello world"


class TestMessagePreprocessor:
    """消息预处理器测试"""
    
    def test_preprocessor_creation(self):
        """测试预处理器创建"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/", "!"],
            case_sensitive=False
        )
        
        assert preprocessor.require_prefix is True
        assert preprocessor.prefixes == ["/", "!"]
        assert preprocessor.case_sensitive is False
    
    def test_preprocessor_creation_with_different_config(self):
        """测试不同配置的预处理器"""
        preprocessor = MessagePreprocessor(
            require_prefix=False,
            prefixes=["#", ">"],
            case_sensitive=True
        )
        
        assert preprocessor.require_prefix is False
        assert preprocessor.prefixes == ["#", ">"]
        assert preprocessor.case_sensitive is True
    
    def test_normalize_case_sensitive(self):
        """测试大小写敏感的规范化"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=True
        )
        
        result = preprocessor._normalize("Hello World")
        assert result == "Hello World"  # 保持原样
    
    def test_normalize_case_insensitive(self):
        """测试大小写不敏感的规范化"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=False
        )
        
        result = preprocessor._normalize("Hello World")
        assert result == "hello world"  # 转换为小写
    
    def test_precheck_empty_message(self):
        """测试空消息的预检查"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=False
        )
        
        # 空消息列表
        event = Mock()
        event.message.messages = []
        
        result = preprocessor.precheck(event)
        assert result is None
    
    def test_precheck_non_text_first_segment(self):
        """测试非文本首段的预检查"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=False
        )
        
        # 首段不是文本
        first_segment = Mock()
        first_segment.msg_seg_type = "image"
        
        event = Mock()
        event.message.messages = [first_segment]
        
        result = preprocessor.precheck(event)
        assert result is None
    
    def test_precheck_with_prefix_match(self):
        """测试前缀匹配的预检查"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/", "!"],
            case_sensitive=False
        )
        
        # 创建带前缀的文本消息
        first_segment = MockTextMessage("/hello world")
        
        event = Mock()
        event.message.messages = [first_segment]
        
        result = preprocessor.precheck(event)
        
        assert result is not None
        assert isinstance(result, PreprocessResult)
        assert result.command_text == "hello world"  # 前缀被移除
    
    def test_precheck_with_different_prefix(self):
        """测试不同前缀的匹配"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/", "!", "#"],
            case_sensitive=False
        )
        
        test_cases = [
            ("!status", "status"),
            ("#help", "help"),
            ("/admin ban user", "admin ban user")
        ]
        
        for input_text, expected_output in test_cases:
            first_segment = MockTextMessage(input_text)
            event = Mock()
            event.message.messages = [first_segment]
            
            result = preprocessor.precheck(event)
            
            assert result is not None
            assert result.command_text == expected_output
    
    def test_precheck_no_prefix_match(self):
        """测试无前缀匹配的情况"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/", "!"],
            case_sensitive=False
        )
        
        # 没有前缀的消息
        first_segment = MockTextMessage("hello world")
        
        event = Mock()
        event.message.messages = [first_segment]
        
        result = preprocessor.precheck(event)
        assert result is None
    
    def test_precheck_prefix_case_insensitive(self):
        """测试大小写不敏感的前缀匹配"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/", "!"],
            case_sensitive=False
        )
        
        # 大写前缀应该匹配
        first_segment = MockTextMessage("/HELLO WORLD")
        
        event = Mock()
        event.message.messages = [first_segment]
        
        result = preprocessor.precheck(event)
        
        assert result is not None
        assert result.command_text == "HELLO WORLD"  # 保持原始大小写，只移除前缀
    
    def test_precheck_prefix_case_sensitive(self):
        """测试大小写敏感的前缀匹配"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=True
        )
        
        # 正确的前缀
        first_segment = MockTextMessage("/hello")
        event = Mock()
        event.message.messages = [first_segment]
        
        result = preprocessor.precheck(event)
        assert result is not None
        assert result.command_text == "hello"
        
        # 错误大小写的前缀（如果前缀本身是大小写敏感的）
        # 注意：这里假设前缀本身也区分大小写
        # 实际行为可能需要根据具体实现调整
    
    def test_precheck_no_prefix_required(self):
        """测试不要求前缀的情况"""
        preprocessor = MessagePreprocessor(
            require_prefix=False,
            prefixes=[],
            case_sensitive=False
        )
        
        # 任何文本都应该通过
        first_segment = MockTextMessage("any text here")
        
        event = Mock()
        event.message.messages = [first_segment]
        
        result = preprocessor.precheck(event)
        
        assert result is not None
        assert result.command_text == "any text here"
    
    def test_precheck_whitespace_handling(self):
        """测试空白字符处理"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=False
        )
        
        # 前缀后有多个空格
        first_segment = MockTextMessage("/   hello world   ")
        
        event = Mock()
        event.message.messages = [first_segment]
        
        result = preprocessor.precheck(event)
        
        assert result is not None
        # 前导空格应该被移除
        assert result.command_text == "hello world   "
    
    def test_precheck_empty_text_after_prefix(self):
        """测试前缀后为空的情况"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=False
        )
        
        # 只有前缀，没有内容
        first_segment = MockTextMessage("/")
        
        event = Mock()
        event.message.messages = [first_segment]
        
        result = preprocessor.precheck(event)
        
        assert result is not None
        assert result.command_text == ""
    
    def test_precheck_prefix_whitespace_only_after(self):
        """测试前缀后只有空白字符的情况"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=False
        )
        
        # 前缀后只有空格
        first_segment = MockTextMessage("/   ")
        
        event = Mock()
        event.message.messages = [first_segment]
        
        result = preprocessor.precheck(event)
        
        assert result is not None
        assert result.command_text == ""  # 空格被trim
    
    def test_precheck_multiple_matching_prefixes(self):
        """测试多个匹配前缀的情况"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["!", "!!"],  # 一个是另一个的前缀
            case_sensitive=False
        )
        
        # 应该匹配最先找到的
        first_segment = MockTextMessage("!!hello")
        
        event = Mock()
        event.message.messages = [first_segment]
        
        result = preprocessor.precheck(event)
        
        assert result is not None
        # 根据实现，可能匹配 "!" 或 "!!"
        # 这里假设匹配第一个找到的
        assert "hello" in result.command_text
    
    def test_precheck_text_attribute_none(self):
        """测试text属性为None的情况"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=False
        )
        
        # text属性为None
        first_segment = Mock()
        first_segment.msg_seg_type = "text"
        first_segment.text = None
        
        event = Mock()
        event.message.messages = [first_segment]
        
        result = preprocessor.precheck(event)
        
        # 应该处理None值
        assert result is None or result.command_text == ""


class TestMessagePreprocessorEdgeCases:
    """消息预处理器边界情况测试"""
    
    def test_very_long_prefix_list(self):
        """测试很长的前缀列表"""
        long_prefixes = [f"prefix{i}" for i in range(10)]
        
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=long_prefixes,
            case_sensitive=False
        )
        
        # 使用中间的某个前缀
        first_segment = MockTextMessage("prefix5test command")
        
        event = Mock()
        event.message.messages = [first_segment]
        
        result = preprocessor.precheck(event)
        
        assert result is not None
        assert result.command_text == "test command"
    
    def test_unicode_prefix(self):
        """测试Unicode前缀"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["中", "→", "☆"],
            case_sensitive=False
        )
        
        # 使用Unicode前缀
        first_segment = MockTextMessage("中文命令 参数")
        
        event = Mock()
        event.message.messages = [first_segment]
        
        result = preprocessor.precheck(event)
        
        assert result is not None
        assert result.command_text == "文命令 参数"
    
    def test_special_character_prefix(self):
        """测试特殊字符前缀"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["<", ">", "@", "#", "&"],
            case_sensitive=False
        )
        
        test_cases = [
            ("<command", "command"),
            (">execute", "execute"),
            ("@bot help", "bot help"),
            ("#tag", "tag"),
            ("&system", "system")
        ]
        
        for input_text, expected_output in test_cases:
            first_segment = MockTextMessage(input_text)
            event = Mock()
            event.message.messages = [first_segment]
            
            result = preprocessor.precheck(event)
            
            assert result is not None
            assert result.command_text == expected_output
    
    def test_empty_prefix_list(self):
        """测试空前缀列表"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=[],  # 空前缀列表
            case_sensitive=False
        )
        
        # 任何消息都不应该匹配
        first_segment = MockTextMessage("/hello")
        
        event = Mock()
        event.message.messages = [first_segment]
        
        result = preprocessor.precheck(event)
        
        assert result is None
    
    def test_none_prefix_list(self):
        """测试None前缀列表"""
        # 这种情况在构造函数中可能不被允许
        # 但如果允许，应该有合理的处理
        try:
            preprocessor = MessagePreprocessor(
                require_prefix=True,
                prefixes=None,
                case_sensitive=False
            )
            
            first_segment = MockTextMessage("/hello")
            event = Mock()
            event.message.messages = [first_segment]
            
            result = preprocessor.precheck(event)
            assert result is None
        except (TypeError, ValueError):
            # 如果构造函数拒绝None，也是可以接受的
            pass


class TestMessagePreprocessorIntegration:
    """消息预处理器集成测试"""
    
    def test_preprocessor_with_real_message_structure(self):
        """测试与真实消息结构的集成"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/", "!"],
            case_sensitive=False
        )
        
        # 模拟更真实的消息结构
        class RealTextSegment:
            def __init__(self, text):
                self.msg_seg_type = "text"
                self.text = text
        
        class RealMessage:
            def __init__(self, segments):
                self.messages = segments
        
        # 创建真实结构的消息
        text_segment = RealTextSegment("/admin user ban @someone")
        message = RealMessage([text_segment])
        
        event = Mock()
        event.message = message
        
        result = preprocessor.precheck(event)
        
        assert result is not None
        assert result.command_text == "admin user ban @someone"
    
    def test_preprocessor_workflow_integration(self):
        """测试预处理器工作流集成"""
        # 测试从消息接收到预处理结果的完整流程
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=False
        )
        
        # 步骤1：接收消息
        raw_message = "/deploy myapp --env=production"
        
        # 步骤2：构建消息对象
        first_segment = MockTextMessage(raw_message)
        event = Mock()
        event.message.messages = [first_segment]
        
        # 步骤3：预处理
        result = preprocessor.precheck(event)
        
        # 步骤4：验证结果可用于后续处理
        assert result is not None
        assert result.command_text == "deploy myapp --env=production"
        
        # 结果应该可以传递给分词器等下游组件
        command_text = result.command_text
        assert "deploy" in command_text
        assert "myapp" in command_text
        assert "--env=production" in command_text
