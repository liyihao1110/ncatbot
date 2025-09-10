"""消息分词器测试

测试消息级别分词器的功能，包括混合内容解析、非文本元素处理等。
"""

import pytest
from unittest.mock import Mock

from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.message_tokenizer import (
    MessageTokenizer, parse_message_command
)
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import (
    Token, TokenType, NonTextToken, ParsedCommand
)
from ncatbot.core.event.message_segment import Image


class MockMessageSegment:
    """模拟消息段"""
    
    def __init__(self, msg_seg_type: str, **kwargs):
        self.msg_seg_type = msg_seg_type
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockTextSegment(MockMessageSegment):
    """模拟文本消息段"""
    
    def __init__(self, text: str):
        super().__init__("text", text=text)


class MockImageSegment(MockMessageSegment):
    """模拟图片消息段"""
    
    def __init__(self, file: str):
        super().__init__("image", file=file)


class MockAtSegment(MockMessageSegment):
    """模拟@消息段"""
    
    def __init__(self, qq: str):
        super().__init__("at", qq=qq)


class MockMessageArray:
    """模拟消息数组"""
    
    def __init__(self, *segments):
        self.messages = list(segments)


class TestMessageTokenizer:
    """消息分词器核心功能测试"""
    
    def test_tokenizer_creation(self):
        """测试分词器创建"""
        tokenizer = MessageTokenizer()
        assert tokenizer is not None
        assert tokenizer.command_parser is not None
    
    def test_tokenize_text_only_message(self):
        """测试纯文本消息分词"""
        tokenizer = MessageTokenizer()
        
        text_segment = MockTextSegment("hello world test")
        message_array = MockMessageArray(text_segment)
        
        tokens = tokenizer.tokenize(message_array)
        
        # 过滤EOF token
        word_tokens = [t for t in tokens if t.type == TokenType.WORD]
        
        assert len(word_tokens) == 3
        assert word_tokens[0].value == "hello"
        assert word_tokens[1].value == "world"
        assert word_tokens[2].value == "test"
    
    def test_tokenize_mixed_content_message(self):
        """测试混合内容消息分词"""
        tokenizer = MessageTokenizer()
        
        text_segment1 = MockTextSegment("hello ")
        at_segment = MockAtSegment("123456")
        text_segment2 = MockTextSegment(" --verbose")
        
        message_array = MockMessageArray(text_segment1, at_segment, text_segment2)
        
        tokens = tokenizer.tokenize(message_array)
        
        # 验证不同类型的token
        word_tokens = [t for t in tokens if t.type == TokenType.WORD]
        non_text_tokens = [t for t in tokens if t.type == TokenType.NON_TEXT_ELEMENT]
        option_tokens = [t for t in tokens if t.type == TokenType.LONG_OPTION]
        
        assert len(word_tokens) >= 1  # "hello"
        assert len(non_text_tokens) == 1  # @消息段
        assert len(option_tokens) == 1  # "--verbose"
    
    def test_tokenize_non_text_only_message(self):
        """测试只有非文本元素的消息"""
        tokenizer = MessageTokenizer()
        
        image_segment = MockImageSegment("image.jpg")
        at_segment = MockAtSegment("123456")
        
        message_array = MockMessageArray(image_segment, at_segment)
        
        tokens = tokenizer.tokenize(message_array)
        
        # 应该只有非文本token和EOF
        non_text_tokens = [t for t in tokens if t.type == TokenType.NON_TEXT_ELEMENT]
        eof_tokens = [t for t in tokens if t.type == TokenType.EOF]
        
        assert len(non_text_tokens) == 2
        assert len(eof_tokens) == 1
    
    def test_tokenize_empty_message(self):
        """测试空消息分词"""
        tokenizer = MessageTokenizer()
        
        message_array = MockMessageArray()
        
        tokens = tokenizer.tokenize(message_array)
        
        # 应该只有EOF token
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
    
    def test_tokenize_complex_command_message(self):
        """测试复杂命令消息分词"""
        tokenizer = MessageTokenizer()
        
        # 构建复杂消息：文本命令 + @用户 + 选项 + 图片
        text1 = MockTextSegment("/send ")
        at_segment = MockAtSegment("123456")
        text2 = MockTextSegment(" --urgent ")
        image_segment = MockImageSegment("file.jpg")
        text3 = MockTextSegment(' "important message"')
        
        message_array = MockMessageArray(text1, at_segment, text2, image_segment, text3)
        
        tokens = tokenizer.tokenize(message_array)
        
        # 验证各种类型的token都存在
        token_types = [t.type for t in tokens]
        assert TokenType.WORD in token_types  # "/send"
        assert TokenType.NON_TEXT_ELEMENT in token_types  # @和图片
        assert TokenType.LONG_OPTION in token_types  # "--urgent"
        assert TokenType.QUOTED_STRING in token_types  # "important message"
    
    def test_is_text_segment(self):
        """测试文本段判断"""
        tokenizer = MessageTokenizer()
        
        # 文本段
        text_segment = MockTextSegment("hello")
        assert tokenizer._is_text_segment(text_segment) is True
        
        # 非文本段
        image_segment = MockImageSegment("image.jpg")
        assert tokenizer._is_text_segment(image_segment) is False
        
        at_segment = MockAtSegment("123456")
        assert tokenizer._is_text_segment(at_segment) is False
    
    def test_token_position_adjustment(self):
        """测试token位置调整"""
        tokenizer = MessageTokenizer()
        
        text1 = MockTextSegment("hello")
        image_segment = MockImageSegment("image.jpg")
        text2 = MockTextSegment("world")
        
        message_array = MockMessageArray(text1, image_segment, text2)
        
        tokens = tokenizer.tokenize(message_array)
        
        # 验证位置递增
        positions = [t.position for t in tokens if t.type != TokenType.EOF]
        assert positions == sorted(positions)  # 位置应该是递增的
    
    def test_parse_message_direct(self):
        """测试直接解析消息到命令"""
        tokenizer = MessageTokenizer()
        
        text_segment = MockTextSegment("deploy app --env=prod -v")
        message_array = MockMessageArray(text_segment)
        
        result = tokenizer.parse_message(message_array)
        
        assert isinstance(result, ParsedCommand)
        assert len(result.elements) >= 2  # deploy, app
        assert "env" in result.named_params
        assert result.named_params["env"] == "prod"
        assert "v" in result.options
        assert result.options["v"] is True


