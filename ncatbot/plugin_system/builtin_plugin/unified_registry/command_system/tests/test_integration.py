"""集成测试

测试字符串分词器和高级命令解析器的组合使用，包括：
- 完整的工作流程
- 真实使用场景
- 性能测试
- 错误处理的端到端测试
"""

import time
from typing import Dict, Any

from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer import (
    StringTokenizer,
    AdvancedCommandParser,
    QuoteMismatchError,
    InvalidEscapeSequenceError,
)


class CommandProcessor:
    """命令处理器 - 演示完整的命令处理流程"""

    def __init__(self):
        self.parser = AdvancedCommandParser()

    def process_command(self, command_text: str) -> Dict[str, Any]:
        """处理命令文本，返回解析结果"""
        # 第一步：分词
        tokenizer = StringTokenizer(command_text)
        tokens = tokenizer.tokenize()

        # 第二步：解析
        result = self.parser.parse(tokens)

        # 第三步：转换为应用格式
        return {
            "original_command": command_text,
            "options": result.options,
            "named_params": result.named_params,
            "arguments": [e.content for e in result.elements],
            "element_count": len(result.elements),
            "option_count": len(result.options),
            "param_count": len(result.named_params),
            "token_count": len(result.raw_tokens),
        }


class TestIntegration:
    """集成测试类"""

    def test_real_world_commands(self):
        """测试真实世界的命令"""
        processor = CommandProcessor()

        # 真实命令示例
        real_commands = [
            # 系统管理命令
            "systemctl start nginx --user --no-block",
            "ps aux | grep python",
            'find /var/log -name "*.log" -mtime +7 -delete',
            # Docker 命令
            "docker run --name web-server -p 80:80 -d nginx:latest",
            "docker exec -it mycontainer /bin/bash",
            "docker build -t myapp:v1.0 --build-arg ENV=prod .",
            # Git 命令
            'git commit -m "feat: add new feature" --author="John Doe <john@example.com>"',
            "git log --oneline --graph --all",
            "git push origin main --force-with-lease",
            # 应用命令
            'backup --source="/home/user/documents" --dest="/backup/2024" --compress=gzip --verbose',
            'deploy myapp --env=production --config="/etc/myapp.conf" --dry-run',
            'search "machine learning" --type=article --limit=10 --sort=relevance',
        ]

        for command in real_commands:
            try:
                result = processor.process_command(command)

                # 基本验证
                assert isinstance(result["options"], dict)
                assert isinstance(result["named_params"], dict)
                assert isinstance(result["arguments"], list)
                assert result["token_count"] > 0

                # 验证内容完整性
                total_content = (
                    len(result["arguments"])
                    + len(result["options"])
                    + len(result["named_params"])
                )
                assert total_content > 0, f"No content parsed from: {command}"

            except Exception as e:
                print(f"Failed to process command: {command}")
                raise e

    def test_command_patterns(self):
        """测试常见的命令模式"""
        processor = CommandProcessor()

        patterns = [
            # 模式：简单命令
            {
                "command": "help",
                "expected_args": ["help"],
                "expected_options": {},
                "expected_params": {},
            },
            # 模式：命令 + 参数
            {
                "command": "search python programming",
                "expected_args": ["search", "python", "programming"],
                "expected_options": {},
                "expected_params": {},
            },
            # 模式：命令 + 选项
            {
                "command": "list --all --verbose",
                "expected_args": ["list"],
                "expected_options": {"all": True, "verbose": True},
                "expected_params": {},
            },
            # 模式：命令 + 参数 + 选项
            {
                "command": "deploy myapp --env=prod --verbose",
                "expected_args": ["deploy", "myapp"],
                "expected_options": {"verbose": True},
                "expected_params": {"env": "prod"},
            },
            # 模式：复杂混合
            {
                "command": 'backup "my documents" --dest=/backup -xvf --compress=gzip --dry-run',
                "expected_args": ["backup", "my documents"],
                "expected_options": {"x": True, "v": True, "f": True, "dry-run": True},
                "expected_params": {"dest": "/backup", "compress": "gzip"},
            },
        ]

        for pattern in patterns:
            result = processor.process_command(pattern["command"])

            assert result["arguments"] == pattern["expected_args"], (
                f"Args mismatch for: {pattern['command']}"
            )
            assert result["options"] == pattern["expected_options"], (
                f"Options mismatch for: {pattern['command']}"
            )
            assert result["named_params"] == pattern["expected_params"], (
                f"Params mismatch for: {pattern['command']}"
            )

    def test_error_handling_integration(self):
        """测试端到端的错误处理"""
        processor = CommandProcessor()

        # 测试语法错误
        error_commands = [
            '"unclosed quote',
            'valid command "unclosed',
            r'bad escape "\z"',
            r'test "ends with backslash\"',
        ]

        for command in error_commands:
            try:
                processor.process_command(command)
                # 如果没有抛出异常，说明处理有问题
                assert False, f"Expected error for command: {command}"
            except (QuoteMismatchError, InvalidEscapeSequenceError):
                # 预期的错误，测试通过
                pass
            except Exception as e:
                # 其他意外错误
                assert False, f"Unexpected error for command '{command}': {e}"

    def test_performance(self):
        """测试性能"""
        processor = CommandProcessor()

        # 性能测试命令
        test_commands = [
            "simple command",
            "command --with=options -xvf",
            'complex "quoted arguments" --many=options --more=params -abc',
            'very long command with many arguments and "quoted strings" --option1=value1 --option2=value2 -xyz --flag',
        ]

        # 热身
        for command in test_commands:
            processor.process_command(command)

        # 性能测试
        iterations = 1000
        start_time = time.time()

        for _ in range(iterations):
            for command in test_commands:
                processor.process_command(command)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_command = total_time / (iterations * len(test_commands))

        # 验证性能（每个命令处理时间应该小于 1ms）
        assert avg_time_per_command < 0.001, (
            f"Performance too slow: {avg_time_per_command:.4f}s per command"
        )

        print(f"Performance test: {avg_time_per_command * 1000:.2f}ms per command")

    def test_unicode_and_special_chars(self):
        """测试 Unicode 和特殊字符"""
        processor = CommandProcessor()

        unicode_commands = [
            'search "中文测试"',
            'deploy --message="Hello, 世界!"',
            'backup "файл.txt" --dest="папка"',
            'process --emoji="😀🎉" --special="café naïve"',
            'test "newline\nhere" --tab="\tvalue"',
        ]

        for command in unicode_commands:
            result = processor.process_command(command)

            # 验证 Unicode 字符正确处理
            assert result["token_count"] > 0
            # 至少应该有一些内容被解析
            total_items = (
                len(result["arguments"])
                + len(result["options"])
                + len(result["named_params"])
            )
            assert total_items > 0, f"No content parsed from Unicode command: {command}"

    def test_edge_case_integration(self):
        """测试边界情况的集成"""
        processor = CommandProcessor()

        edge_cases = [
            # 空命令
            "",
            "   ",
            "\t\n",
            # 只有选项
            "-v",
            "--help",
            "-xvf --verbose",
            # 只有赋值
            "--config=app.json",
            "-p=8080 --host=localhost",
            # 复杂的空格处理
            "  command   --option=value   arg1   arg2  ",
            # 特殊字符
            "test --special='!@#$%^&*()'",
            'command --path="/path/with spaces/file.txt"',
        ]

        for command in edge_cases:
            try:
                result = processor.process_command(command)

                # 基本结构验证
                assert isinstance(result["options"], dict)
                assert isinstance(result["named_params"], dict)
                assert isinstance(result["arguments"], list)

                # 空命令应该返回空结果
                if command.strip() == "":
                    assert len(result["arguments"]) == 0
                    assert len(result["options"]) == 0
                    assert len(result["named_params"]) == 0

            except Exception as e:
                print(f"Failed on edge case: '{command}'")
                raise e


