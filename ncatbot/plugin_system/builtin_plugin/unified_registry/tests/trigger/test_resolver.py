"""命令解析器测试

测试命令解析器的功能，包括命令匹配、层级命令解析、冲突检测等。
"""

import pytest
from unittest.mock import Mock

from ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.resolver import (
    CommandResolver, CommandEntry
)
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.utils.specs import CommandSpec
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import (
    Token, TokenType
)


class TestCommandEntry:
    """命令条目测试"""
    
    def test_command_entry_creation(self):
        """测试命令条目创建"""
        mock_command = Mock()
        mock_command.func = lambda: "test"
        
        entry = CommandEntry(
            path_words=("admin", "user"),
            command=mock_command
        )
        
        assert entry.path_words == ("admin", "user")
        assert entry.command is mock_command


class TestCommandResolver:
    """命令解析器测试"""
    
    def test_resolver_creation(self):
        """测试解析器创建"""
        resolver = CommandResolver(
            case_sensitive=False,
            allow_hierarchical=False
        )
        
        assert resolver.case_sensitive is False
        assert resolver.allow_hierarchical is False
        assert len(resolver._index) == 0
    
    def test_resolver_creation_with_different_config(self):
        """测试不同配置的解析器"""
        resolver = CommandResolver(
            case_sensitive=True,
            allow_hierarchical=True
        )
        
        assert resolver.case_sensitive is True
        assert resolver.allow_hierarchical is True
    
    def test_normalize_case_sensitive(self):
        """测试大小写敏感的规范化"""
        resolver = CommandResolver(case_sensitive=True, allow_hierarchical=False)
        
        result = resolver._normalize("Hello")
        assert result == "Hello"
    
    def test_normalize_case_insensitive(self):
        """测试大小写不敏感的规范化"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        result = resolver._normalize("Hello")
        assert result == "hello"
    
    def test_path_to_norm(self):
        """测试路径规范化"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        path = ("Admin", "User", "Ban")
        normalized = resolver._path_to_norm(path)
        
        assert normalized == ("admin", "user", "ban")
    
    def test_build_index_simple(self):
        """测试简单索引构建"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        # 创建模拟命令
        mock_command1 = Mock()
        mock_command1.func = lambda: "hello"
        
        mock_command2 = Mock()
        mock_command2.func = lambda: "bye"
        
        commands = {
            ("hello",): mock_command1,
            ("bye",): mock_command2
        }
        
        aliases = {}
        
        resolver.build_index(commands, aliases)
        
        # 验证索引构建
        assert len(resolver._index) == 2
        assert ("hello",) in resolver._index
        assert ("bye",) in resolver._index
    
    def test_build_index_with_aliases(self):
        """测试带别名的索引构建"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        mock_command = Mock()
        mock_command.func = lambda: "status"
        
        commands = {
            ("status",): mock_command
        }
        
        aliases = {
            ("st",): mock_command,
            ("stat",): mock_command
        }
        
        resolver.build_index(commands, aliases)
        
        # 验证主命令和别名都在索引中
        assert len(resolver._index) == 3
        assert ("status",) in resolver._index
        assert ("st",) in resolver._index
        assert ("stat",) in resolver._index
    
    def test_build_index_hierarchical_allowed(self):
        """测试允许层级的索引构建"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=True)
        
        mock_cmd1 = Mock()
        mock_cmd1.func = lambda: "admin"
        
        mock_cmd2 = Mock()
        mock_cmd2.func = lambda: "admin_user"
        
        commands = {
            ("admin",): mock_cmd1,
            ("admin", "user"): mock_cmd2
        }
        
        # 层级命令应该被允许
        resolver.build_index(commands, {})
        
        assert len(resolver._index) == 2
        assert ("admin",) in resolver._index
        assert ("admin", "user") in resolver._index
    
    def test_build_index_hierarchical_conflict(self):
        """测试层级冲突检测"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        mock_cmd1 = Mock()
        mock_cmd1.func = lambda: "admin"
        
        mock_cmd2 = Mock()
        mock_cmd2.func = lambda: "admin_user"
        
        commands = {
            ("admin",): mock_cmd1,
            ("admin", "user"): mock_cmd2  # 与 ("admin",) 存在前缀关系
        }
        
        # 不允许层级时应该抛出异常
        with pytest.raises(ValueError) as exc_info:
            resolver.build_index(commands, {})
        
        assert "前缀冲突" in str(exc_info.value) or "conflict" in str(exc_info.value).lower()
    
    def test_build_index_duplicate_command(self):
        """测试重复命令检测"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        mock_cmd1 = Mock()
        mock_cmd1.func = lambda: "test1"
        
        mock_cmd2 = Mock()
        mock_cmd2.func = lambda: "test2"
        
        commands = {
            ("test",): mock_cmd1
        }
        
        aliases = {
            ("test",): mock_cmd2  # 与命令名重复
        }
        
        # 重复命令应该抛出异常
        with pytest.raises(ValueError) as exc_info:
            resolver.build_index(commands, aliases)
        
        assert "重复" in str(exc_info.value) or "duplicate" in str(exc_info.value).lower()
    
    def test_resolve_from_tokens_simple(self):
        """测试简单token解析"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        # 构建索引
        mock_command = Mock()
        mock_command.func = lambda: "hello"
        
        commands = {("hello",): mock_command}
        resolver.build_index(commands, {})
        
        # 创建tokens
        tokens = [
            Token(TokenType.WORD, "hello", 0),
            Token(TokenType.WORD, "world", 6)
        ]
        
        result = resolver.resolve_from_tokens(tokens)
        
        assert result is not None
        assert result.command is mock_command
        assert result.path_words == ("hello",)
    
    def test_resolve_from_tokens_not_found(self):
        """测试未找到命令的解析"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        # 构建空索引
        resolver.build_index({}, {})
        
        tokens = [
            Token(TokenType.WORD, "nonexistent", 0)
        ]
        
        result = resolver.resolve_from_tokens(tokens)
        assert result is None
    
    def test_resolve_from_tokens_case_insensitive(self):
        """测试大小写不敏感的解析"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        mock_command = Mock()
        mock_command.func = lambda: "hello"
        
        commands = {("hello",): mock_command}
        resolver.build_index(commands, {})
        
        # 使用大写输入
        tokens = [
            Token(TokenType.WORD, "HELLO", 0)
        ]
        
        result = resolver.resolve_from_tokens(tokens)
        
        assert result is not None
        assert result.command is mock_command
    
    def test_resolve_from_tokens_case_sensitive(self):
        """测试大小写敏感的解析"""
        resolver = CommandResolver(case_sensitive=True, allow_hierarchical=False)
        
        mock_command = Mock()
        mock_command.func = lambda: "hello"
        
        commands = {("hello",): mock_command}
        resolver.build_index(commands, {})
        
        # 正确大小写
        tokens = [Token(TokenType.WORD, "hello", 0)]
        result = resolver.resolve_from_tokens(tokens)
        assert result is not None
        
        # 错误大小写
        tokens = [Token(TokenType.WORD, "HELLO", 0)]
        result = resolver.resolve_from_tokens(tokens)
        assert result is None
    
    def test_resolve_from_tokens_hierarchical(self):
        """测试层级命令解析"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=True)
        
        mock_cmd1 = Mock()
        mock_cmd1.func = lambda: "admin"
        
        mock_cmd2 = Mock()
        mock_cmd2.func = lambda: "admin_user_ban"
        
        commands = {
            ("admin",): mock_cmd1,
            ("admin", "user", "ban"): mock_cmd2
        }
        
        resolver.build_index(commands, {})
        
        # 解析长命令
        tokens = [
            Token(TokenType.WORD, "admin", 0),
            Token(TokenType.WORD, "user", 6),
            Token(TokenType.WORD, "ban", 11)
        ]
        
        result = resolver.resolve_from_tokens(tokens)
        
        # 应该匹配最长的命令
        assert result is not None
        assert result.command is mock_cmd2
        assert result.path_words == ("admin", "user", "ban")
    
    def test_resolve_from_tokens_partial_match(self):
        """测试部分匹配解析"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=True)
        
        mock_cmd = Mock()
        mock_cmd.func = lambda: "admin_user"
        
        commands = {
            ("admin", "user"): mock_cmd
        }
        
        resolver.build_index(commands, {})
        
        # 只有部分token匹配
        tokens = [
            Token(TokenType.WORD, "admin", 0),
            Token(TokenType.WORD, "user", 6),
            Token(TokenType.WORD, "extra", 11)  # 额外的token
        ]
        
        result = resolver.resolve_from_tokens(tokens)
        
        # 应该匹配部分命令
        assert result is not None
        assert result.command is mock_cmd
        assert result.path_words == ("admin", "user")
    
    def test_resolve_from_tokens_with_options(self):
        """测试包含选项的token解析"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        mock_command = Mock()
        mock_command.func = lambda: "deploy"
        
        commands = {("deploy",): mock_command}
        resolver.build_index(commands, {})
        
        # 包含选项的tokens
        tokens = [
            Token(TokenType.WORD, "deploy", 0),
            Token(TokenType.SHORT_OPTION, "v", 7),  # 选项应该停止命令词聚合
            Token(TokenType.WORD, "app", 10)
        ]
        
        result = resolver.resolve_from_tokens(tokens)
        
        assert result is not None
        assert result.command is mock_command
        assert result.path_words == ("deploy",)
    
    def test_resolve_from_tokens_quoted_strings(self):
        """测试包含引用字符串的解析"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        mock_command = Mock()
        mock_command.func = lambda: "echo"
        
        commands = {("echo",): mock_command}
        resolver.build_index(commands, {})
        
        tokens = [
            Token(TokenType.WORD, "echo", 0),
            Token(TokenType.QUOTED_STRING, "hello world", 5),
            Token(TokenType.WORD, "test", 18)
        ]
        
        result = resolver.resolve_from_tokens(tokens)
        
        assert result is not None
        assert result.command is mock_command
    
    def test_resolve_from_tokens_empty_tokens(self):
        """测试空token列表"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        mock_command = Mock()
        commands = {("test",): mock_command}
        resolver.build_index(commands, {})
        
        result = resolver.resolve_from_tokens([])
        assert result is None
    
    def test_resolve_from_tokens_non_word_first(self):
        """测试首个token不是单词的情况"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        mock_command = Mock()
        commands = {("test",): mock_command}
        resolver.build_index(commands, {})
        
        tokens = [
            Token(TokenType.SHORT_OPTION, "v", 0),  # 首个是选项
            Token(TokenType.WORD, "test", 3)
        ]
        
        result = resolver.resolve_from_tokens(tokens)
        assert result is None  # 没有命令词