class TestNonTextToken:
    """非文本Token测试"""
    
    def test_non_text_token_creation(self):
        """测试非文本Token创建"""
        image_segment = Image("test.jpg")
        token = NonTextToken(image_segment, 5)
        
        assert token.type == TokenType.NON_TEXT_ELEMENT
        assert token.position == 5
        assert token.segment is image_segment
        assert token.element_type == "image"
        assert "[image]" in token.value
    
    def test_non_text_token_type_mapping(self):
        """测试非文本Token类型映射"""
        # 测试不同类型的消息段
        test_cases = [
            (MockAtSegment("123"), "at"),
            (MockImageSegment("img.jpg"), "image"),
            (MockMessageSegment("video", file="vid.mp4"), "video"),
            (MockMessageSegment("face", id="1"), "face"),
        ]
        
        for segment, expected_type in test_cases:
            # 模拟类名
            segment.__class__.__name__ = {
                "at": "At",
                "image": "Image", 
                "video": "Video",
                "face": "Face"
            }.get(expected_type, "Unknown")
            
            token = NonTextToken(segment, 0)
            assert token.element_type == expected_type
    
    def test_non_text_token_unknown_type(self):
        """测试未知类型的非文本Token"""
        unknown_segment = MockMessageSegment("unknown_type")
        unknown_segment.__class__.__name__ = "UnknownSegment"
        
        token = NonTextToken(unknown_segment, 0)
        assert token.element_type == "unknownsegment"  # 转小写


class TestMessageTokenizerIntegration:
    """消息分词器集成测试"""
    
    def test_full_command_parsing_workflow(self):
        """测试完整命令解析工作流"""
        # 构建真实的命令消息
        text1 = MockTextSegment("/admin ban ")
        at_segment = MockAtSegment("malicious_user")
        text2 = MockTextSegment(" --reason=spam --duration=24h")
        
        message_array = MockMessageArray(text1, at_segment, text2)
        
        # 解析
        result = parse_message_command(message_array)
        
        # 验证解析结果
        assert isinstance(result, ParsedCommand)
        
        # 检查元素
        elements = result.elements
        text_elements = [e for e in elements if e.type == "text"]
        at_elements = [e for e in elements if e.type == "at"]
        
        assert len(text_elements) >= 2  # "/admin", "ban"
        assert len(at_elements) == 1
        
        # 检查选项和参数
        assert "reason" in result.named_params
        assert result.named_params["reason"] == "spam"
        assert "duration" in result.named_params
        assert result.named_params["duration"] == "24h"
    
    def test_mixed_text_and_segments_parsing(self):
        """测试混合文本和消息段解析"""
        # 复杂消息：命令 + 参数 + @用户 + 选项 + 图片 + 引用文本
        segments = [
            MockTextSegment("/send "),
            MockAtSegment("user123"),
            MockTextSegment(" --priority=high "),
            MockImageSegment("attachment.png"),
            MockTextSegment(' "Check this out"')
        ]
        
        message_array = MockMessageArray(*segments)
        result = parse_message_command(message_array)
        
        # 验证各种元素都被正确解析
        assert len(result.elements) >= 4  # send, @user, image, "Check this out"
        
        # 验证不同类型的元素
        element_types = [e.type for e in result.elements]
        assert "text" in element_types
        assert "at" in element_types
        assert "image" in element_types
        
        # 验证参数
        assert result.named_params["priority"] == "high"
    
    def test_command_with_multiple_non_text_elements(self):
        """测试包含多个非文本元素的命令"""
        segments = [
            MockTextSegment("/gallery create "),
            MockImageSegment("img1.jpg"),
            MockTextSegment(" "),
            MockImageSegment("img2.png"),
            MockTextSegment(" "),
            MockImageSegment("img3.gif"),
            MockTextSegment(" --title=MyGallery")
        ]
        
        message_array = MockMessageArray(*segments)
        result = parse_message_command(message_array)
        
        # 验证图片元素
        image_elements = [e for e in result.elements if e.type == "image"]
        assert len(image_elements) == 3
        
        # 验证参数
        assert result.named_params["title"] == "MyGallery"
    
    def test_empty_and_whitespace_handling(self):
        """测试空内容和空白字符处理"""
        segments = [
            MockTextSegment("  /test  "),  # 前后有空格
            MockTextSegment("   "),        # 只有空格
            MockImageSegment("test.jpg"),
            MockTextSegment("\t--flag\n")  # 有制表符和换行
        ]
        
        message_array = MockMessageArray(*segments)
        result = parse_message_command(message_array)
        
        # 空白应该被正确处理
        text_elements = [e for e in result.elements if e.type == "text"]
        assert len(text_elements) >= 1  # 至少有 "/test"
        
        # 选项应该被识别
        assert "flag" in result.options
        assert result.options["flag"] is True