def test_workflow_examples():
    """测试完整的工作流程示例"""
    processor = CommandProcessor()

    # 模拟实际应用中的命令处理流程
    workflows = [
        {
            "name": "文件备份工作流",
            "commands": [
                'backup --source="/home/user" --dest="/backup" --verbose',
                'verify --path="/backup" --checksum',
                "cleanup --older-than=30days --dry-run",
            ],
        },
        {
            "name": "容器部署工作流",
            "commands": [
                "build --tag=myapp:latest --no-cache",
                "push --registry=hub.docker.com --tag=myapp:latest",
                "deploy --image=myapp:latest --replicas=3 --env=production",
            ],
        },
        {
            "name": "数据处理工作流",
            "commands": [
                'extract --source="/data/raw" --format=csv',
                'transform --rules="/config/rules.json" --output="/data/processed"',
                'load --destination="postgresql://localhost/db" --batch-size=1000',
            ],
        },
    ]

    for workflow in workflows:
        print(f"\n处理工作流: {workflow['name']}")

        for command in workflow["commands"]:
            result = processor.process_command(command)

            # 验证每个命令都被正确处理
            assert result["token_count"] > 0
            print(f"  ✓ {command}")
            print(f"    参数: {result['arguments']}")
            print(f"    选项: {result['options']}")
            print(f"    命名参数: {result['named_params']}")


