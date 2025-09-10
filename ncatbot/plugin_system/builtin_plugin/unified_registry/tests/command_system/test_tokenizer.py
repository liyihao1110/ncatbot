"""词法分析器测试

测试字符串分词器的功能，包括基本分词、选项解析、引用字符串、转义序列等。
"""

import pytest
from unittest.mock import Mock

from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import (
    StringTokenizer, Token, TokenType, QuoteState, AdvancedCommandParser,
    QuoteMismatchError, InvalidEscapeSequenceError, Element, ParsedCommand
)


class TestToken:
    """Token类测试"""
    
    def test_token_creation(self):
        """测试Token创建"""
        token = Token(TokenType.WORD, "hello", 0)
        assert token.type == TokenType.WORD
        assert token.value == "hello"
        assert token.position == 0
    
    def test_token_str_representation(self):
        """测试Token字符串表示"""
        token = Token(TokenType.LONG_OPTION, "verbose", 5)
        str_repr = str(token)
        assert "long_option" in str_repr
        assert "verbose" in str_repr
        assert "pos=5" in str_repr
    
    def test_token_repr(self):
        """测试Token repr"""
        token = Token(TokenType.SHORT_OPTION, "v", 10)
        repr_str = repr(token)
        assert repr_str == str(token)


class TestStringTokenizer:
    """字符串分词器测试"""
    
    def test_tokenizer_creation(self):
        """测试分词器创建"""
        tokenizer = StringTokenizer("test input")
        assert tokenizer.text == "test input"
        assert tokenizer.length == 10
        assert tokenizer.position == 0
    
    def test_basic_word_tokenization(self):
        """测试基本单词分词"""
        tokenizer = StringTokenizer("hello world test")
        tokens = tokenizer.tokenize()
        
        # 过滤EOF token
        word_tokens = [t for t in tokens if t.type != TokenType.EOF]
        
        assert len(word_tokens) == 3
        assert word_tokens[0].type == TokenType.WORD
        assert word_tokens[0].value == "hello"
        assert word_tokens[1].type == TokenType.WORD
        assert word_tokens[1].value == "world"
        assert word_tokens[2].type == TokenType.WORD
        assert word_tokens[2].value == "test"
    
    def test_short_option_parsing(self):
        """测试短选项解析"""
        tokenizer = StringTokenizer("-v -x -abc")
        tokens = tokenizer.tokenize()
        
        option_tokens = [t for t in tokens if t.type == TokenType.SHORT_OPTION]
        
        assert len(option_tokens) == 3
        assert option_tokens[0].value == "v"
        assert option_tokens[1].value == "x"
        assert option_tokens[2].value == "abc"  # 组合选项
    
    def test_long_option_parsing(self):
        """测试长选项解析"""
        tokenizer = StringTokenizer("--verbose --help --debug-mode")
        tokens = tokenizer.tokenize()
        
        option_tokens = [t for t in tokens if t.type == TokenType.LONG_OPTION]
        
        assert len(option_tokens) == 3
        assert option_tokens[0].value == "verbose"
        assert option_tokens[1].value == "help"
        assert option_tokens[2].value == "debug-mode"
    
    def test_option_with_assignment(self):
        """测试带赋值的选项"""
        tokenizer = StringTokenizer("-p=1234 --env=production")
        tokens = tokenizer.tokenize()
        
        # 查找选项、分隔符和值
        short_option = next(t for t in tokens if t.type == TokenType.SHORT_OPTION)
        long_option = next(t for t in tokens if t.type == TokenType.LONG_OPTION)
        separators = [t for t in tokens if t.type == TokenType.SEPARATOR]
        words = [t for t in tokens if t.type == TokenType.WORD]
        
        assert short_option.value == "p"
        assert long_option.value == "env"
        assert len(separators) == 2
        assert "1234" in [w.value for w in words]
        assert "production" in [w.value for w in words]
    
    def test_quoted_string_parsing(self):
        """测试引用字符串解析"""
        tokenizer = StringTokenizer('"hello world" "test string"')
        tokens = tokenizer.tokenize()
        
        quoted_tokens = [t for t in tokens if t.type == TokenType.QUOTED_STRING]
        
        assert len(quoted_tokens) == 2
        assert quoted_tokens[0].value == "hello world"
        assert quoted_tokens[1].value == "test string"
    
    def test_escape_sequences(self):
        """测试转义序列"""
        tokenizer = StringTokenizer(r'"hello \"world\"" "line1\nline2" "tab\there"')
        tokens = tokenizer.tokenize()
        
        quoted_tokens = [t for t in tokens if t.type == TokenType.QUOTED_STRING]
        
        assert len(quoted_tokens) == 3
        assert quoted_tokens[0].value == 'hello "world"'
        assert quoted_tokens[1].value == "line1\nline2"
        assert quoted_tokens[2].value == "tab\there"
    
    def test_mixed_content_parsing(self):
        """测试混合内容解析"""
        tokenizer = StringTokenizer('deploy app --env=prod -v "config file" --force')
        tokens = tokenizer.tokenize()
        
        # 过滤EOF
        tokens = [t for t in tokens if t.type != TokenType.EOF]
        
        # 验证不同类型的token都存在
        types = [t.type for t in tokens]
        assert TokenType.WORD in types
        assert TokenType.LONG_OPTION in types
        assert TokenType.SHORT_OPTION in types
        assert TokenType.SEPARATOR in types
        assert TokenType.QUOTED_STRING in types
    
    def test_whitespace_handling(self):
        """测试空白字符处理"""
        tokenizer = StringTokenizer("  hello   world  \t  test  ")
        tokens = tokenizer.tokenize()
        
        word_tokens = [t for t in tokens if t.type == TokenType.WORD]
        
        assert len(word_tokens) == 3
        assert word_tokens[0].value == "hello"
        assert word_tokens[1].value == "world"
        assert word_tokens[2].value == "test"
    
    def test_empty_string_tokenization(self):
        """测试空字符串分词"""
        tokenizer = StringTokenizer("")
        tokens = tokenizer.tokenize()
        
        # 应该只有EOF token
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF
    
    def test_whitespace_only_tokenization(self):
        """测试只有空白字符的分词"""
        tokenizer = StringTokenizer("   \t  \n  ")
        tokens = tokenizer.tokenize()
        
        # 应该只有EOF token
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF


