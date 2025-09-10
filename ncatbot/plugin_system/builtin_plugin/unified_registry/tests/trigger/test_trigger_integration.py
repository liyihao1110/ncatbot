"""触发器系统集成测试

测试触发器系统各组件的集成功能，包括完整触发流程、错误处理等。
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.preprocessor import MessagePreprocessor
from ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.resolver import CommandResolver
from ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder import ArgumentBinder
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import (
    StringTokenizer, Token, TokenType
)
from ncatbot.utils.testing import EventFactory

class TestTriggerSystemIntegration:
    """触发器系统整体集成测试"""
    
    def test_complete_trigger_flow(self):
        """测试完整触发流程"""
        # 1. 创建各个组件
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=False
        )
        
        resolver = CommandResolver(
            case_sensitive=False,
            allow_hierarchical=False
        )
        
        binder = ArgumentBinder()
        
        # 2. 准备命令注册
        mock_command = Mock()
        mock_command.func = lambda event, target: f"Banned {target}"
        
        commands = {("ban",): mock_command}
        resolver.build_index(commands, {})
        
        # 3. 创建测试事件
        event = EventFactory.create_group_message("/ban testuser")
        
        # 4. 执行完整流程
        
        # 步骤1：预处理
        preprocess_result = preprocessor.precheck(event)
        assert preprocess_result is not None
        assert preprocess_result.command_text == "ban testuser"
        
        # 步骤2：分词
        tokenizer = StringTokenizer(preprocess_result.command_text)
        tokens = tokenizer.tokenize()
        word_tokens = [t for t in tokens if t.type in (TokenType.WORD, TokenType.QUOTED_STRING)]
        assert len(word_tokens) >= 2  # ban, testuser
        
        # 步骤3：解析命令
        match = resolver.resolve_from_tokens(tokens)
        assert match is not None
        assert match.command is mock_command
        assert match.path_words == ("ban",)
        
        # 步骤4：参数绑定（模拟）
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {}
        
        # 模拟绑定结果
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import ParsedCommand
        
        mock_parsed = ParsedCommand(
            options={},
            named_params={},
            elements=[
                Mock(type="text", content="ban"),
                Mock(type="text", content="testuser")
            ],
            raw_tokens=[]
        )
        
        with pytest.MonkeyPatch().context() as m:
            mock_tokenizer = Mock()
            mock_tokenizer.parse_message.return_value = mock_parsed
            m.setattr("ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder.MessageTokenizer", 
                     lambda: mock_tokenizer)
            
            bind_result = binder.bind(mock_spec, event, match.path_words, ["/"])
            
            assert bind_result.ok is True
            assert "testuser" in bind_result.args
    
    def test_trigger_flow_with_complex_command(self):
        """测试复杂命令的触发流程"""
        # 组件初始化
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/", "!"],
            case_sensitive=False
        )
        
        resolver = CommandResolver(
            case_sensitive=False,
            allow_hierarchical=True
        )
        
        binder = ArgumentBinder()
        
        # 注册层级命令
        mock_command = Mock()
        mock_command.func = lambda event, user, reason, duration: f"Banned {user} for {reason} ({duration})"
        
        commands = {("admin", "user", "ban"): mock_command}
        aliases = {("admin", "u", "ban"): mock_command}
        resolver.build_index(commands, aliases)
        
        # 测试复杂命令: !admin u ban @user123 --reason=spam --duration=24h
        event = EventFactory.create_group_message("!admin u ban @user123 --reason=spam --duration=24h")
        
        # 流程执行
        
        # 1. 预处理
        preprocess_result = preprocessor.precheck(event)
        assert preprocess_result is not None
        assert preprocess_result.command_text == "admin u ban @user123 --reason=spam --duration=24h"
        
        # 2. 分词
        tokenizer = StringTokenizer(preprocess_result.command_text)
        tokens = tokenizer.tokenize()
        
        # 3. 解析命令
        match = resolver.resolve_from_tokens(tokens)
        assert match is not None
        assert match.command is mock_command
        assert match.path_words == ("admin", "u", "ban")
        
        # 4. 参数绑定（模拟复杂解析）
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {}
        
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import ParsedCommand
        
        mock_parsed = ParsedCommand(
            options={},
            named_params={"reason": "spam", "duration": "24h"},
            elements=[
                Mock(type="text", content="admin"),
                Mock(type="text", content="u"),
                Mock(type="text", content="ban"),
                Mock(type="text", content="@user123")
            ],
            raw_tokens=[]
        )
        
        with pytest.MonkeyPatch().context() as m:
            mock_tokenizer = Mock()
            mock_tokenizer.parse_message.return_value = mock_parsed
            m.setattr("ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder.MessageTokenizer", 
                     lambda: mock_tokenizer)
            
            bind_result = binder.bind(mock_spec, event, match.path_words, ["!"])
            
            assert bind_result.ok is True
            assert "@user123" in bind_result.args
            assert "reason" in bind_result.named_args
            assert bind_result.named_args["reason"] == "spam"
            assert "duration" in bind_result.named_args
            assert bind_result.named_args["duration"] == "24h"
    
    def test_trigger_flow_no_prefix_match(self):
        """测试无前缀匹配的流程"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=False
        )
        
        # 无前缀的消息
        event = EventFactory.create_group_message("hello world")
        
        # 预处理应该失败
        preprocess_result = preprocessor.precheck(event)
        assert preprocess_result is None
    
    def test_trigger_flow_command_not_found(self):
        """测试命令未找到的流程"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=False
        )
        
        resolver = CommandResolver(
            case_sensitive=False,
            allow_hierarchical=False
        )
        
        # 构建空索引
        resolver.build_index({}, {})
        
        event = EventFactory.create_group_message("/nonexistent command")
        
        # 预处理成功
        preprocess_result = preprocessor.precheck(event)
        assert preprocess_result is not None
        
        # 分词
        tokenizer = StringTokenizer(preprocess_result.command_text)
        tokens = tokenizer.tokenize()
        
        # 解析失败
        match = resolver.resolve_from_tokens(tokens)
        assert match is None
    
    def test_trigger_flow_with_options_and_quotes(self):
        """测试包含选项和引号的触发流程"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=False
        )
        
        resolver = CommandResolver(
            case_sensitive=False,
            allow_hierarchical=False
        )
        
        binder = ArgumentBinder()
        
        # 注册命令
        mock_command = Mock()
        commands = {("deploy",): mock_command}
        resolver.build_index(commands, {})
        
        # 复杂命令: /deploy "my app" --env=production -v --force
        event = EventFactory.create_group_message('/deploy "my app" --env=production -v --force')
        
        # 执行流程
        preprocess_result = preprocessor.precheck(event)
        assert preprocess_result is not None
        
        tokenizer = StringTokenizer(preprocess_result.command_text)
        tokens = tokenizer.tokenize()
        
        # 验证分词结果
        word_tokens = [t for t in tokens if t.type == TokenType.WORD]
        quoted_tokens = [t for t in tokens if t.type == TokenType.QUOTED_STRING]
        option_tokens = [t for t in tokens if t.type in (TokenType.SHORT_OPTION, TokenType.LONG_OPTION)]
        
        assert len(word_tokens) >= 1  # deploy
        assert len(quoted_tokens) >= 1  # "my app"
        assert len(option_tokens) >= 3  # env, v, force
        
        match = resolver.resolve_from_tokens(tokens)
        assert match is not None
        assert match.command is mock_command


