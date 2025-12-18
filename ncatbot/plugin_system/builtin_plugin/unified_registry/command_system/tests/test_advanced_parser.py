"""高级命令解析器测试

测试 AdvancedCommandParser 的功能，包括：
- 选项解析（布尔状态）
- 命名参数解析（键值对）
- Element 解析（未解析内容）
- 位置保持
- 与 StringTokenizer 的组合使用
"""

from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer import (
    StringTokenizer,
    AdvancedCommandParser,
    Token,
    TokenType,
)


class TestAdvancedCommandParser:
    """高级命令解析器测试类"""

    def test_options_parsing(self):
        """测试选项解析"""
        parser = AdvancedCommandParser()

        # 短选项
        tokenizer = StringTokenizer("-v")
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        assert result.options == {"v": True}
        assert result.named_params == {}
        assert result.elements == []

        # 组合短选项
        tokenizer = StringTokenizer("-xvf")
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        assert result.options == {"x": True, "v": True, "f": True}
        assert result.named_params == {}
        assert result.elements == []

        # 长选项
        tokenizer = StringTokenizer("--verbose --debug")
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        assert result.options == {"verbose": True, "debug": True}
        assert result.named_params == {}
        assert result.elements == []

        # 混合选项
        tokenizer = StringTokenizer("-v --debug -xf --help")
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        expected_options = {
            "v": True,
            "debug": True,
            "x": True,
            "f": True,
            "help": True,
        }
        assert result.options == expected_options
        assert result.named_params == {}
        assert result.elements == []

    def test_named_params_parsing(self):
        """测试命名参数解析"""
        parser = AdvancedCommandParser()

        # 短选项赋值
        tokenizer = StringTokenizer("-p=8080")
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        assert result.options == {}
        assert result.named_params == {"p": "8080"}
        assert result.elements == []

        # 长选项赋值
        tokenizer = StringTokenizer("--port=8080 --host=localhost")
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        assert result.options == {}
        assert result.named_params == {"port": "8080", "host": "localhost"}
        assert result.elements == []

        # 引用字符串赋值
        tokenizer = StringTokenizer('--message="hello world" -c="gzip"')
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        assert result.options == {}
        assert result.named_params == {"message": "hello world", "c": "gzip"}
        assert result.elements == []

        # 复杂值
        tokenizer = StringTokenizer(
            '--env="NODE_ENV=production" --config="/path/to/config.json"'
        )
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        expected_params = {
            "env": "NODE_ENV=production",
            "config": "/path/to/config.json",
        }
        assert result.named_params == expected_params

    def test_elements_parsing(self):
        """测试 Element 解析"""
        parser = AdvancedCommandParser()

        # 基本元素
        tokenizer = StringTokenizer('backup "my files" document.txt')
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        assert result.options == {}
        assert result.named_params == {}
        assert len(result.elements) == 3

        # 检查元素内容和位置
        assert result.elements[0].type == "text"
        assert result.elements[0].content == "backup"
        assert result.elements[0].position == 0

        assert result.elements[1].type == "text"
        assert result.elements[1].content == "my files"
        assert result.elements[1].position == 1

        assert result.elements[2].type == "text"
        assert result.elements[2].content == "document.txt"
        assert result.elements[2].position == 2

        # 只有引用字符串
        tokenizer = StringTokenizer('"first string" "second string"')
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        assert len(result.elements) == 2
        assert result.elements[0].content == "first string"
        assert result.elements[1].content == "second string"

        # 混合元素类型
        tokenizer = StringTokenizer('command "quoted arg" normal_arg')
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        assert len(result.elements) == 3
        contents = [e.content for e in result.elements]
        assert contents == ["command", "quoted arg", "normal_arg"]

    def test_mixed_parsing(self):
        """测试混合解析"""
        parser = AdvancedCommandParser()

        # 完整的复杂命令
        command = 'backup "my files" --dest=/backup -xvf --compress=gzip document.txt --verbose'
        tokenizer = StringTokenizer(command)
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        # 检查选项
        expected_options = {"x": True, "v": True, "f": True, "verbose": True}
        assert result.options == expected_options

        # 检查命名参数
        expected_named_params = {"dest": "/backup", "compress": "gzip"}
        assert result.named_params == expected_named_params

        # 检查元素
        assert len(result.elements) == 3
        contents = [e.content for e in result.elements]
        assert contents == ["backup", "my files", "document.txt"]

        # 检查位置
        for i, element in enumerate(result.elements):
            assert element.position == i

    def test_position_preservation(self):
        """测试位置保持"""
        parser = AdvancedCommandParser()

        # 验证元素位置按原始顺序
        command = "cmd1 --opt1 arg2 -p=val arg3 --flag arg4"
        tokenizer = StringTokenizer(command)
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        # 元素应该按原始顺序
        expected_contents = ["cmd1", "arg2", "arg3", "arg4"]
        actual_contents = [e.content for e in result.elements]
        assert actual_contents == expected_contents

        # 位置应该是连续的
        for i, element in enumerate(result.elements):
            assert element.position == i

        # 选项和参数
        assert result.options == {"opt1": True, "flag": True}
        assert result.named_params == {"p": "val"}

    def test_complex_scenarios(self):
        """测试复杂场景"""
        parser = AdvancedCommandParser()

        scenarios = [
            # Docker 风格命令
            {
                "command": 'docker run --name=myapp -p=8080:80 -d "nginx:latest" --env="NODE_ENV=prod"',
                "expected_options": {"d": True},
                "expected_params": {
                    "name": "myapp",
                    "p": "8080:80",
                    "env": "NODE_ENV=prod",
                },
                "expected_elements": ["docker", "run", "nginx:latest"],
            },
            # Git 风格命令 - 简化测试，避免特殊字符问题
            {
                "command": 'git commit -m="Initial commit" --author="John Doe"',
                "expected_options": {},
                "expected_params": {"m": "Initial commit", "author": "John Doe"},
                "expected_elements": ["git", "commit"],
            },
            # 备份命令
            {
                "command": 'backup --source="/data/important" --dest="/backup" --compress --verbose',
                "expected_options": {"compress": True, "verbose": True},
                "expected_params": {"source": "/data/important", "dest": "/backup"},
                "expected_elements": ["backup"],
            },
        ]

        for scenario in scenarios:
            tokenizer = StringTokenizer(scenario["command"])
            tokens = tokenizer.tokenize()
            result = parser.parse(tokens)

            assert result.options == scenario["expected_options"], (
                f"Options failed for: {scenario['command']}"
            )
            assert result.named_params == scenario["expected_params"], (
                f"Params failed for: {scenario['command']}"
            )

            actual_contents = [e.content for e in result.elements]
            assert actual_contents == scenario["expected_elements"], (
                f"Elements failed for: {scenario['command']}"
            )

    def test_edge_cases(self):
        """测试边界情况"""
        parser = AdvancedCommandParser()

        # 空命令
        tokenizer = StringTokenizer("")
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        assert result.options == {}
        assert result.named_params == {}
        assert result.elements == []

        # 只有空白字符
        tokenizer = StringTokenizer("   ")
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        assert result.options == {}
        assert result.named_params == {}
        assert result.elements == []

        # 选项后没有值（应该被当作选项）
        tokenizer = StringTokenizer("--config=")
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        # 因为没有有效的值 token，应该被当作普通选项
        assert result.options == {"config": True}
        assert result.named_params == {}

        # 只有分隔符
        tokenizer = StringTokenizer("=")
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        assert result.options == {}
        assert result.named_params == {}
        assert result.elements == []  # 分隔符被跳过

    def test_raw_tokens_preservation(self):
        """测试原始 Token 保存"""
        parser = AdvancedCommandParser()

        command = "-v --debug=true hello world"
        tokenizer = StringTokenizer(command)
        tokens = tokenizer.tokenize()
        result = parser.parse(tokens)

        # 原始 tokens 应该被保存
        assert result.raw_tokens == tokens
        assert len(result.raw_tokens) == len(tokens)

        # 验证原始 tokens 完整性
        assert any(t.type == TokenType.SHORT_OPTION for t in result.raw_tokens)
        assert any(t.type == TokenType.LONG_OPTION for t in result.raw_tokens)
        assert any(t.type == TokenType.WORD for t in result.raw_tokens)

    def test_error_resilience(self):
        """测试错误恢复能力"""
        parser = AdvancedCommandParser()

        # 处理无效的 token 序列
        # 创建一个手动构造的 token 列表
        tokens = [
            Token(TokenType.SHORT_OPTION, "v", 0),
            Token(TokenType.SEPARATOR, "=", 2),
            # 缺少值 token，直接跳到下一个
            Token(TokenType.WORD, "hello", 3),
            Token(TokenType.EOF, "", 8),
        ]

        result = parser.parse(tokens)

        # 应该优雅处理，将选项当作纯选项，因为分隔符后没有有效的值token
        assert result.options == {"v": True}
        assert result.named_params == {}
        assert len(result.elements) == 1
        assert result.elements[0].content == "hello"