class TestStringTokenizerErrors:
    """字符串分词器错误处理测试"""
    
    def test_unmatched_quote_error(self):
        """测试未匹配引号错误"""
        tokenizer = StringTokenizer('"unmatched quote')
        
        with pytest.raises(QuoteMismatchError) as exc_info:
            tokenizer.tokenize()
        
        assert exc_info.value.quote_char == '"'
        assert exc_info.value.position == 0
    
    def test_invalid_escape_sequence_error(self):
        """测试无效转义序列错误"""
        tokenizer = StringTokenizer(r'"invalid \z escape"')
        
        with pytest.raises(InvalidEscapeSequenceError) as exc_info:
            tokenizer.tokenize()
        
        assert exc_info.value.sequence == "z"
    
    def test_escape_at_end_error(self):
        """测试字符串末尾转义错误"""
        tokenizer = StringTokenizer('"escape at end\\')
        
        with pytest.raises(InvalidEscapeSequenceError) as exc_info:
            tokenizer.tokenize()
        
        assert exc_info.value.sequence == "EOF"
    
    def test_empty_short_option_error(self):
        """测试空短选项错误"""
        tokenizer = StringTokenizer("- hello")
        
        with pytest.raises(Exception):  # 根据实际实现调整异常类型
            tokenizer.tokenize()
    
    def test_empty_long_option_error(self):
        """测试空长选项错误"""
        tokenizer = StringTokenizer("-- hello")
        
        with pytest.raises(Exception):  # 根据实际实现调整异常类型
            tokenizer.tokenize()