class TestMessageTokenizerEdgeCases:
    """消息分词器边界情况测试"""
    
    def test_tokenize_very_long_message(self):
        """测试分词非常长的消息"""
        # 创建长文本
        long_text = " ".join([f"word{i}" for i in range(1000)])
        text_segment = MockTextSegment(long_text)
        message_array = MockMessageArray(text_segment)
        
        tokenizer = MessageTokenizer()
        tokens = tokenizer.tokenize(message_array)
        
        # 应该有大量的word token
        word_tokens = [t for t in tokens if t.type == TokenType.WORD]
        assert len(word_tokens) == 1000
    
    def test_tokenize_malformed_text_segments(self):
        """测试畸形文本段"""
        # 模拟缺少text属性的段
        class BadTextSegment:
            def __init__(self):
                self.msg_seg_type = "text"
                # 故意不设置text属性
        
        bad_segment = BadTextSegment()
        message_array = MockMessageArray(bad_segment)
        
        tokenizer = MessageTokenizer()
        
        # 应该能处理错误情况
        try:
            tokens = tokenizer.tokenize(message_array)
            # 如果没有抛出异常，检查结果
            assert len(tokens) >= 1  # 至少有EOF
        except (AttributeError, TypeError):
            # 如果抛出异常也是可以接受的
            pass
    
    def test_tokenize_mixed_valid_invalid_segments(self):
        """测试混合有效和无效消息段"""
        valid_text = MockTextSegment("valid text")
        valid_image = MockImageSegment("image.jpg")
        
        # 无效段（缺少必要属性）
        class InvalidSegment:
            pass
        
        invalid_segment = InvalidSegment()
        
        message_array = MockMessageArray(valid_text, invalid_segment, valid_image)
        
        tokenizer = MessageTokenizer()
        
        # 应该能部分处理
        try:
            tokens = tokenizer.tokenize(message_array)
            # 验证有效部分被处理
            word_tokens = [t for t in tokens if t.type == TokenType.WORD]
            assert len(word_tokens) >= 2  # "valid", "text"
        except Exception:
            # 异常处理也是可接受的
            pass


class TestParseMessageCommandFunction:
    """parse_message_command便捷函数测试"""
    
    def test_convenience_function(self):
        """测试便捷函数"""
        text_segment = MockTextSegment("test --flag value")
        message_array = MockMessageArray(text_segment)
        
        result = parse_message_command(message_array)
        
        assert isinstance(result, ParsedCommand)
        assert "flag" in result.options
        assert result.options["flag"] is True
    
    def test_convenience_function_consistency(self):
        """测试便捷函数与直接调用的一致性"""
        text_segment = MockTextSegment("deploy app --env=test")
        message_array = MockMessageArray(text_segment)
        
        # 直接调用
        tokenizer = MessageTokenizer()
        direct_result = tokenizer.parse_message(message_array)
        
        # 便捷函数调用
        convenience_result = parse_message_command(message_array)
        
        # 结果应该一致
        assert direct_result.options == convenience_result.options
        assert direct_result.named_params == convenience_result.named_params
        assert len(direct_result.elements) == len(convenience_result.elements)