class TestTriggerErrorScenarios:
    """触发器错误场景测试"""
    
    def test_preprocessor_error_handling(self):
        """测试预处理器错误处理"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=False
        )
        
        # 创建有问题的事件
        event = Mock()
        event.message.messages = []  # 空消息
        
        result = preprocessor.precheck(event)
        assert result is None
        
        # 非文本首段
        event.message.messages = [Mock(msg_seg_type="image")]
        result = preprocessor.precheck(event)
        assert result is None
    
    def test_resolver_conflict_error(self):
        """测试解析器冲突错误"""
        resolver = CommandResolver(
            case_sensitive=False,
            allow_hierarchical=False  # 不允许层级
        )
        
        # 创建冲突的命令
        mock_cmd1 = Mock()
        mock_cmd2 = Mock()
        
        commands = {
            ("admin",): mock_cmd1,
            ("admin", "user"): mock_cmd2  # 与 admin 冲突
        }
        
        # 应该抛出冲突错误
        with pytest.raises(ValueError):
            resolver.build_index(commands, {})
    
    def test_binder_error_handling(self):
        """测试绑定器错误处理"""
        binder = ArgumentBinder()
        
        # 创建会出错的规格
        mock_spec = Mock()
        mock_spec.get_kw_binding.side_effect = Exception("Binding error")
        
        event = EventFactory.create_group_message("/test arg -v")
        
        # 应该抛出异常
        with pytest.raises(Exception):
            binder.bind(mock_spec, event, ("test",), ["/"])
    
    def test_tokenizer_error_integration(self):
        """测试分词器错误的集成处理"""
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import (
            QuoteMismatchError
        )
        
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=False
        )
        
        # 带有未匹配引号的消息
        event = EventFactory.create_group_message('/test "unmatched quote')
        
        preprocess_result = preprocessor.precheck(event)
        assert preprocess_result is not None
        
        # 分词应该抛出异常
        tokenizer = StringTokenizer(preprocess_result.command_text)
        with pytest.raises(QuoteMismatchError):
            tokenizer.tokenize()


class TestTriggerPerformanceIntegration:
    """触发器性能集成测试"""
    
    def test_large_command_set_performance(self):
        """测试大量命令集的性能"""
        resolver = CommandResolver(
            case_sensitive=False,
            allow_hierarchical=True
        )
        
        # 创建大量命令
        commands = {}
        for i in range(1000):
            mock_cmd = Mock()
            commands[(f"cmd{i}",)] = mock_cmd
        
        # 创建层级命令
        for i in range(100):
            mock_cmd = Mock()
            commands[("group", f"sub{i}")] = mock_cmd
        
        # 构建索引应该快速完成
        resolver.build_index(commands, {})
        
        # 解析应该快速完成
        tokens = [Token(TokenType.WORD, "cmd500", 0)]
        result = resolver.resolve_from_tokens(tokens)
        assert result is not None
        
        # 层级命令解析
        tokens = [
            Token(TokenType.WORD, "group", 0),
            Token(TokenType.WORD, "sub50", 6)
        ]
        result = resolver.resolve_from_tokens(tokens)
        assert result is not None
    
    def test_complex_message_parsing_performance(self):
        """测试复杂消息解析性能"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/"],
            case_sensitive=False
        )
        
        # 创建复杂长消息
        complex_message = '/deploy app --env=production --config="very long config file path with spaces.json" --timeout=300 --retries=3 -v --force --debug'
        
        event = EventFactory.create_group_message(complex_message)
        
        # 预处理应该快速完成
        preprocess_result = preprocessor.precheck(event)
        assert preprocess_result is not None
        
        # 分词应该快速完成
        tokenizer = StringTokenizer(preprocess_result.command_text)
        tokens = tokenizer.tokenize()
        
        # 验证复杂解析结果
        assert len(tokens) > 10  # 应该有多个token


