"""参数绑定器测试

测试参数绑定器的功能，包括基本绑定、命名参数绑定、选项绑定等。
"""

import pytest
from unittest.mock import Mock

from ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder import (
    ArgumentBinder, BindResult
)
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.utils.specs import CommandSpec
from ncatbot.utils.testing import EventFactory
from ncatbot.core.event.message_segment import MessageArray, Text, At, Image

class TestArgumentBinder:
    """参数绑定器测试"""
    
    def test_binder_creation(self):
        """测试绑定器创建"""
        binder = ArgumentBinder()
        assert binder is not None
    
    def test_bind_simple_command(self):
        """测试简单命令绑定"""
        binder = ArgumentBinder()
        
        # 创建模拟规格
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {}
        
        # 创建简单消息事件
        event = EventFactory.create_group_message("hello world")
        
        # 绑定参数
        result = binder.bind(mock_spec, event, ("hello",), ["/"])
        
        assert result.ok is True
        assert len(result.args) >= 1  # 至少有"world"
        assert isinstance(result.named_args, dict)
    
    def test_bind_with_path_words_skipping(self):
        """测试路径词跳过"""
        binder = ArgumentBinder()
        
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {}
        
        # 命令：/admin user ban target_user
        # 路径词：("admin", "user", "ban")
        # 应该跳过前三个词，绑定"target_user"
        event = EventFactory.create_group_message("/admin user ban target_user")
        
        result = binder.bind(mock_spec, event, ("admin", "user", "ban"), ["/"])
        print(result.named_args, result.args)
        assert result.ok is True
        assert "target_user" in result.args
    
    def test_bind_with_named_parameters(self):
        """测试命名参数绑定"""
        binder = ArgumentBinder()
        
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {}
        
        # 创建带命名参数的消息
        # 这需要模拟MessageTokenizer的行为
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.message_tokenizer import MessageTokenizer
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import ParsedCommand
        
        # 模拟解析结果
        mock_parsed = ParsedCommand(
            options={},
            named_params={"env": "production", "timeout": "30"},
            elements=[
                Mock(type="text", content="deploy"),
                Mock(type="text", content="myapp")
            ],
            raw_tokens=[]
        )
        
        # 模拟tokenizer
        with pytest.MonkeyPatch().context() as m:
            mock_tokenizer = Mock()
            mock_tokenizer.parse_message.return_value = mock_parsed
            m.setattr("ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder.MessageTokenizer", 
                     lambda: mock_tokenizer)
            
            event = EventFactory.create_group_message("deploy myapp --env=production --timeout=30")
            result = binder.bind(mock_spec, event, ("deploy",), ["/"])
            
            assert result.ok is True
            assert "env" in result.named_args
            assert result.named_args["env"] == "production"
            assert "timeout" in result.named_args
            assert result.named_args["timeout"] == "30"
    
    def test_bind_with_options(self):
        """测试选项绑定"""
        binder = ArgumentBinder()
        
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {"verbose": True, "force": True}
        
        # 模拟带选项的解析结果
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import ParsedCommand
        
        mock_parsed = ParsedCommand(
            options={"v": True, "force": True},
            named_params={},
            elements=[
                Mock(type="text", content="deploy"),
                Mock(type="text", content="app")
            ],
            raw_tokens=[]
        )
        
        with pytest.MonkeyPatch().context() as m:
            mock_tokenizer = Mock()
            mock_tokenizer.parse_message.return_value = mock_parsed
            m.setattr("ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder.MessageTokenizer", 
                     lambda: mock_tokenizer)
            
            event = EventFactory.create_group_message("deploy app -v --force")
            result = binder.bind(mock_spec, event, ("deploy",), ["/"])
            
            assert result.ok is True
            assert "verbose" in result.named_args
            assert "force" in result.named_args
            assert result.named_args["verbose"] is True
            assert result.named_args["force"] is True
    
    def test_bind_with_complex_message(self):
        """测试复杂消息绑定"""
        binder = ArgumentBinder()
        
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {}
        
        # 创建包含非文本元素的消息
        text1 = Text("/send ")
        at_segment = At("123456")
        text2 = Text(" urgent message")
        
        message_array = MessageArray(text1, at_segment, text2)
        event = EventFactory.create_group_message(message_array)
        
        # 模拟解析结果
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import ParsedCommand
        
        mock_parsed = ParsedCommand(
            options={},
            named_params={},
            elements=[
                Mock(type="text", content="send"),
                Mock(type="at", content="123456"),
                Mock(type="text", content="urgent"),
                Mock(type="text", content="message")
            ],
            raw_tokens=[]
        )
        
        with pytest.MonkeyPatch().context() as m:
            mock_tokenizer = Mock()
            mock_tokenizer.parse_message.return_value = mock_parsed
            m.setattr("ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder.MessageTokenizer", 
                     lambda: mock_tokenizer)
            
            result = binder.bind(mock_spec, event, ("send",), ["/"])
            
            assert result.ok is True
            assert len(result.args) >= 3  # @用户, urgent, message
    
    def test_bind_prefix_matching(self):
        """测试前缀匹配"""
        binder = ArgumentBinder()
        
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {}
        
        # 测试不同前缀
        test_cases = [
            ("/test arg", ["/"], ("test",)),
            ("!test arg", ["!", "/"], ("test",)),
            ("#test arg", ["#", "!", "/"], ("test",))
        ]
        
        for message_text, prefixes, path_words in test_cases:
            event = EventFactory.create_group_message(message_text)
            
            # 模拟简单解析
            from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import ParsedCommand
            
            mock_parsed = ParsedCommand(
                options={},
                named_params={},
                elements=[
                    Mock(type="text", content="test"),
                    Mock(type="text", content="arg")
                ],
                raw_tokens=[]
            )
            
            with pytest.MonkeyPatch().context() as m:
                mock_tokenizer = Mock()
                mock_tokenizer.parse_message.return_value = mock_parsed
                m.setattr("ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder.MessageTokenizer", 
                         lambda: mock_tokenizer)
                
                result = binder.bind(mock_spec, event, path_words, prefixes)
                
                assert result.ok is True
                assert "arg" in result.args
    
    def test_bind_error_handling(self):
        """测试绑定错误处理"""
        binder = ArgumentBinder()
        
        mock_spec = Mock()
        mock_spec.get_kw_binding.side_effect = Exception("Spec error")
        
        event = EventFactory.create_group_message("test message --output")
        
        # 应该捕获并处理异常
        with pytest.raises(Exception):
            binder.bind(mock_spec, event, ("test",), ["/"])
    
    def test_bind_empty_message(self):
        """测试空消息绑定"""
        binder = ArgumentBinder()
        
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {}
        
        event = EventFactory.create_group_message(MessageArray())
        
        # 模拟空解析结果
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import ParsedCommand
        
        mock_parsed = ParsedCommand(
            options={},
            named_params={},
            elements=[],
            raw_tokens=[]
        )
        
        with pytest.MonkeyPatch().context() as m:
            mock_tokenizer = Mock()
            mock_tokenizer.parse_message.return_value = mock_parsed
            m.setattr("ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder.MessageTokenizer", 
                     lambda: mock_tokenizer)
            
            result = binder.bind(mock_spec, event, (), ["/"])
            
            assert result.ok is True
            assert len(result.args) == 0
    
    def test_bind_path_words_mismatch(self):
        """测试路径词不匹配"""
        binder = ArgumentBinder()
        
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {}
        
        # 消息: "/test arg"
        # 路径词: ("admin", "user") - 不匹配
        event = EventFactory.create_group_message("/test arg")
        
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import ParsedCommand
        
        mock_parsed = ParsedCommand(
            options={},
            named_params={},
            elements=[
                Mock(type="text", content="/test"),  # 带前缀
                Mock(type="text", content="arg")
            ],
            raw_tokens=[]
        )
        
        with pytest.MonkeyPatch().context() as m:
            mock_tokenizer = Mock()
            mock_tokenizer.parse_message.return_value = mock_parsed
            m.setattr("ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder.MessageTokenizer", 
                     lambda: mock_tokenizer)
            
            result = binder.bind(mock_spec, event, ("admin", "user"), ["/"])
            
            # 应该仍然成功，但跳过逻辑可能不同
            assert result.ok is True
    
    def test_bind_partial_path_match(self):
        """测试部分路径匹配"""
        binder = ArgumentBinder()
        
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {}
        
        # 消息: "/admin user ban target extra"
        # 路径词: ("admin", "user") - 部分匹配
        event = EventFactory.create_group_message("/admin user ban target extra")
        
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import ParsedCommand
        
        mock_parsed = ParsedCommand(
            options={},
            named_params={},
            elements=[
                Mock(type="text", content="/admin"),
                Mock(type="text", content="user"), 
                Mock(type="text", content="ban"),
                Mock(type="text", content="target"),
                Mock(type="text", content="extra")
            ],
            raw_tokens=[]
        )
        
        with pytest.MonkeyPatch().context() as m:
            mock_tokenizer = Mock()
            mock_tokenizer.parse_message.return_value = mock_parsed
            m.setattr("ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder.MessageTokenizer", 
                     lambda: mock_tokenizer)
            
            result = binder.bind(mock_spec, event, ("admin", "user"), ["/"])
            
            assert result.ok is True
            # 应该跳过"admin", "user"，绑定"ban", "target", "extra"
            assert "ban" in result.args
            assert "target" in result.args
            assert "extra" in result.args


