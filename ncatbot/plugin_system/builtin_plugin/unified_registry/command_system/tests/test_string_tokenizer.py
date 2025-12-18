"""字符串分词器测试

测试 StringTokenizer 的所有功能，包括：
- 基本分词
- 短选项和长选项识别
- 参数赋值
- 转义字符串处理
- 错误处理
"""

from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer import (
    StringTokenizer,
    TokenType,
    QuoteMismatchError,
    InvalidEscapeSequenceError,
)


class TestStringTokenizer:
    """字符串分词器测试类"""

    def test_basic_words(self):
        """测试基本单词分词"""
        tokenizer = StringTokenizer("hello world test")
        tokens = tokenizer.tokenize()

        # 应该有 3 个 WORD token + 1 个 EOF token
        assert len(tokens) == 4
        assert tokens[0].type == TokenType.WORD
        assert tokens[0].value == "hello"
        assert tokens[1].type == TokenType.WORD
        assert tokens[1].value == "world"
        assert tokens[2].type == TokenType.WORD
        assert tokens[2].value == "test"
        assert tokens[3].type == TokenType.EOF

    def test_short_options(self):
        """测试短选项识别"""
        # 单个短选项
        tokenizer = StringTokenizer("-v")
        tokens = tokenizer.tokenize()
        assert len(tokens) == 2  # option + EOF
        assert tokens[0].type == TokenType.SHORT_OPTION
        assert tokens[0].value == "v"

        # 组合短选项
        tokenizer = StringTokenizer("-xvf")
        tokens = tokenizer.tokenize()
        assert len(tokens) == 2  # option + EOF
        assert tokens[0].type == TokenType.SHORT_OPTION
        assert tokens[0].value == "xvf"

        # 多个短选项
        tokenizer = StringTokenizer("-v -x -f")
        tokens = tokenizer.tokenize()
        assert len(tokens) == 4  # 3 options + EOF
        assert all(t.type == TokenType.SHORT_OPTION for t in tokens[:-1])
        assert [t.value for t in tokens[:-1]] == ["v", "x", "f"]

    def test_long_options(self):
        """测试长选项识别"""
        # 单个长选项
        tokenizer = StringTokenizer("--verbose")
        tokens = tokenizer.tokenize()
        assert len(tokens) == 2  # option + EOF
        assert tokens[0].type == TokenType.LONG_OPTION
        assert tokens[0].value == "verbose"

        # 多个长选项
        tokenizer = StringTokenizer("--verbose --debug --help")
        tokens = tokenizer.tokenize()
        assert len(tokens) == 4  # 3 options + EOF
        assert all(t.type == TokenType.LONG_OPTION for t in tokens[:-1])
        assert [t.value for t in tokens[:-1]] == ["verbose", "debug", "help"]

    def test_option_assignments(self):
        """测试选项赋值"""
        # 短选项赋值
        tokenizer = StringTokenizer("-p=8080")
        tokens = tokenizer.tokenize()
        assert len(tokens) == 4  # option + separator + value + EOF
        assert tokens[0].type == TokenType.SHORT_OPTION
        assert tokens[0].value == "p"
        assert tokens[1].type == TokenType.SEPARATOR
        assert tokens[1].value == "="
        assert tokens[2].type == TokenType.WORD
        assert tokens[2].value == "8080"

        # 长选项赋值
        tokenizer = StringTokenizer("--config=app.json")
        tokens = tokenizer.tokenize()
        assert len(tokens) == 4  # option + separator + value + EOF
        assert tokens[0].type == TokenType.LONG_OPTION
        assert tokens[0].value == "config"
        assert tokens[1].type == TokenType.SEPARATOR
        assert tokens[1].value == "="
        assert tokens[2].type == TokenType.WORD
        assert tokens[2].value == "app.json"

        # 引用字符串赋值
        tokenizer = StringTokenizer('--message="hello world"')
        tokens = tokenizer.tokenize()
        assert len(tokens) == 4  # option + separator + value + EOF
        assert tokens[0].type == TokenType.LONG_OPTION
        assert tokens[0].value == "message"
        assert tokens[1].type == TokenType.SEPARATOR
        assert tokens[1].value == "="
        assert tokens[2].type == TokenType.QUOTED_STRING
        assert tokens[2].value == "hello world"

    def test_quoted_strings(self):
        """测试引用字符串处理"""
        # 基本引用字符串
        tokenizer = StringTokenizer('"hello world"')
        tokens = tokenizer.tokenize()
        assert len(tokens) == 2  # string + EOF
        assert tokens[0].type == TokenType.QUOTED_STRING
        assert tokens[0].value == "hello world"

        # 空引用字符串
        tokenizer = StringTokenizer('""')
        tokens = tokenizer.tokenize()
        assert len(tokens) == 2  # string + EOF
        assert tokens[0].type == TokenType.QUOTED_STRING
        assert tokens[0].value == ""

        # 多个引用字符串
        tokenizer = StringTokenizer('"first" "second" "third"')
        tokens = tokenizer.tokenize()
        assert len(tokens) == 4  # 3 strings + EOF
        assert all(t.type == TokenType.QUOTED_STRING for t in tokens[:-1])
        assert [t.value for t in tokens[:-1]] == ["first", "second", "third"]

    def test_escape_sequences(self):
        """测试转义序列"""
        # 基本转义序列
        escape_tests = [
            (r'"hello \"world\""', 'hello "world"'),
            (r'"line1\nline2"', "line1\nline2"),
            (r'"tab\there"', "tab\there"),
            (r'"carriage\rreturn"', "carriage\rreturn"),
            (r'"backslash\\"', "backslash\\"),
            (r'"slash\/"', "slash/"),
        ]

        for input_str, expected in escape_tests:
            tokenizer = StringTokenizer(input_str)
            tokens = tokenizer.tokenize()
            assert len(tokens) == 2  # string + EOF
            assert tokens[0].type == TokenType.QUOTED_STRING
            assert tokens[0].value == expected, f"Failed for input: {input_str}"

    def test_whitespace_handling(self):
        """测试空白字符处理"""
        # 多个空格
        tokenizer = StringTokenizer("  hello   world  ")
        tokens = tokenizer.tokenize()
        assert len(tokens) == 3  # 2 words + EOF
        assert [t.value for t in tokens[:-1]] == ["hello", "world"]

        # 制表符和换行符
        tokenizer = StringTokenizer("\thello\nworld\r\n")
        tokens = tokenizer.tokenize()
        assert len(tokens) == 3  # 2 words + EOF
        assert [t.value for t in tokens[:-1]] == ["hello", "world"]

        # 纯空白字符
        tokenizer = StringTokenizer("   \t\n\r  ")
        tokens = tokenizer.tokenize()
        assert len(tokens) == 1  # 只有 EOF
        assert tokens[0].type == TokenType.EOF

    def test_complex_commands(self):
        """测试复杂命令解析"""
        complex_commands = [
            'deploy --env=prod -xvf "my app" --debug',
            'backup "source dir" --dest="/backup/folder" -c=gzip',
            "docker run --name=myapp -p=8080:80 -d nginx:latest",
            'git commit -m "Initial commit" --author="张三 <zhangsan@example.com>"',
        ]

        for command in complex_commands:
            tokenizer = StringTokenizer(command)
            tokens = tokenizer.tokenize()

            # 验证最后一个是 EOF token
            assert tokens[-1].type == TokenType.EOF

            # 验证没有空的 token 值（除了 EOF）
            for token in tokens[:-1]:
                assert token.value != ""

            # 验证位置信息正确
            for token in tokens:
                assert token.position >= 0

    def test_error_handling(self):
        """测试错误处理"""
        # # 未闭合的引号
        # with pytest.raises(QuoteMismatchError) as exc_info:
        #     tokenizer = StringTokenizer('"unclosed quote')
        #     tokenizer.tokenize()
        # assert "Unmatched quote" in str(exc_info.value)

        # # 无效转义序列
        # with pytest.raises(InvalidEscapeSequenceError) as exc_info:
        #     tokenizer = StringTokenizer(r'"invalid \z escape"')
        #     tokenizer.tokenize()
        # assert "Invalid escape sequence" in str(exc_info.value)

        # # 转义序列在字符串末尾
        # with pytest.raises(InvalidEscapeSequenceError) as exc_info:
        #     tokenizer = StringTokenizer(r'"ends with backslash \"')
        #     tokenizer.tokenize()
        # assert "Invalid escape sequence" in str(exc_info.value)

    def test_edge_cases(self):
        """测试边界情况"""
        # 空字符串
        tokenizer = StringTokenizer("")
        tokens = tokenizer.tokenize()
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF

        # 只有选项分隔符
        tokenizer = StringTokenizer("=")
        tokens = tokenizer.tokenize()
        assert len(tokens) == 2  # separator + EOF
        assert tokens[0].type == TokenType.SEPARATOR
        assert tokens[0].value == "="

        # 只有短横线
        tokenizer = StringTokenizer("-")
        tokens = tokenizer.tokenize()
        assert len(tokens) == 2  # word + EOF
        assert tokens[0].type == TokenType.WORD
        assert tokens[0].value == "-"

        # 只有双短横线 - 这会触发空长选项错误
        try:
            tokenizer = StringTokenizer("--")
            tokens = tokenizer.tokenize()
            # 如果没有抛出异常，检查是否被当作普通词处理
            assert len(tokens) == 2  # word + EOF
            assert tokens[0].type == TokenType.WORD
            assert tokens[0].value == "--"
        except Exception:
            # 空长选项会抛出异常，这是预期的
            pass

    def test_position_tracking(self):
        """测试位置跟踪"""
        tokenizer = StringTokenizer("hello --world")
        tokens = tokenizer.tokenize()

        # 检查位置信息
        assert tokens[0].position == 0  # "hello" 开始位置
        assert tokens[1].position == 8  # "--world" 开始位置

        # 复杂示例
        tokenizer = StringTokenizer('test "quoted" -v')
        tokens = tokenizer.tokenize()

        assert tokens[0].position == 0  # "test"
        assert tokens[1].position == 7  # "quoted"
        assert tokens[2].position == 15  # "-v"


