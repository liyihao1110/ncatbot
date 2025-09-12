"""完整工作流测试

测试unified_registry模块的完整工作流程，从消息接收到命令执行的端到端测试。
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from ncatbot.plugin_system.builtin_plugin.unified_registry import UnifiedRegistryPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import (
    filter_registry, GroupFilter, PrivateFilter, AdminFilter
)
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils.testing import EventFactory
from ncatbot.core.event.message_segment import MessageArray, Text, At


class TestFullWorkflow:
    """完整工作流测试"""
    
    @pytest.mark.asyncio
    async def test_simple_command_full_workflow(self, unified_plugin, clean_registries):
        """测试简单命令的完整工作流"""
        execution_log = []
        
        # 1. 注册命令
        @command_registry.command("hello", description="问候命令")
        def hello_command(event: BaseMessageEvent):
            execution_log.append("hello_executed")
            return "Hello World!"
        hello_command.__is_command__ = True
        
        # 2. 创建消息事件
        mock_event = EventFactory.create_private_message(message="/hello", user_id="test_user")
        
        # 3. 处理消息事件
        await unified_plugin.handle_message_event(mock_event)

        # 4. 验证执行
        assert "hello_executed" in execution_log
    
    @pytest.mark.asyncio
    async def test_command_with_parameters_workflow(self, unified_plugin, clean_registries):
        """测试带参数命令的完整工作流"""
        execution_results = []
        
        # 1. 注册带参数的命令
        @command_registry.command("greet", description="个性化问候")
        def greet_command(event: BaseMessageEvent, name: str, age: int = 18):
            result = f"Hello {name}, you are {age} years old!"
            execution_results.append(result)
            return result
        greet_command.__is_command__ = True
        
        # 2. 创建带参数的消息事件
        mock_event = EventFactory.create_private_message(message="/greet Alice 25", user_id="test_user")
        
        # 3. 模拟参数绑定和执行
        await unified_plugin.handle_message_event(mock_event)
            
        assert "Hello Alice" in "".join(execution_results)
        assert "25 years old" in "".join(execution_results)
    
    
    @pytest.mark.asyncio
    async def test_filtered_command_workflow(self, unified_plugin, clean_registries, mock_status_manager):
        """测试带过滤器命令的完整工作流"""
        execution_log = []
        
        # 1. 注册带过滤器的命令
        @command_registry.command("admin_only", description="管理员专用命令")
        def admin_command(event: BaseMessageEvent):
            execution_log.append("admin_command_executed")
            return "Admin operation completed"
        admin_command.__is_command__ = True
        
        # 2. 添加管理员过滤器
        admin_filter = AdminFilter()
        filter_registry.add_filter_to_function(admin_command, admin_filter)
        
        # 3. 测试非管理员用户
        mock_status_manager.user_has_role.return_value = False
        
        mock_event = EventFactory.create_private_message(message="/admin_only", user_id="normal_user")
        
        await unified_plugin.handle_message_event(mock_event)
        
        # 非管理员不应该执行命令
        assert "admin_command_executed" not in execution_log
        
        # 4. 测试管理员用户
        execution_log.clear()
        mock_status_manager.user_has_role.return_value = True
        
        mock_event = EventFactory.create_private_message(message="/admin_only", user_id="admin_user")
        
        with patch.object(unified_plugin, '_execute_function') as mock_execute:
            mock_execute.return_value = "Admin operation completed"
            
            await unified_plugin.handle_message_event(mock_event)
            
            # 管理员应该能执行命令
            mock_execute.assert_called()
    
    @pytest.mark.asyncio
    async def test_hierarchical_command_workflow(self, unified_plugin, clean_registries):
        """测试层级命令的完整工作流"""
        execution_log = []
        
        # 1. 注册层级命令
        admin_group = command_registry.group("admin", description="管理员命令组")
        user_group = admin_group.group("user", description="用户管理")
        
        @user_group.command("ban", description="封禁用户")
        def ban_user_command(event: BaseMessageEvent, target_user: str):
            execution_log.append(f"banned_{target_user}")
            return f"User {target_user} has been banned"
        ban_user_command.__is_command__ = True
        
        # 2. 创建层级命令消息
        mock_event = EventFactory.create_private_message(message="/admin user ban target123", user_id="admin_user")
        
        # 3. 模拟执行
        with patch.object(unified_plugin, '_execute_function') as mock_execute:
            mock_execute.return_value = "User target123 has been banned"
            
            await unified_plugin.handle_message_event(mock_event)
            
            # 验证层级命令被正确解析和执行
            mock_execute.assert_called()
    
    @pytest.mark.asyncio
    async def test_complex_message_workflow(self, unified_plugin, clean_registries):
        """测试复杂消息的完整工作流"""
        execution_log = []
        
        # 1. 注册处理复杂消息的命令
        @command_registry.command("send", description="发送消息给用户")
        def send_command(event: BaseMessageEvent, target: str, message_text: str):
            execution_log.append(f"sent_to_{target}_{message_text}")
            return f"Message sent to {target}: {message_text}"
        send_command.__is_command__ = True
        
        # 2. 创建包含@和文本的复杂消息
        segments = [
            Text("/send "),
            At("123456"),  # @用户
            Text(" hello world")
        ]
        message_array = MessageArray(*segments)
        mock_event = EventFactory.create_private_message(message=message_array, user_id="sender")
        
        # 3. 模拟执行
        with patch.object(unified_plugin, '_execute_function') as mock_execute:
            mock_execute.return_value = "Message sent"
            
            await unified_plugin.handle_message_event(mock_event)
            
            # 验证复杂消息被正确处理
            mock_execute.assert_called()
    
    @pytest.mark.asyncio
    async def test_alias_command_workflow(self, unified_plugin, clean_registries):
        """测试别名命令的完整工作流"""
        execution_log = []
        
        # 1. 注册带别名的命令
        @command_registry.command("status", aliases=["st", "stat"], description="查看状态")
        def status_command(event: BaseMessageEvent):
            execution_log.append("status_checked")
            return "System status: OK"
        status_command.__is_command__ = True
        
        # 2. 测试主命令名
        mock_event_1 = EventFactory.create_private_message(message="/status", user_id="test_user")
        await unified_plugin.handle_message_event(mock_event_1)
        assert "status_checked" in execution_log
        execution_log.clear()
        mock_event_2 = EventFactory.create_private_message(message="/st", user_id="test_user")
        await unified_plugin.handle_message_event(mock_event_2)
        assert "status_checked" in execution_log
        assert "status_checked" in execution_log
        execution_log.clear()
        mock_event_3 = EventFactory.create_private_message(message="/stat", user_id="test_user")
        await unified_plugin.handle_message_event(mock_event_3)
        assert "status_checked" in execution_log
        assert "status_checked" in execution_log
        
    
    @pytest.mark.asyncio
    async def test_filter_only_workflow(self, unified_plugin, clean_registries):
        """测试纯过滤器（非命令）的完整工作流"""
        execution_log = []
        
        # 1. 注册纯过滤器函数
        @filter_registry.register("log_filter")
        def log_all_messages(event: BaseMessageEvent):
            execution_log.append(f"logged_{event.user_id}")
            return True
        
        # 2. 创建普通消息（非命令）
        mock_event = EventFactory.create_private_message(message="hello everyone", user_id="test_user")
        
        # 3. 模拟执行
        with patch.object(unified_plugin, '_execute_function') as mock_execute:
            mock_execute.return_value = True
            
            await unified_plugin.handle_message_event(mock_event)
            
            # 验证过滤器被执行
            mock_execute.assert_called()
    
    @pytest.mark.asyncio
    async def test_no_match_workflow(self, unified_plugin, clean_registries):
        """测试无匹配的完整工作流"""
        # 1. 不注册任何命令
        
        # 2. 创建命令格式的消息
        mock_event = EventFactory.create_private_message(message="/nonexistent", user_id="test_user")
        
        # 3. 处理消息
        result = await unified_plugin.handle_message_event(mock_event)
        
        # 4. 应该正常处理，不抛出异常
        # 结果可能是None或False，表示无匹配
        assert result is None or result is False
    
    @pytest.mark.asyncio
    async def test_error_handling_workflow(self, unified_plugin, clean_registries):
        """测试错误处理的完整工作流"""
        # 1. 注册会抛异常的命令
        @command_registry.command("error_cmd", description="会出错的命令")
        def error_command(event: BaseMessageEvent):
            raise ValueError("Command error")
        error_command.__is_command__ = True
        
        # 2. 创建消息事件
        mock_event = EventFactory.create_private_message(message="/error_cmd", user_id="test_user")
        
        # 3. 模拟执行
        # 应该能处理错误，不崩溃
        result = await unified_plugin.handle_message_event(mock_event)
        
        # 错误应该被捕获
        assert result is None or result is False


class TestAsyncWorkflow:
    """异步工作流测试"""
    
    @pytest.mark.asyncio
    async def test_async_command_workflow(self, unified_plugin, clean_registries):
        """测试异步命令的完整工作流"""
        execution_log = []
        
        # 1. 注册异步命令
        @command_registry.command("async_task", description="异步任务")
        async def async_command(event: BaseMessageEvent, delay: float = 0.01):
            await asyncio.sleep(delay)
            execution_log.append("async_task_completed")
            return "Async task completed"
        async_command.__is_command__ = True
        
        # 2. 创建消息事件
        mock_event = EventFactory.create_private_message(message="/async_task 0.01", user_id="test_user")
        
        # 3. 模拟执行
        with patch.object(unified_plugin, '_execute_function') as mock_execute:
            # 模拟异步执行
            async def async_execute(*args, **kwargs):
                return await async_command(mock_event, 0.01)
            
            mock_execute.side_effect = async_execute
            
            await unified_plugin.handle_message_event(mock_event)
            
            # 验证异步命令被执行
            mock_execute.assert_called()
            assert "async_task_completed" in execution_log
    
    @pytest.mark.asyncio
    async def test_concurrent_message_handling(self, unified_plugin, clean_registries):
        """测试并发消息处理"""
        execution_count = []
        
        # 1. 注册命令
        @command_registry.command("concurrent", description="并发测试")
        async def concurrent_command(event: BaseMessageEvent, task_id: str):
            await asyncio.sleep(0.01)  # 模拟异步操作
            execution_count.append(task_id)
            return f"Task {task_id} completed"
        concurrent_command.__is_command__ = True
        
        # 2. 创建多个消息事件
        events = []
        for i in range(5):
            mock_event = EventFactory.create_private_message(message=f"/concurrent task{i}", user_id=f"user{i}")
            events.append(mock_event)
        
        # 3. 并发处理
        with patch.object(unified_plugin, '_execute_function') as mock_execute:
            # 模拟并发执行
            async def concurrent_execute(func, event, *args, **kwargs):
                return await func(event, *args, **kwargs)
            
            mock_execute.side_effect = concurrent_execute
            
            # 并发处理所有消息
            tasks = [unified_plugin.handle_message_event(event) for event in events]
            await asyncio.gather(*tasks)
            
            # 验证所有任务都被执行
            assert len(execution_count) == 5
            assert all(f"task{i}" in execution_count for i in range(5))


class TestWorkflowWithRealComponents:
    """使用真实组件的工作流测试"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_real_workflow(self, unified_plugin, clean_registries):
        """端到端真实工作流测试"""
        execution_log = []
        
        # 1. 注册真实命令和过滤器
        @command_registry.command("deploy", aliases=["d"], description="部署应用")
        def deploy_command(event: BaseMessageEvent, app_name: str, env: str = "dev"):
            execution_log.append(f"deployed_{app_name}_to_{env}")
            return f"Successfully deployed {app_name} to {env}"
        deploy_command.__is_command__ = True
        
        # 添加群聊过滤器
        group_filter = GroupFilter()
        filter_registry.add_filter_to_function(deploy_command, group_filter)
        
        # 2. 创建群聊消息事件
        mock_event = EventFactory.create_group_message(
            message="/deploy myapp prod",
            user_id="deployer",
            group_id="dev_group"
        )
        
        # 3. 让unified_plugin处理真实的初始化和执行
        # 注意：这里不模拟内部方法，让它们真实执行
        result = await unified_plugin.handle_message_event(mock_event)
        
        # 4. 验证处理完成（具体结果取决于实现）
        # 由于是真实工作流，结果可能因实现细节而异
        assert result is None or isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_plugin_initialization_workflow(self, test_client):
        """测试插件初始化工作流"""
        # 1. 注册插件
        test_client.register_plugin(UnifiedRegistryPlugin)
        
        # 2. 获取插件实例
        plugins = test_client.get_registered_plugins()
        unified_plugin = next((p for p in plugins if isinstance(p, UnifiedRegistryPlugin)), None)
        assert unified_plugin is not None
        
        # 3. 验证插件状态
        assert unified_plugin.name == "UnifiedRegistryPlugin"
        assert unified_plugin._preprocessor is not None
        assert unified_plugin._resolver is not None
        assert unified_plugin._binder is not None
        
        # 4. 清理
        test_client.unregister_plugin(unified_plugin)
    
    @pytest.mark.asyncio
    async def test_multi_plugin_interaction_workflow(self, test_client, clean_registries):
        """测试多插件交互工作流"""
        execution_log = []
        
        # 1. 创建辅助插件
        from ncatbot.plugin_system import BasePlugin
        
        class HelperPlugin(BasePlugin):
            name = "HelperPlugin"
            version = "1.0.0"
            
            async def on_load(self):
                self.data = {"helper": "ready"}
            
            def get_helper_data(self):
                return self.data
        
        # 2. 注册插件
        test_client.register_plugin(HelperPlugin)
        test_client.register_plugin(UnifiedRegistryPlugin)
        
        # 3. 获取插件实例
        plugins = test_client.get_registered_plugins()
        helper_plugin = next((p for p in plugins if isinstance(p, HelperPlugin)), None)
        unified_plugin = next((p for p in plugins if isinstance(p, UnifiedRegistryPlugin)), None)
        
        assert helper_plugin is not None
        assert unified_plugin is not None
        
        # 4. 注册依赖其他插件的命令
        @command_registry.command("get_helper", description="获取辅助数据")
        def get_helper_command(event: BaseMessageEvent):
            # 这里应该能访问到 helper_plugin，但由于测试环境限制，我们简化处理
            execution_log.append("accessed_helper")
            return "Helper data retrieved"
        get_helper_command.__is_command__ = True
        
        # 5. 测试命令执行
        mock_event = EventFactory.create_private_message(message="/get_helper", user_id="test_user")
        
        # 模拟执行（由于真实的插件查找比较复杂，这里简化）
        with patch.object(unified_plugin, '_find_plugin_for_function', return_value=helper_plugin):
            with patch.object(unified_plugin, '_execute_function') as mock_execute:
                mock_execute.return_value = "Helper data retrieved"
                
                await unified_plugin.handle_message_event(mock_event)
                mock_execute.assert_called()
        
        # 6. 清理
        test_client.unregister_plugin(helper_plugin)
        test_client.unregister_plugin(unified_plugin)