class TestArgumentBinderEdgeCases:
    """参数绑定器边界情况测试"""
    
    def test_bind_very_long_argument_list(self):
        """测试很长的参数列表"""
        binder = ArgumentBinder()
        
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {}
        
        # 创建很长的参数列表
        long_args = " ".join([f"arg{i}" for i in range(100)])
        event = EventFactory.create_group_message(f"/test {long_args}")
        
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import ParsedCommand
        
        elements = [Mock(type="text", content="test")]
        elements.extend([Mock(type="text", content=f"arg{i}") for i in range(100)])
        
        mock_parsed = ParsedCommand(
            options={},
            named_params={},
            elements=elements,
            raw_tokens=[]
        )
        
        with pytest.MonkeyPatch().context() as m:
            mock_tokenizer = Mock()
            mock_tokenizer.parse_message.return_value = mock_parsed
            m.setattr("ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder.MessageTokenizer", 
                     lambda: mock_tokenizer)
            
            result = binder.bind(mock_spec, event, ("test",), ["/"])
            
            assert result.ok is True
            assert len(result.args) == 100
    
    def test_bind_unicode_arguments(self):
        """测试Unicode参数"""
        binder = ArgumentBinder()
        
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {}
        
        event = EventFactory.create_group_message("/测试 参数一 参数二")
        
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import ParsedCommand
        
        mock_parsed = ParsedCommand(
            options={},
            named_params={},
            elements=[
                Mock(type="text", content="测试"),
                Mock(type="text", content="参数一"),
                Mock(type="text", content="参数二")
            ],
            raw_tokens=[]
        )
        
        with pytest.MonkeyPatch().context() as m:
            mock_tokenizer = Mock()
            mock_tokenizer.parse_message.return_value = mock_parsed
            m.setattr("ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder.MessageTokenizer", 
                     lambda: mock_tokenizer)
            
            result = binder.bind(mock_spec, event, ("测试",), ["/"])
            
            assert result.ok is True
            assert "参数一" in result.args
            assert "参数二" in result.args
    
    def test_bind_special_characters(self):
        """测试特殊字符参数"""
        binder = ArgumentBinder()
        
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {}
        
        # 包含特殊字符的参数
        event = EventFactory.create_group_message('/test "quoted arg" arg@with@symbols')
        
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import ParsedCommand
        
        mock_parsed = ParsedCommand(
            options={},
            named_params={},
            elements=[
                Mock(type="text", content="test"),
                Mock(type="text", content="quoted arg"),  # 引号已被处理
                Mock(type="text", content="arg@with@symbols")
            ],
            raw_tokens=[]
        )
        
        with pytest.MonkeyPatch().context() as m:
            mock_tokenizer = Mock()
            mock_tokenizer.parse_message.return_value = mock_parsed
            m.setattr("ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder.MessageTokenizer", 
                     lambda: mock_tokenizer)
            
            result = binder.bind(mock_spec, event, ("test",), ["/"])
            
            assert result.ok is True
            assert "quoted arg" in result.args
            assert "arg@with@symbols" in result.args
    
    def test_bind_mixed_content_types(self):
        """测试混合内容类型"""
        binder = ArgumentBinder()
        
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {}
        
        event = EventFactory.create_group_message("mixed content message")
        
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import ParsedCommand
        
        # 混合文本和非文本元素
        mock_parsed = ParsedCommand(
            options={},
            named_params={},
            elements=[
                Mock(type="text", content="cmd"),
                Mock(type="at", content="user123"),
                Mock(type="text", content="message"),
                Mock(type="image", content="image.jpg")
            ],
            raw_tokens=[]
        )
        
        with pytest.MonkeyPatch().context() as m:
            mock_tokenizer = Mock()
            mock_tokenizer.parse_message.return_value = mock_parsed
            m.setattr("ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder.MessageTokenizer", 
                     lambda: mock_tokenizer)
            
            result = binder.bind(mock_spec, event, ("cmd",), ["/"])
            
            assert result.ok is True
            # 应该包含所有类型的内容
            assert len(result.args) == 3  # @user, message, image
    
    def test_bind_error_recovery(self):
        """测试错误恢复"""
        binder = ArgumentBinder()
        
        # 模拟规格错误
        mock_spec = Mock()
        mock_spec.get_kw_binding.side_effect = KeyError("Missing option")
        
        event = EventFactory.create_group_message("/test --unknown-option")
        
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import ParsedCommand
        
        mock_parsed = ParsedCommand(
            options={"unknown-option": True},
            named_params={},
            elements=[Mock(type="text", content="test")],
            raw_tokens=[]
        )
        
        with pytest.MonkeyPatch().context() as m:
            mock_tokenizer = Mock()
            mock_tokenizer.parse_message.return_value = mock_parsed
            m.setattr("ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder.MessageTokenizer", 
                     lambda: mock_tokenizer)
            
            # 应该抛出异常或返回错误结果
            with pytest.raises(Exception):
                binder.bind(mock_spec, event, ("test",), ["/"])