class TestCommandResolverEdgeCases:
    """命令解析器边界情况测试"""
    
    def test_very_long_command_path(self):
        """测试很长的命令路径"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=True)
        
        # 创建深层嵌套命令
        long_path = tuple(f"level{i}" for i in range(20))
        mock_command = Mock()
        mock_command.func = lambda: "deep_command"
        
        commands = {long_path: mock_command}
        resolver.build_index(commands, {})
        
        # 创建匹配的tokens
        tokens = [Token(TokenType.WORD, f"level{i}", i*10) for i in range(20)]
        
        result = resolver.resolve_from_tokens(tokens)
        
        assert result is not None
        assert result.command is mock_command
        assert result.path_words == tuple(f"level{i}" for i in range(20))
    
    def test_unicode_command_names(self):
        """测试Unicode命令名"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        mock_command = Mock()
        mock_command.func = lambda: "unicode_cmd"
        
        unicode_path = ("测试", "命令")
        commands = {unicode_path: mock_command}
        resolver.build_index(commands, {})
        
        tokens = [
            Token(TokenType.WORD, "测试", 0),
            Token(TokenType.WORD, "命令", 3)
        ]
        
        result = resolver.resolve_from_tokens(tokens)
        
        assert result is not None
        assert result.command is mock_command
    
    def test_special_character_commands(self):
        """测试特殊字符命令"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        mock_command = Mock()
        mock_command.func = lambda: "special_cmd"
        
        special_path = ("cmd-with-dashes", "sub_with_underscores")
        commands = {special_path: mock_command}
        resolver.build_index(commands, {})
        
        tokens = [
            Token(TokenType.WORD, "cmd-with-dashes", 0),
            Token(TokenType.WORD, "sub_with_underscores", 16)
        ]
        
        result = resolver.resolve_from_tokens(tokens)
        
        assert result is not None
        assert result.command is mock_command
    
    def test_case_boundary_conflicts(self):
        """测试大小写边界冲突"""
        resolver = CommandResolver(case_sensitive=True, allow_hierarchical=False)
        
        mock_cmd1 = Mock()
        mock_cmd1.func = lambda: "lower"
        
        mock_cmd2 = Mock()
        mock_cmd2.func = lambda: "upper"
        
        commands = {
            ("test",): mock_cmd1,
            ("TEST",): mock_cmd2  # 大小写不同
        }
        
        # 大小写敏感时应该允许
        resolver.build_index(commands, {})
        
        assert len(resolver._index) == 2
        assert ("test",) in resolver._index
        assert ("TEST",) in resolver._index
    
    def test_mixed_token_types_in_command(self):
        """测试命令中混合token类型"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        mock_command = Mock()
        commands = {("test",): mock_command}
        resolver.build_index(commands, {})
        
        # 混合不同类型的tokens
        tokens = [
            Token(TokenType.WORD, "test", 0),
            Token(TokenType.QUOTED_STRING, "quoted", 5),  # 引用字符串也应该算作命令词
            Token(TokenType.SHORT_OPTION, "v", 13)  # 选项停止命令词聚合
        ]
        
        result = resolver.resolve_from_tokens(tokens)
        
        # 根据实现，可能只匹配第一个WORD token
        assert result is not None
        assert result.command is mock_command