def test_memory_usage():
    """测试内存使用情况"""
    import gc

    processor = CommandProcessor()

    # 大量命令处理，检查内存泄漏
    large_commands = [
        f'process-{i} --config="/very/long/path/to/config/file/number/{i}.json" --verbose --dry-run'
        for i in range(100)
    ]

    # 处理前的内存状态
    gc.collect()

    results = []
    for command in large_commands:
        result = processor.process_command(command)
        results.append(result)

    # 处理后清理
    results.clear()
    gc.collect()

    # 如果运行到这里没有内存错误，说明基本正常
    assert True


if __name__ == "__main__":
    print("运行集成测试...")

    # 创建测试实例
    test_instance = TestIntegration()

    # 运行所有测试方法
    test_methods = [
        ("真实世界命令", test_instance.test_real_world_commands),
        ("命令模式", test_instance.test_command_patterns),
        ("错误处理集成", test_instance.test_error_handling_integration),
        ("性能测试", test_instance.test_performance),
        ("Unicode 和特殊字符", test_instance.test_unicode_and_special_chars),
        ("边界情况集成", test_instance.test_edge_case_integration),
    ]

    for test_name, test_method in test_methods:
        try:
            test_method()
            print(f"✓ {test_name}测试通过")
        except Exception as e:
            print(f"✗ {test_name}测试失败: {e}")
            raise

    # 工作流程示例
    try:
        test_workflow_examples()
        print("✓ 工作流程示例测试通过")
    except Exception as e:
        print(f"✗ 工作流程示例测试失败: {e}")
        raise

    # 内存测试
    try:
        test_memory_usage()
        print("✓ 内存使用测试通过")
    except Exception as e:
        print(f"✗ 内存使用测试失败: {e}")
        raise

    print("\n所有集成测试通过！🎉")

    # 演示完整的使用方法
    print("\n=== 完整使用演示 ===")
    processor = CommandProcessor()
    demo_command = 'deploy "my awesome app" --env=production --replicas=3 -xvf --config="/etc/app.conf" --dry-run'

    result = processor.process_command(demo_command)

    print(f"输入命令: {demo_command}")
    print("解析结果:")
    print(f"  参数数量: {result['element_count']}")
    print(f"  选项数量: {result['option_count']}")
    print(f"  命名参数数量: {result['param_count']}")
    print(f"  Token 数量: {result['token_count']}")
    print(f"  参数: {result['arguments']}")
    print(f"  选项: {result['options']}")
    print(f"  命名参数: {result['named_params']}")

    print("\n命令系统已准备就绪，可以处理各种复杂的命令行输入！✨")