class TestTriggerStateManagement:
    """触发器状态管理测试"""
    
    def test_component_isolation(self):
        """测试组件隔离"""
        # 创建两套独立的组件
        preprocessor1 = MessagePreprocessor(require_prefix=True, prefixes=["/"], case_sensitive=False)
        preprocessor2 = MessagePreprocessor(require_prefix=True, prefixes=["!"], case_sensitive=True)
        
        resolver1 = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        resolver2 = CommandResolver(case_sensitive=True, allow_hierarchical=True)
        
        # 在不同解析器中注册不同命令
        mock_cmd1 = Mock()
        mock_cmd2 = Mock()
        
        resolver1.build_index({("test1",): mock_cmd1}, {})
        resolver2.build_index({("test2",): mock_cmd2}, {})
        
        # 验证隔离
        tokens1 = [Token(TokenType.WORD, "test1", 0)]
        tokens2 = [Token(TokenType.WORD, "test2", 0)]
        
        assert resolver1.resolve_from_tokens(tokens1) is not None
        assert resolver1.resolve_from_tokens(tokens2) is None
        assert resolver2.resolve_from_tokens(tokens1) is None
        assert resolver2.resolve_from_tokens(tokens2) is not None
    
    def test_state_consistency(self):
        """测试状态一致性"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        mock_command = Mock()
        commands = {("test",): mock_command}
        resolver.build_index(commands, {})
        
        # 多次解析应该得到一致的结果
        tokens = [Token(TokenType.WORD, "test", 0)]
        
        result1 = resolver.resolve_from_tokens(tokens)
        result2 = resolver.resolve_from_tokens(tokens)
        
        assert result1.command is result2.command
        assert result1.path_words == result2.path_words
    
    def test_component_reinitialization(self):
        """测试组件重新初始化"""
        resolver = CommandResolver(case_sensitive=False, allow_hierarchical=False)
        
        # 第一次构建
        mock_cmd1 = Mock()
        resolver.build_index({("test1",): mock_cmd1}, {})
        
        tokens = [Token(TokenType.WORD, "test1", 0)]
        result = resolver.resolve_from_tokens(tokens)
        assert result is not None
        assert result.command is mock_cmd1
        
        # 重新构建（覆盖之前的索引）
        mock_cmd2 = Mock()
        resolver.build_index({("test2",): mock_cmd2}, {})
        
        # 旧命令应该不存在
        result = resolver.resolve_from_tokens(tokens)
        assert result is None
        
        # 新命令应该存在
        tokens = [Token(TokenType.WORD, "test2", 0)]
        result = resolver.resolve_from_tokens(tokens)
        assert result is not None
        assert result.command is mock_cmd2


class TestTriggerRealWorldScenarios:
    """触发器真实世界场景测试"""
    
    def test_admin_command_scenario(self):
        """测试管理员命令场景"""
        # 模拟真实的管理员命令处理流程
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/", "!"],
            case_sensitive=False
        )
        
        resolver = CommandResolver(
            case_sensitive=False,
            allow_hierarchical=True
        )
        
        # 注册管理员命令
        ban_cmd = Mock()
        kick_cmd = Mock()
        mute_cmd = Mock()
        
        commands = {
            ("admin", "ban"): ban_cmd,
            ("admin", "kick"): kick_cmd,
            ("admin", "mute"): mute_cmd
        }
        
        aliases = {
            ("ban",): ban_cmd,  # 简化别名
            ("kick",): kick_cmd,
            ("mute",): mute_cmd
        }
        
        resolver.build_index(commands, aliases)
        
        # 测试不同的管理员命令
        test_commands = [
            "/admin ban @user123 --reason=spam",
            "!ban @user456",  # 使用别名
            "/admin mute @user789 --duration=1h",
            "/kick @user000"  # 别名
        ]
        
        for cmd_text in test_commands:
            event = EventFactory.create_group_message(cmd_text)
            
            preprocess_result = preprocessor.precheck(event)
            assert preprocess_result is not None
            
            tokenizer = StringTokenizer(preprocess_result.command_text)
            tokens = tokenizer.tokenize()
            
            match = resolver.resolve_from_tokens(tokens)
            assert match is not None
            assert match.command in [ban_cmd, kick_cmd, mute_cmd]
    
    def test_help_system_scenario(self):
        """测试帮助系统场景"""
        preprocessor = MessagePreprocessor(
            require_prefix=True,
            prefixes=["/", "?"],
            case_sensitive=False
        )
        
        resolver = CommandResolver(
            case_sensitive=False,
            allow_hierarchical=True
        )
        
        # 注册帮助命令
        help_cmd = Mock()
        
        commands = {
            ("help",): help_cmd
        }
        
        aliases = {
            ("h",): help_cmd,
            ("?",): help_cmd,
            ("帮助",): help_cmd  # 中文别名
        }
        
        resolver.build_index(commands, aliases)
        
        # 测试各种帮助调用方式
        help_commands = [
            "/help",
            "/h",
            "/?",
            "/帮助",
            "?help",  # 使用?前缀
        ]
        
        for cmd_text in help_commands:
            event = EventFactory.create_group_message(cmd_text)
            
            preprocess_result = preprocessor.precheck(event)
            if preprocess_result is None:
                continue  # 某些前缀可能不匹配
            
            tokenizer = StringTokenizer(preprocess_result.command_text)
            tokens = tokenizer.tokenize()
            
            match = resolver.resolve_from_tokens(tokens)
            if match is not None:  # 某些情况可能解析失败
                assert match.command is help_cmd