class TestAdvancedCommandParser:
    """高级命令解析器测试"""
    
    def test_parser_creation(self):
        """测试解析器创建"""
        parser = AdvancedCommandParser()
        assert parser is not None
    
    def test_parse_simple_tokens(self):
        """测试解析简单token"""
        parser = AdvancedCommandParser()
        tokens = [
            Token(TokenType.WORD, "hello", 0),
            Token(TokenType.WORD, "world", 6),
            Token(TokenType.EOF, "", 11)
        ]
        
        result = parser.parse(tokens)
        
        assert isinstance(result, ParsedCommand)
        assert len(result.options) == 0
        assert len(result.named_params) == 0
        assert len(result.elements) == 2
        assert result.elements[0].content == "hello"
        assert result.elements[1].content == "world"
    
    def test_parse_options(self):
        """测试解析选项"""
        parser = AdvancedCommandParser()
        tokens = [
            Token(TokenType.SHORT_OPTION, "v", 0),
            Token(TokenType.LONG_OPTION, "verbose", 3),
            Token(TokenType.SHORT_OPTION, "xf", 12),  # 组合选项
            Token(TokenType.EOF, "", 15)
        ]
        
        result = parser.parse(tokens)
        
        assert "v" in result.options
        assert "verbose" in result.options
        assert "x" in result.options
        assert "f" in result.options
        assert all(value is True for value in result.options.values())
    
    def test_parse_named_parameters(self):
        """测试解析命名参数"""
        parser = AdvancedCommandParser()
        tokens = [
            Token(TokenType.SHORT_OPTION, "p", 0),
            Token(TokenType.SEPARATOR, "=", 2),
            Token(TokenType.WORD, "1234", 3),
            Token(TokenType.LONG_OPTION, "env", 8),
            Token(TokenType.SEPARATOR, "=", 11),
            Token(TokenType.QUOTED_STRING, "production", 12),
            Token(TokenType.EOF, "", 24)
        ]
        
        result = parser.parse(tokens)
        
        assert "p" in result.named_params
        assert result.named_params["p"] == "1234"
        assert "env" in result.named_params
        assert result.named_params["env"] == "production"
    
    def test_parse_mixed_content(self):
        """测试解析混合内容"""
        parser = AdvancedCommandParser()
        tokens = [
            Token(TokenType.WORD, "deploy", 0),
            Token(TokenType.WORD, "app", 7),
            Token(TokenType.SHORT_OPTION, "v", 11),
            Token(TokenType.LONG_OPTION, "env", 14),
            Token(TokenType.SEPARATOR, "=", 17),
            Token(TokenType.WORD, "prod", 18),
            Token(TokenType.QUOTED_STRING, "config file", 23),
            Token(TokenType.EOF, "", 36)
        ]
        
        result = parser.parse(tokens)
        
        # 验证选项
        assert "v" in result.options
        assert result.options["v"] is True
        
        # 验证命名参数
        assert "env" in result.named_params
        assert result.named_params["env"] == "prod"
        
        # 验证元素
        assert len(result.elements) == 3  # deploy, app, "config file"
        assert result.elements[0].content == "deploy"
        assert result.elements[1].content == "app"
        assert result.elements[2].content == "config file"
    
    def test_parse_empty_tokens(self):
        """测试解析空token列表"""
        parser = AdvancedCommandParser()
        tokens = [Token(TokenType.EOF, "", 0)]
        
        result = parser.parse(tokens)
        
        assert len(result.options) == 0
        assert len(result.named_params) == 0
        assert len(result.elements) == 0
    
    def test_parse_assignment_detection(self):
        """测试赋值检测"""
        parser = AdvancedCommandParser()
        
        # 有赋值的情况
        tokens_with_assignment = [
            Token(TokenType.SHORT_OPTION, "p", 0),
            Token(TokenType.SEPARATOR, "=", 1),
            Token(TokenType.WORD, "value", 2),
            Token(TokenType.EOF, "", 7)
        ]
        
        result = parser.parse(tokens_with_assignment)
        assert "p" in result.named_params
        assert result.named_params["p"] == "value"
        
        # 无赋值的情况
        tokens_without_assignment = [
            Token(TokenType.SHORT_OPTION, "v", 0),
            Token(TokenType.WORD, "separate", 2),
            Token(TokenType.EOF, "", 10)
        ]
        
        result = parser.parse(tokens_without_assignment)
        assert "v" in result.options
        assert result.options["v"] is True
        assert len(result.elements) == 1
        assert result.elements[0].content == "separate"