class TestCommandResolverIntegration:
    """命令解析器集成测试"""
    
    def test_resolver_with_real_command_structure(self):
        """测试与真实命令结构的集成"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=True)
        
        # 模拟真实的命令结构
        commands = {}
        aliases = {}
        
        # 根级命令
        help_cmd = Mock()
        help_cmd.func = lambda: "help"
        commands[("help",)] = help_cmd
        aliases[("h",)] = help_cmd
        aliases[("?",)] = help_cmd
        
        # 管理员命令组
        admin_reload = Mock()
        admin_reload.func = lambda: "admin_reload"
        commands[("admin", "reload")] = admin_reload
        
        admin_user_ban = Mock()
        admin_user_ban.func = lambda: "admin_user_ban"
        commands[("admin", "user", "ban")] = admin_user_ban
        aliases[("admin", "u", "ban")] = admin_user_ban
        
        resolver.build_index(commands, aliases)
        
        # 测试各种解析场景
        test_cases = [
            (["help"], help_cmd),
            (["h"], help_cmd),
            (["?"], help_cmd),
            (["admin", "reload"], admin_reload),
            (["admin", "user", "ban"], admin_user_ban),
            (["admin", "u", "ban"], admin_user_ban),
        ]
        
        for words, expected_cmd in test_cases:
            tokens = [Token(TokenType.WORD, word, i*10) for i, word in enumerate(words)]
            result = resolver.resolve_from_tokens(tokens)
            
            assert result is not None, f"Failed to resolve: {words}"
            assert result.command is expected_cmd, f"Wrong command for: {words}"
    
    def test_resolver_performance_with_many_commands(self):
        """测试大量命令的解析性能"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=True)
        
        # 创建大量命令
        commands = {}
        for i in range(1000):
            mock_cmd = Mock()
            mock_cmd.func = lambda: f"cmd_{i}"
            commands[(f"cmd{i}",)] = mock_cmd
        
        # 创建一些层级命令
        for i in range(100):
            mock_cmd = Mock()
            mock_cmd.func = lambda: f"nested_cmd_{i}"
            commands[("group", f"sub{i}")] = mock_cmd
        
        resolver.build_index(commands, {})
        
        # 测试解析性能
        tokens = [Token(TokenType.WORD, "cmd500", 0)]
        result = resolver.resolve_from_tokens(tokens)
        
        assert result is not None
        
        # 测试嵌套命令解析
        tokens = [
            Token(TokenType.WORD, "group", 0),
            Token(TokenType.WORD, "sub50", 6)
        ]
        result = resolver.resolve_from_tokens(tokens)
        
        assert result is not None
    
    def test_resolver_state_isolation(self):
        """测试解析器状态隔离"""
        resolver1 = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        resolver2 = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        # 在不同解析器中构建不同的索引
        mock_cmd1 = Mock()
        mock_cmd1.func = lambda: "resolver1_cmd"
        
        mock_cmd2 = Mock()
        mock_cmd2.func = lambda: "resolver2_cmd"
        
        resolver1.build_index({("test1",): mock_cmd1}, {})
        resolver2.build_index({("test2",): mock_cmd2}, {})
        
        # 验证隔离
        tokens1 = [Token(TokenType.WORD, "test1", 0)]
        tokens2 = [Token(TokenType.WORD, "test2", 0)]
        
        result1_from_1 = resolver1.resolve_from_tokens(tokens1)
        result1_from_2 = resolver2.resolve_from_tokens(tokens1)
        result2_from_1 = resolver1.resolve_from_tokens(tokens2)
        result2_from_2 = resolver2.resolve_from_tokens(tokens2)
        
        assert result1_from_1 is not None
        assert result1_from_2 is None
        assert result2_from_1 is None
        assert result2_from_2 is not None
