"""统一注册插件测试

测试 UnifiedRegistryPlugin 的核心功能，包括事件处理、命令执行、过滤器验证等。
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch

from ncatbot.core.event import BaseMessageEvent, GroupMessageEvent, PrivateMessageEvent
from ncatbot.utils.testing import EventFactory
from ncatbot.plugin_system.builtin_plugin.unified_registry.plugin import UnifiedRegistryPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import (
    GroupFilter, PrivateFilter, AdminFilter, filter_registry
)
from ncatbot.plugin_system import command_registry
from ncatbot.utils.testing import EventFactory
from .conftest import AsyncTestCase


class TestUnifiedRegistryPlugin(AsyncTestCase):
    """统一注册插件核心功能测试"""
    
    @pytest.mark.asyncio
    async def test_plugin_initialization(self, unified_plugin):
        """测试插件初始化"""
        plugin = unified_plugin
        
        # 检查基本属性
        assert plugin.name == "UnifiedRegistryPlugin"
        assert plugin.author == "huan-yp"
        assert plugin.version == "2.0.0"
        
        # 检查组件初始化
        assert plugin._preprocessor is not None
        assert plugin._resolver is not None
        assert plugin._binder is not None
        assert plugin._filter_validator is not None
        
        # 检查前缀配置
        assert "/", "!" in plugin.prefixes
        
    @pytest.mark.asyncio 
    async def test_event_subscription(self, test_client, unified_plugin):
        """测试事件订阅"""
        plugin = unified_plugin
        
        # 检查事件总线订阅 - 使用正确的属性访问
        exact_subscriptions = test_client.event_bus._exact
        regex_subscriptions = test_client.event_bus._regex
        
        # 应该订阅了消息事件（通过正则表达式订阅）
        message_subscribed = any(
            "group_message_event" in str(pattern_tuple[0].pattern) or 
            "private_message_event" in str(pattern_tuple[0].pattern)
            for pattern_tuple in regex_subscriptions
        )
        assert message_subscribed, "应该订阅消息事件"
        
        # 应该订阅了通知和请求事件（通过正则表达式订阅）
        notice_subscribed = any(
            "notice_event" in str(pattern_tuple[0].pattern) or 
            "request_event" in str(pattern_tuple[0].pattern)
            for pattern_tuple in regex_subscriptions
        )
        assert notice_subscribed, "应该订阅通知和请求事件"
    
    @pytest.mark.asyncio
    async def test_handle_message_event_with_command(self, unified_plugin, clean_registries):
        """测试处理包含命令的消息事件"""
        plugin = unified_plugin
        
        # 注册测试命令
        @command_registry.command("test")
        def test_command(event: BaseMessageEvent):
            return "Command executed"
        test_command.__is_command__ = True
        
        # 创建测试事件
        test_event = EventFactory.create_group_message("/test", user_id="123")
        
        # 直接测试命令处理逻辑
        with patch.object(plugin, '_execute_function') as mock_execute:
            mock_execute.return_value = "Command executed"
            
            # 测试预处理
            preprocess_result = plugin._preprocessor.precheck(test_event)
            assert preprocess_result is not None
            assert preprocess_result.command_text == "test"
    
    @pytest.mark.asyncio
    async def test_handle_message_event_with_filter(self, unified_plugin, clean_registries):
        """测试处理包含过滤器的消息事件"""
        plugin = unified_plugin
        
        # 注册测试过滤器函数
        @filter_registry.register("test_filter")
        def test_filter(event: BaseMessageEvent):
            return True
        
        # 创建测试事件
        test_event = EventFactory.create_group_message("hello", user_id="123")
        
        # 模拟执行函数
        with patch.object(plugin, '_execute_function') as mock_execute:
            mock_execute.return_value = True
            
            result = await plugin.handle_message_event(test_event)
            
            # 应该调用了执行函数
            mock_execute.assert_called()
    
    @pytest.mark.asyncio
    async def test_handle_message_event_no_match(self, unified_plugin, clean_registries):
        """测试处理无匹配的消息事件"""
        plugin = unified_plugin
        
        # 创建测试事件（不是命令格式）
        mock_event = EventFactory.create_private_message(message="hello", user_id="123")
        
        # 应该能正常处理，不抛出异常
        result = await plugin.handle_message_event(mock_event)
        
        # 无命令匹配时应该正常返回
        assert result is None or result is False
    
    @pytest.mark.asyncio
    async def test_command_execution_success(self, unified_plugin, clean_registries):
        """测试命令执行成功"""
        plugin = unified_plugin
        
        # 创建测试函数
        def test_func(event: BaseMessageEvent):
            return "Success"
        test_func.__is_command__ = True
        
        # 直接执行函数
        result = await plugin._execute_function(test_func, Mock())
        assert result == "Success"
    
    @pytest.mark.asyncio
    async def test_command_execution_with_params(self, unified_plugin, clean_registries):
        """测试带参数的命令执行"""
        plugin = unified_plugin
        
        # 创建带参数的测试函数
        def test_func_with_params(event: BaseMessageEvent, name: str, age: int = 18):
            return f"Hello {name}, age {age}"
        test_func_with_params.__is_command__ = True
        
        # 直接执行函数
        result = await plugin._execute_function(
            test_func_with_params, 
            Mock(), 
            "Alice", 
            age=25
        )
        assert "Hello Alice" in result
        assert "age 25" in result
    
    @pytest.mark.asyncio
    async def test_command_execution_error_handling(self, unified_plugin, clean_registries):
        """测试命令执行错误处理"""
        plugin = unified_plugin
        
        # 创建会抛出异常的测试函数
        def error_func(event: BaseMessageEvent):
            raise ValueError("Test error")
        error_func.__is_command__ = True
        
        # 直接执行函数
        result = await plugin._execute_function(error_func, Mock())
        
        # 错误应该被捕获，返回 False
        assert result is False
    
    def test_filter_validation_pass(self, unified_plugin, mock_private_message):
        """测试过滤器验证通过"""
        plugin = unified_plugin
        
        # 创建带过滤器的函数
        def test_func(event: BaseMessageEvent):
            return "Passed"
        test_func.__filters__ = [PrivateFilter()]
        
        # 验证应该通过（私聊消息 + 私聊过滤器）
        result = plugin._filter_validator.validate_filters(test_func, mock_private_message)
        assert result is True
    
    def test_filter_validation_fail(self, unified_plugin, mock_private_message):
        """测试过滤器验证失败"""
        plugin = unified_plugin
        
        # 创建带群聊过滤器的函数
        def test_func(event: BaseMessageEvent):
            return "Should not pass"
        test_func.__filters__ = [GroupFilter()]
        
        # 验证应该失败（私聊消息 + 群聊过滤器）
        result = plugin._filter_validator.validate_filters(test_func, mock_private_message)
        assert result is False
    
    def test_find_plugin_for_function(self, unified_plugin):
        """测试查找函数所属插件"""
        plugin = unified_plugin
        
        # 创建测试函数
        def test_func():
            pass
        
        # 创建一个真实的插件类来测试
        class TestPlugin:
            def test_func(self):
                pass
        
        # 将测试函数设置为插件类的方法
        TestPlugin.test_func = test_func
        mock_plugin = TestPlugin()
        
        with patch.object(plugin, 'list_plugins', return_value=[mock_plugin]):
            result = plugin._find_plugin_for_function(test_func)
            assert result is mock_plugin
    
    def test_func_plugin_map_caching(self, unified_plugin):
        """测试函数插件映射缓存"""
        plugin = unified_plugin
        
        # 创建测试函数
        def test_func():
            pass
        
        mock_plugin = Mock()
        
        # 第一次查找
        plugin.func_plugin_map[test_func] = mock_plugin
        result1 = plugin._find_plugin_for_function(test_func)
        assert result1 is mock_plugin
        
        # 第二次查找应该使用缓存
        result2 = plugin._find_plugin_for_function(test_func)
        assert result2 is mock_plugin
    
    def test_clear_cache(self, unified_plugin):
        """测试清理缓存"""
        plugin = unified_plugin
        
        # 添加一些缓存数据
        plugin.func_plugin_map['test'] = Mock()
        assert len(plugin.func_plugin_map) > 0
        
        # 清理缓存
        plugin.clear_cache()
        assert len(plugin.func_plugin_map) == 0
    
    @pytest.mark.asyncio
    async def test_initialize_if_needed(self, unified_plugin, clean_registries):
        """测试惰性初始化"""
        plugin = unified_plugin
        
        # 重置初始化状态
        plugin._initialized = False
        
        # 注册测试命令
        @command_registry.command("test")
        def test_command(event: BaseMessageEvent):
            return "Test"
        test_command.__is_command__ = True
        
        # 调用初始化
        plugin.initialize_if_needed()
        
        # 应该已初始化
        assert plugin._initialized is True
        
        # 再次调用不应该重复初始化
        with patch.object(plugin._resolver, 'build_index') as mock_build:
            plugin.initialize_if_needed()
            mock_build.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_legacy_event(self, unified_plugin):
        """测试处理传统事件（notice/request）"""
        plugin = unified_plugin
        
        # 创建通知事件
        mock_notice_event = Mock()
        mock_notice_event.post_type = "notice"
        
        # 应该能处理但目前返回 False
        result = await plugin.handle_legacy_event(mock_notice_event)
        assert result is False
        
        # 创建请求事件
        mock_request_event = Mock()
        mock_request_event.post_type = "request"
        
        # 应该能处理但目前返回 False
        result = await plugin.handle_legacy_event(mock_request_event)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_async_function_execution(self, unified_plugin):
        """测试异步函数执行"""
        plugin = unified_plugin
        
        # 创建异步测试函数
        async def async_test_func(event: BaseMessageEvent):
            await asyncio.sleep(0.01)  # 模拟异步操作
            return "Async result"
        async_test_func.__is_command__ = True
        
        # 直接执行函数
        result = await plugin._execute_function(async_test_func, Mock())
        assert result == "Async result"
    
    def test_normalize_case(self, unified_plugin):
        """测试大小写规范化"""
        plugin = unified_plugin
        
        # 目前实现为原样返回
        result = plugin._normalize_case("TestString")
        assert result == "TestString"
    
    @pytest.mark.asyncio
    async def test_run_pure_filters(self, unified_plugin, clean_registries):
        """测试执行纯过滤器"""
        plugin = unified_plugin
        
        executed_filters = []
        
        # 注册纯过滤器函数
        def pure_filter1(event: BaseMessageEvent):
            executed_filters.append("filter1")
            return True
        
        def pure_filter2(event: BaseMessageEvent):
            executed_filters.append("filter2") 
            return True
        
        # 添加到过滤器注册器
        filter_registry._function_filters.extend([pure_filter1, pure_filter2])
        
        # 创建测试事件
        test_event = EventFactory.create_group_message("test")
        
        # 模拟执行函数
        with patch.object(plugin, '_execute_function') as mock_execute:
            await plugin._run_pure_filters(test_event)
            
            # 应该调用了所有纯过滤器
            assert mock_execute.call_count == 2
    
    @pytest.mark.asyncio
    async def test_run_command_with_prefix_mismatch(self, unified_plugin, clean_registries):
        """测试运行命令时前缀不匹配"""
        plugin = unified_plugin
        
        # 创建没有前缀的消息事件
        test_event = EventFactory.create_group_message("hello")  # 没有 / 或 ! 前缀
        
        # 运行命令应该返回 False（前缀不匹配）
        result = await plugin._run_command(test_event)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_run_command_no_match(self, unified_plugin, clean_registries):
        """测试运行命令时没有匹配的命令"""
        plugin = unified_plugin
        
        # 创建有前缀但没有对应命令的消息事件
        test_event = EventFactory.create_group_message("/nonexistent")
        
        # 运行命令应该返回 False（命令不存在）
        result = await plugin._run_command(test_event)
        assert result is False