class TestElement:
    """Element类测试"""
    
    def test_element_creation(self):
        """测试Element创建"""
        element = Element("text", "hello", 0)
        assert element.type == "text"
        assert element.content == "hello"
        assert element.position == 0
    
    def test_element_str_representation(self):
        """测试Element字符串表示"""
        element = Element("image", "http://example.com/img.jpg", 5)
        str_repr = str(element)
        assert "image" in str_repr
        assert "http://example.com/img.jpg" in str_repr
        assert "pos=5" in str_repr


class TestParsedCommand:
    """ParsedCommand类测试"""
    
    def test_parsed_command_creation(self):
        """测试ParsedCommand创建"""
        options = {"v": True, "verbose": True}
        named_params = {"env": "prod", "port": "8080"}
        elements = [Element("text", "deploy", 0), Element("text", "app", 7)]
        raw_tokens = []
        
        parsed = ParsedCommand(options, named_params, elements, raw_tokens)
        
        assert parsed.options == options
        assert parsed.named_params == named_params
        assert parsed.elements == elements
        assert parsed.raw_tokens == raw_tokens
    
    def test_get_text_params(self):
        """测试获取文本参数"""
        # 模拟混合参数类型
        mock_segment = Mock()
        mock_segment.msg_seg_type = "image"
        
        named_params = {
            "text_param": "hello",
            "number_param": "123",
            "segment_param": mock_segment
        }
        
        parsed = ParsedCommand({}, named_params, [], [])
        text_params = parsed.get_text_params()
        
        assert "text_param" in text_params
        assert "number_param" in text_params
        assert "segment_param" not in text_params
    
    def test_get_segment_params(self):
        """测试获取消息段参数"""
        # 模拟消息段
        mock_segment = Mock()
        mock_segment.msg_seg_type = "image"
        
        named_params = {
            "text_param": "hello",
            "segment_param": mock_segment
        }
        
        parsed = ParsedCommand({}, named_params, [], [])
        segment_params = parsed.get_segment_params()
        
        assert "segment_param" in segment_params
        assert "text_param" not in segment_params
    
    def test_parsed_command_str_representation(self):
        """测试ParsedCommand字符串表示"""
        options = {"v": True}
        named_params = {"env": "test"}
        elements = [Element("text", "test", 0)]
        
        parsed = ParsedCommand(options, named_params, elements, [])
        str_repr = str(parsed)
        
        assert "ParsedCommand" in str_repr
        assert "options" in str_repr
        assert "named_params" in str_repr
        assert "elements" in str_repr


class TestTokenizerIntegration:
    """分词器集成测试"""
    
    def test_tokenizer_parser_integration(self):
        """测试分词器和解析器集成"""
        # 完整的命令行
        command_line = 'deploy myapp --env=production -v --force "config.json"'
        
        # 分词
        tokenizer = StringTokenizer(command_line)
        tokens = tokenizer.tokenize()
        
        # 解析
        parser = AdvancedCommandParser()
        result = parser.parse(tokens)
        
        # 验证结果
        assert len(result.elements) >= 3  # deploy, myapp, config.json
        assert result.options["v"] is True
        assert result.options["force"] is True
        assert result.named_params["env"] == "production"
    
    def test_complex_command_parsing(self):
        """测试复杂命令解析"""
        command_line = r'process "file with spaces.txt" --mode=batch -xvf --timeout=30 "output dir"'
        
        tokenizer = StringTokenizer(command_line)
        tokens = tokenizer.tokenize()
        
        parser = AdvancedCommandParser()
        result = parser.parse(tokens)
        
        # 验证复杂结果
        assert "x" in result.options
        assert "v" in result.options
        assert "f" in result.options
        assert result.named_params["mode"] == "batch"
        assert result.named_params["timeout"] == "30"
        
        # 验证带空格的文件名
        file_elements = [e for e in result.elements if "spaces" in str(e.content)]
        assert len(file_elements) > 0