def test_integration_with_string_tokenizer():
    """测试与字符串分词器的集成"""
    # 完整的集成测试
    integration_cases = [
        {
            "input": "help",
            "expected_options": {},
            "expected_params": {},
            "expected_elements": ["help"],
        },
        {
            "input": "search python --type=article -v",
            "expected_options": {"v": True},
            "expected_params": {"type": "article"},
            "expected_elements": ["search", "python"],
        },
        {
            "input": 'backup "my files" --dest="/backup" --compress',
            "expected_options": {"compress": True},
            "expected_params": {"dest": "/backup"},
            "expected_elements": ["backup", "my files"],
        },
        {
            "input": "-xvf --config=app.json process data.txt",
            "expected_options": {"x": True, "v": True, "f": True},
            "expected_params": {"config": "app.json"},
            "expected_elements": ["process", "data.txt"],
        },
    ]

    parser = AdvancedCommandParser()

    for case in integration_cases:
        # 使用 StringTokenizer 进行分词
        tokenizer = StringTokenizer(case["input"])
        tokens = tokenizer.tokenize()

        # 使用 AdvancedCommandParser 进行解析
        result = parser.parse(tokens)

        # 验证结果
        assert result.options == case["expected_options"], (
            f"Options mismatch for: {case['input']}"
        )
        assert result.named_params == case["expected_params"], (
            f"Params mismatch for: {case['input']}"
        )

        actual_elements = [e.content for e in result.elements]
        assert actual_elements == case["expected_elements"], (
            f"Elements mismatch for: {case['input']}"
        )