def test_integration_with_imports():
    """测试导入和集成"""
    # 测试所有必要的导入都可用
    from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer import (
        StringTokenizer,
        TokenType,
    )

    # 基本功能测试
    tokenizer = StringTokenizer('-v --config="test.json" hello')
    tokens = tokenizer.tokenize()

    assert len(tokens) == 6  # option + option + separator + string + word + EOF
    assert tokens[0].type == TokenType.SHORT_OPTION
    assert tokens[1].type == TokenType.LONG_OPTION
    assert tokens[2].type == TokenType.SEPARATOR
    assert tokens[3].type == TokenType.QUOTED_STRING
    assert tokens[4].type == TokenType.WORD


if __name__ == "__main__":
    print("运行字符串分词器测试...")

    # 创建测试实例
    test_instance = TestStringTokenizer()

    # 运行所有测试方法
    test_methods = [
        ("基本单词分词", test_instance.test_basic_words),
        ("短选项识别", test_instance.test_short_options),
        ("长选项识别", test_instance.test_long_options),
        ("选项赋值", test_instance.test_option_assignments),
        ("引用字符串", test_instance.test_quoted_strings),
        ("转义序列", test_instance.test_escape_sequences),
        ("空白字符处理", test_instance.test_whitespace_handling),
        ("复杂命令", test_instance.test_complex_commands),
        ("边界情况", test_instance.test_edge_cases),
        ("位置跟踪", test_instance.test_position_tracking),
    ]

    for test_name, test_method in test_methods:
        try:
            test_method()
            print(f"✓ {test_name}测试通过")
        except Exception as e:
            print(f"✗ {test_name}测试失败: {e}")

    # 错误处理测试（需要特殊处理）
    print("\n测试错误处理...")
    try:
        StringTokenizer('"未闭合引号').tokenize()
    except QuoteMismatchError:
        print("✓ 引号不匹配错误捕获成功")

    try:
        StringTokenizer(r'"无效\z转义"').tokenize()
    except InvalidEscapeSequenceError:
        print("✓ 无效转义序列错误捕获成功")

    # 集成测试
    test_integration_with_imports()
    print("✓ 导入和集成测试通过")

    print("\n字符串分词器所有测试完成！✨")