class TestArgumentBinderIntegration:
    """参数绑定器集成测试"""
    
    def test_full_binding_workflow(self):
        """测试完整绑定工作流"""
        binder = ArgumentBinder()
        
        # 创建真实的CommandSpec（模拟）
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {"verbose": True, "force": True}
        
        # 复杂命令：/deploy myapp --env=prod -v --force "config.json"
        event = EventFactory.create_group_message("/deploy myapp --env=prod -v --force config.json")
        
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import ParsedCommand
        
        mock_parsed = ParsedCommand(
            options={"v": True, "force": True},
            named_params={"env": "prod"},
            elements=[
                Mock(type="text", content="deploy"),
                Mock(type="text", content="myapp"),
                Mock(type="text", content="config.json")
            ],
            raw_tokens=[]
        )
        
        with pytest.MonkeyPatch().context() as m:
            mock_tokenizer = Mock()
            mock_tokenizer.parse_message.return_value = mock_parsed
            m.setattr("ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder.MessageTokenizer", 
                     lambda: mock_tokenizer)
            
            result = binder.bind(mock_spec, event, ("deploy",), ["/"])
            
            assert result.ok is True
            
            # 验证位置参数
            assert "myapp" in result.args
            assert "config.json" in result.args
            
            # 验证命名参数
            assert "env" in result.named_args
            assert result.named_args["env"] == "prod"
            
            # 验证选项绑定
            assert "verbose" in result.named_args
            assert "force" in result.named_args
            assert result.named_args["verbose"] is True
            assert result.named_args["force"] is True
    
    def test_binding_consistency(self):
        """测试绑定一致性"""
        binder = ArgumentBinder()
        
        mock_spec = Mock()
        mock_spec.get_kw_binding.return_value = {}
        
        # 相同输入应该产生一致的结果
        event = EventFactory.create_group_message("/test arg1 arg2")
        
        from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.lexer.tokenizer import ParsedCommand
        
        mock_parsed = ParsedCommand(
            options={},
            named_params={},
            elements=[
                Mock(type="text", content="test"),
                Mock(type="text", content="arg1"),
                Mock(type="text", content="arg2")
            ],
            raw_tokens=[]
        )
        
        with pytest.MonkeyPatch().context() as m:
            mock_tokenizer = Mock()
            mock_tokenizer.parse_message.return_value = mock_parsed
            m.setattr("ncatbot.plugin_system.builtin_plugin.unified_registry.trigger.binder.MessageTokenizer", 
                     lambda: mock_tokenizer)
            
            # 多次绑定应该得到相同结果
            result1 = binder.bind(mock_spec, event, ("test",), ["/"])
            result2 = binder.bind(mock_spec, event, ("test",), ["/"])
            
            assert result1.ok == result2.ok
            assert result1.args == result2.args
            assert result1.named_args == result2.named_args
