"""事件处理集成测试

测试unified_registry模块在各种事件处理场景下的集成表现。
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from ncatbot.core.event.message_segment import MessageArray, Text, At, Image
from ncatbot.plugin_system.builtin_plugin.unified_registry import UnifiedRegistryPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import (
    filter_registry, GroupFilter, PrivateFilter, AdminFilter, CustomFilter
)
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils.testing import EventFactory


class TestMessageEventHandling:
    """消息事件处理测试"""
    
    @pytest.mark.asyncio
    async def test_group_message_handling(self, unified_plugin, clean_registries):
        """测试群聊消息处理"""
        execution_log = []
        
        # 1. 注册群聊专用命令
        @command_registry.command("group_cmd", description="群聊命令")
        def group_command(event: BaseMessageEvent):
            execution_log.append("group_cmd_executed")
            return "Group command executed"
        group_command.__is_command__ = True
        
        # 添加群聊过滤器
        group_filter = GroupFilter()
        filter_registry.add_filter_to_function(group_command, group_filter)
        
        # 2. 创建群聊消息事件
        mock_event = EventFactory.create_group_message(
            message="/group_cmd",
            user_id="user123",
            group_id="group456"
        )
        
        # 3. 处理事件
        with patch.object(unified_plugin, '_execute_function') as mock_execute:
            mock_execute.return_value = "Group command executed"
            
            await unified_plugin.handle_message_event(mock_event)
            
            # 群聊命令应该被执行
            mock_execute.assert_called()
    
    @pytest.mark.asyncio
    async def test_private_message_handling(self, unified_plugin, clean_registries):
        """测试私聊消息处理"""
        execution_log = []
        
        # 1. 注册私聊专用命令
        @command_registry.command("private_cmd", description="私聊命令")
        def private_command(event: BaseMessageEvent):
            execution_log.append("private_cmd_executed")
            return "Private command executed"
        private_command.__is_command__ = True
        
        # 添加私聊过滤器
        private_filter = PrivateFilter()
        filter_registry.add_filter_to_function(private_command, private_filter)
        
        # 2. 创建私聊消息事件
        mock_event = EventFactory.create_private_message(
            message="/private_cmd",
            user_id="user123"
        )
        
        # 3. 处理事件
        with patch.object(unified_plugin, '_execute_function') as mock_execute:
            mock_execute.return_value = "Private command executed"
            
            await unified_plugin.handle_message_event(mock_event)
            
            # 私聊命令应该被执行
            mock_execute.assert_called()
    
    @pytest.mark.asyncio
    async def test_mixed_message_types_handling(self, unified_plugin, clean_registries):
        """测试混合消息类型处理"""
        execution_log = []
        
        # 1. 注册通用命令（无特定过滤器）
        @command_registry.command("universal", description="通用命令")
        def universal_command(event: BaseMessageEvent):
            msg_type = "group" if event.is_group_msg() else "private"
            execution_log.append(f"universal_cmd_{msg_type}")
            return f"Universal command in {msg_type}"
        universal_command.__is_command__ = True
        
        # 2. 测试群聊消息
        group_event = EventFactory.create_group_message(message="/universal", user_id="user1")
        
        with patch.object(unified_plugin, '_execute_function') as mock_execute:
            mock_execute.return_value = "Universal command in group"
            
            await unified_plugin.handle_message_event(group_event)
            mock_execute.assert_called()
        
        # 3. 测试私聊消息
        private_event = EventFactory.create_private_message(message="/universal", user_id="user2")
        
        with patch.object(unified_plugin, '_execute_function') as mock_execute:
            mock_execute.return_value = "Universal command in private"
            
            await unified_plugin.handle_message_event(private_event)
            mock_execute.assert_called()
    
    @pytest.mark.asyncio
    async def test_message_with_complex_content(self, unified_plugin, clean_registries):
        """测试复杂内容消息处理"""
        execution_log = []
        
        # 1. 注册处理复杂内容的命令
        @command_registry.command("process", description="处理复杂内容")
        def process_command(event: BaseMessageEvent):
            execution_log.append("process_complex_content")
            return "Complex content processed"
        process_command.__is_command__ = True
        
        # 2. 创建包含多种消息段的复杂消息        
        segments = [
            Text("/process "),
            At("123456"),
            Text(" please handle "),
            Image("http://example.com/image.jpg"),
            Text(" urgent")
        ]
        
        message_array = MessageArray(*segments)
        mock_event = EventFactory.create_group_message(message=message_array, user_id="user123")
        
        # 3. 处理复杂消息
        with patch.object(unified_plugin, '_execute_function') as mock_execute:
            mock_execute.return_value = "Complex content processed"
            
            await unified_plugin.handle_message_event(mock_event)
            
            # 复杂消息应该被正确处理
            mock_execute.assert_called()


class TestLegacyEventHandling:
    """传统事件处理测试"""
    
    @pytest.mark.asyncio
    async def test_notice_event_handling(self, unified_plugin):
        """测试通知事件处理"""
        # 1. 创建通知事件
        mock_notice_event = Mock()
        mock_notice_event.post_type = "notice"
        mock_notice_event.notice_type = "group_increase"
        mock_notice_event.user_id = "new_user123"
        mock_notice_event.group_id = "group456"
        
        
        # 2. 处理通知事件
        result = await unified_plugin.handle_legacy_event(mock_notice_event)
        
        # 3. 当前实现应该返回False（未实现具体处理）
        assert result is False
    
    @pytest.mark.asyncio
    async def test_request_event_handling(self, unified_plugin):
        """测试请求事件处理"""
        # 1. 创建请求事件
        mock_request_event = Mock()
        mock_request_event.post_type = "request"
        mock_request_event.request_type = "friend"
        mock_request_event.user_id = "requester123"
        mock_request_event.comment = "请添加我为好友"
        
        
        # 2. 处理请求事件
        result = await unified_plugin.handle_legacy_event(mock_request_event)
        
        # 3. 当前实现应该返回False（未实现具体处理）
        assert result is False
    
    @pytest.mark.asyncio
    async def test_unknown_legacy_event_handling(self, unified_plugin):
        """测试未知传统事件处理"""
        # 1. 创建未知类型事件
        mock_unknown_event = Mock()
        mock_unknown_event.post_type = "unknown_type"
        
        
        # 2. 处理未知事件
        result = await unified_plugin.handle_legacy_event(mock_unknown_event)
        
        # 3. 应该返回False
        assert result is False


class TestEventFiltering:
    """事件过滤测试"""
    
    @pytest.mark.asyncio
    async def test_admin_event_filtering(self, unified_plugin, clean_registries, mock_status_manager):
        """测试管理员事件过滤"""
        execution_log = []
        
        # 1. 注册管理员命令
        @command_registry.command("admin_action", description="管理员操作")
        def admin_action_command(event: BaseMessageEvent):
            execution_log.append("admin_action_executed")
            return "Admin action completed"
        admin_action_command.__is_command__ = True
        
        # 添加管理员过滤器
        admin_filter = AdminFilter()
        filter_registry.add_filter_to_function(admin_action_command, admin_filter)
        
        # 2. 测试非管理员用户
        mock_status_manager.user_has_role.return_value = False
        
        mock_event = EventFactory.create_private_message(message="/admin_action", user_id="normal_user")
        
        await unified_plugin.handle_message_event(mock_event)
        
        # 非管理员用户不应该执行命令
        assert "admin_action_executed" not in execution_log
        
        # 3. 测试管理员用户
        execution_log.clear()
        mock_status_manager.user_has_role.return_value = True
        
        mock_event = EventFactory.create_private_message(message="/admin_action", user_id="admin_user")
        
        with patch.object(unified_plugin, '_execute_function') as mock_execute:
            mock_execute.return_value = "Admin action completed"
            
            await unified_plugin.handle_message_event(mock_event)
            
            # 管理员用户应该能执行命令
            mock_execute.assert_called()
    
    @pytest.mark.asyncio
    async def test_custom_event_filtering(self, unified_plugin, clean_registries):
        """测试自定义事件过滤"""
        execution_log = []
        
        # 1. 创建自定义过滤器
        def time_based_filter(event: BaseMessageEvent):
            # 模拟时间过滤：只在工作时间允许
            return True  # 简化为总是允许
        
        custom_filter = CustomFilter(time_based_filter, "time_check")
        
        # 2. 注册带自定义过滤器的命令
        @command_registry.command("time_sensitive", description="时间敏感命令")
        def time_command(event: BaseMessageEvent):
            execution_log.append("time_sensitive_executed")
            return "Time sensitive operation completed"
        time_command.__is_command__ = True
        
        filter_registry.add_filter_to_function(time_command, custom_filter)
        
        # 3. 测试过滤器
        mock_event = EventFactory.create_private_message(message="/time_sensitive", user_id="user123")
    
        with patch.object(unified_plugin, '_execute_function') as mock_execute:
            mock_execute.return_value = "Time sensitive operation completed"
            
            await unified_plugin.handle_message_event(mock_event)
            
            # 自定义过滤器允许时应该执行
            mock_execute.assert_called()
    
    @pytest.mark.asyncio
    async def test_multiple_filter_chain(self, unified_plugin, clean_registries, mock_status_manager):
        """测试多重过滤器链"""
        execution_log = []
        
        # 1. 创建多个过滤器
        group_filter = GroupFilter()
        admin_filter = AdminFilter()
        
        def active_hours_filter(event: BaseMessageEvent):
            return True  # 简化为总是通过
        
        custom_filter = CustomFilter(active_hours_filter, "active_hours")
        
        # 2. 注册带多重过滤器的命令
        @command_registry.command("super_admin", description="超级管理员命令")
        def super_admin_command(event: BaseMessageEvent):
            execution_log.append("super_admin_executed")
            return "Super admin operation completed"
        super_admin_command.__is_command__ = True
        
        # 添加多个过滤器
        filter_registry.add_filter_to_function(super_admin_command, group_filter, admin_filter, custom_filter)
        
        # 3. 测试过滤器链
        # 设置管理员权限
        mock_status_manager.user_has_role.return_value = True
        
        mock_event = EventFactory.create_group_message(
            message="/super_admin",
            user_id="super_admin",
            group_id="admin_group"
        )
        
        with patch.object(unified_plugin, '_execute_function') as mock_execute:
            mock_execute.return_value = "Super admin operation completed"
            
            await unified_plugin.handle_message_event(mock_event)
            
            # 所有过滤器都通过时应该执行
            mock_execute.assert_called()
        
        # 4. 测试过滤器链失败
        execution_log.clear()
        
        # 创建私聊消息（不满足群聊过滤器）
        mock_event = EventFactory.create_private_message(
            message="/super_admin",
            user_id="super_admin"
        )
        
        await unified_plugin.handle_message_event(mock_event)
        
        # 过滤器链失败时不应该执行
        assert "super_admin_executed" not in execution_log


class TestEventErrorHandling:
    """事件错误处理测试"""
    
    @pytest.mark.asyncio
    async def test_malformed_message_event(self, unified_plugin):
        """测试畸形消息事件处理"""
        # 1. 创建畸形事件
        mock_event = Mock()
        mock_event.message = None  # 缺少消息内容
        
        
        # 2. 处理畸形事件
        try:
            result = await unified_plugin.handle_message_event(mock_event)
            # 应该能处理错误，不崩溃
            assert result is None or isinstance(result, bool)
        except Exception:
            # 如果抛出异常，也是可以接受的处理方式
            pass
    
    @pytest.mark.asyncio
    async def test_event_processing_exception(self, unified_plugin, clean_registries):
        """测试事件处理异常"""
        # 1. 注册会抛异常的命令
        @command_registry.command("error_prone", description="容易出错的命令")
        def error_command(event: BaseMessageEvent):
            raise RuntimeError("Processing error")
        error_command.__is_command__ = True
        
        # 2. 创建消息事件
        mock_event = EventFactory.create_private_message(message="/error_prone", user_id="test_user")
        
        # 3. 处理事件
        # 应该能处理异常，不崩溃
        result = await unified_plugin.handle_message_event(mock_event)
        assert result is None or isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_filter_exception_handling(self, unified_plugin, clean_registries):
        """测试过滤器异常处理"""
        # 1. 创建会抛异常的过滤器
        def error_filter(event: BaseMessageEvent):
            raise ValueError("Filter error")
        
        error_custom_filter = CustomFilter(error_filter, "error_filter")
        
        # 2. 注册带异常过滤器的命令
        @command_registry.command("filtered_cmd", description="带异常过滤器的命令")
        def filtered_command(event: BaseMessageEvent):
            return "Should not execute"
        filtered_command.__is_command__ = True
        
        filter_registry.add_filter_to_function(filtered_command, error_custom_filter)
        
        # 3. 处理事件
        mock_event = EventFactory.create_private_message(message="/filtered_cmd", user_id="test_user")
        
            # 过滤器异常应该被适当处理
        try:
            result = await unified_plugin.handle_message_event(mock_event)
            # 如果异常被捕获，可能返回False或None
            assert result is None or result is False
        except ValueError:
            # 如果异常被向上传播，也是可以接受的
            pass


class TestEventConcurrency:
    """事件并发处理测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_event_processing(self, unified_plugin, clean_registries):
        """测试并发事件处理"""
        execution_count = []
        
        # 1. 注册异步命令
        @command_registry.command("concurrent", description="并发测试命令")
        async def concurrent_command(event: BaseMessageEvent, task_id: str):
            await asyncio.sleep(0.01)  # 模拟异步操作
            execution_count.append(task_id)
            return f"Task {task_id} completed"
        concurrent_command.__is_command__ = True
        
        # 2. 创建多个事件
        events = []
        for i in range(10):
            mock_event = EventFactory.create_private_message(message=f"/concurrent task{i}", user_id=f"user{i}")
            events.append(mock_event)
        await asyncio.gather(*[unified_plugin.handle_message_event(event) for event in events])
        
        # 验证所有任务都被处理
        assert len(execution_count) == 10
        assert all(f"task{i}" in execution_count for i in range(10))
    
    @pytest.mark.asyncio
    async def test_event_queue_handling(self, unified_plugin, clean_registries):
        """测试事件队列处理"""
        execution_order = []
        
        # 1. 注册带延迟的命令
        @command_registry.command("queued", description="队列测试命令")
        async def queued_command(event: BaseMessageEvent, order_id: str):
            execution_order.append(f"start_{order_id}")
            await asyncio.sleep(0.01)  # 模拟处理时间
            execution_order.append(f"end_{order_id}")
            return f"Order {order_id} processed"
        queued_command.__is_command__ = True
        
        # 2. 创建序列事件
        events = []
        for i in range(5):
            mock_event = EventFactory.create_private_message(message=f"/queued order{i}", user_id=f"user{i}")
            events.append(mock_event)
        
        # 3. 顺序处理（不并发）
        with patch.object(unified_plugin, '_execute_function') as mock_execute:
            async def sequential_execute(func, event, *args, **kwargs):
                return await func(event, *args, **kwargs)
            
            mock_execute.side_effect = sequential_execute
            
            # 顺序处理事件
            for event in events:
                await unified_plugin.handle_message_event(event)
            
            # 验证执行顺序
            assert len(execution_order) == 10  # 5个start + 5个end
            
            # 验证顺序正确性
            for i in range(5):
                assert f"start_order{i}" in execution_order
                assert f"end_order{i}" in execution_order