if __name__ == "__main__":
    print("运行高级命令解析器测试...")

    # 创建测试实例
    test_instance = TestAdvancedCommandParser()

    # 运行所有测试方法
    test_methods = [
        ("选项解析", test_instance.test_options_parsing),
        ("命名参数解析", test_instance.test_named_params_parsing),
        ("Element 解析", test_instance.test_elements_parsing),
        ("混合解析", test_instance.test_mixed_parsing),
        ("位置保持", test_instance.test_position_preservation),
        ("复杂场景", test_instance.test_complex_scenarios),
        ("边界情况", test_instance.test_edge_cases),
        ("原始 Token 保存", test_instance.test_raw_tokens_preservation),
        ("错误恢复", test_instance.test_error_resilience),
    ]

    for test_name, test_method in test_methods:
        try:
            test_method()
            print(f"✓ {test_name}测试通过")
        except Exception as e:
            print(f"✗ {test_name}测试失败: {e}")

    # 集成测试
    try:
        test_integration_with_string_tokenizer()
        print("✓ 与字符串分词器集成测试通过")
    except Exception as e:
        print(f"✗ 集成测试失败: {e}")

    print("\n高级命令解析器所有测试完成！✨")

    # 演示用法
    print("\n演示完整用法:")
    command = 'backup "important files" --dest=/backup -xvf --compress=gzip --verbose'
    tokenizer = StringTokenizer(command)
    tokens = tokenizer.tokenize()
    parser = AdvancedCommandParser()
    result = parser.parse(tokens)

    print(f"输入: {command}")
    print(f"选项: {result.options}")
    print(f"命名参数: {result.named_params}")
    print(f"元素: {[e.content for e in result.elements]}")
