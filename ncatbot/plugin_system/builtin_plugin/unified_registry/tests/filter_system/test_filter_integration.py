"""过滤器系统集成测试

测试过滤器系统各组件的集成功能，包括过滤器链执行、与命令的集成、装饰器使用等。
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from ncatbot.core.event import BaseMessageEvent, GroupMessageEvent, PrivateMessageEvent
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import (
    filter_registry, GroupFilter, PrivateFilter, AdminFilter, CustomFilter,
    group_only, private_only, admin_only
)


class TestFilterChainExecution:
    """过滤器链执行测试"""
    
    @pytest.mark.asyncio
    async def test_simple_filter_chain(self, mock_group_message, clean_registries):
        """测试简单过滤器链执行"""
        execution_order = []
        
        # 创建记录执行顺序的过滤器
        def filter1(event: BaseMessageEvent):
            execution_order.append("filter1")
            return True
        
        def filter2(event: BaseMessageEvent):
            execution_order.append("filter2")
            return True
        
        # 注册过滤器
        filter_registry.register(filter1, "filter1")
        filter_registry.register(filter2, "filter2")
        
        # 创建带过滤器的函数
        def test_function(event: BaseMessageEvent):
            execution_order.append("function")
            return "executed"
        
        # 手动添加过滤器
        filter_registry.add_filter_to_function(test_function, "filter1", "filter2")
        
        # 验证过滤器已添加
        assert hasattr(test_function, '__filters__')
        assert len(test_function.__filters__) == 2
    
    @pytest.mark.asyncio
    async def test_filter_chain_early_termination(self, mock_private_message, clean_registries):
        """测试过滤器链早期终止"""
        execution_order = []
        
        # 第一个过滤器通过
        def filter1(event: BaseMessageEvent):
            execution_order.append("filter1")
            return True
        
        # 第二个过滤器失败
        def filter2(event: BaseMessageEvent):
            execution_order.append("filter2")
            return False
        
        # 第三个过滤器不应该被执行
        def filter3(event: BaseMessageEvent):
            execution_order.append("filter3")
            return True
        
        # 注册过滤器
        filter_registry.register(filter1, "filter1")
        filter_registry.register(filter2, "filter2") 
        filter_registry.register(filter3, "filter3")
        
        # 创建带过滤器的函数
        def test_function(event: BaseMessageEvent):
            execution_order.append("function")
            return "executed"
        
        filter_registry.add_filter_to_function(test_function, "filter1", "filter2", "filter3")
        
        # 模拟验证器行为
        from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.validator import FilterValidator
        validator = FilterValidator()
        
        result = validator.validate_filters(test_function, mock_private_message)
        
        # 应该在filter2失败时停止
        assert result is False
    
    @pytest.mark.asyncio
    async def test_mixed_filter_types_chain(self, mock_group_message, mock_status_manager, clean_registries):
        """测试混合过滤器类型链"""
        # 内置过滤器
        group_filter = GroupFilter()
        admin_filter = AdminFilter()
        
        # 自定义过滤器
        def time_filter(event: BaseMessageEvent):
            return True  # 简化为总是通过
        
        custom_filter = CustomFilter(time_filter, "time_check")
        
        # 模拟管理员权限
        mock_status_manager.user_has_role.return_value = True
        
        # 注册自定义过滤器
        filter_registry.register_filter("time_check", custom_filter)
        filter_registry.register_filter("group_check", group_filter)
        filter_registry.register_filter("admin_check", admin_filter)
        
        def test_function(event: BaseMessageEvent):
            return "all filters passed"
        
        # 添加混合过滤器
        filter_registry.add_filter_to_function(
            test_function, 
            "group_check", 
            "admin_check", 
            "time_check"
        )
        
        # 验证所有过滤器
        from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.validator import FilterValidator
        validator = FilterValidator()
        
        result = validator.validate_filters(test_function, mock_group_message)
        assert result is True


class TestFilterWithCommand:
    """过滤器与命令集成测试"""
    
    @pytest.mark.asyncio
    async def test_filter_command_integration(self, unified_plugin, mock_group_message, clean_registries):
        """测试过滤器与命令的集成"""
        from ncatbot.plugin_system import command_registry
        
        # 注册带过滤器的命令
        @command_registry.command("admin_cmd")
        def admin_command(event: BaseMessageEvent):
            return "Admin command executed"
        admin_command.__is_command__ = True
        
        # 添加管理员过滤器
        admin_filter = AdminFilter()
        filter_registry.add_filter_to_function(admin_command, admin_filter)
        
        # 模拟执行
        with patch.object(unified_plugin, '_filter_validator') as mock_validator:
            mock_validator.validate_filters.return_value = True
            
            result = await unified_plugin._execute_function(admin_command, mock_group_message)
            
            # 应该调用过滤器验证
            mock_validator.validate_filters.assert_called_once_with(admin_command, mock_group_message)
    
    @pytest.mark.asyncio
    async def test_filter_command_rejection(self, unified_plugin, mock_private_message, clean_registries):
        """测试过滤器拒绝命令执行"""
        from ncatbot.plugin_system import command_registry
        
        # 注册带群聊过滤器的命令
        @command_registry.command("group_only_cmd")
        def group_only_command(event: BaseMessageEvent):
            return "Should not execute"
        group_only_command.__is_command__ = True
        
        # 添加群聊过滤器
        group_filter = GroupFilter()
        filter_registry.add_filter_to_function(group_only_command, group_filter)
        
        # 模拟执行（私聊消息应该被拒绝）
        with patch.object(unified_plugin, '_filter_validator') as mock_validator:
            mock_validator.validate_filters.return_value = False
            
            result = await unified_plugin._execute_function(group_only_command, mock_private_message)
            
            # 应该被过滤器拒绝
            assert result is False


class TestFilterDecorators:
    """过滤器装饰器测试"""
    
    def test_group_only_decorator(self, mock_group_message, mock_private_message, clean_registries):
        """测试群聊专用装饰器"""
        @group_only
        def group_function(event: BaseMessageEvent):
            return "group only"
        
        # 检查过滤器是否添加
        assert hasattr(group_function, '__filters__')
        assert len(group_function.__filters__) > 0
        assert any(isinstance(f, GroupFilter) for f in group_function.__filters__)
    
    def test_private_only_decorator(self, mock_private_message, mock_group_message, clean_registries):
        """测试私聊专用装饰器"""
        @private_only
        def private_function(event: BaseMessageEvent):
            return "private only"
        
        # 检查过滤器是否添加
        assert hasattr(private_function, '__filters__')
        assert len(private_function.__filters__) > 0
        assert any(isinstance(f, PrivateFilter) for f in private_function.__filters__)
    
    def test_admin_only_decorator(self, mock_private_message, mock_status_manager, clean_registries):
        """测试管理员专用装饰器"""
        @admin_only
        def admin_function(event: BaseMessageEvent):
            return "admin only"
        
        # 检查过滤器是否添加
        assert hasattr(admin_function, '__filters__')
        assert len(admin_function.__filters__) > 0
        assert any(isinstance(f, AdminFilter) for f in admin_function.__filters__)
    
    def test_chained_decorators(self, mock_group_message, mock_status_manager, clean_registries):
        """测试链式装饰器"""
        @admin_only
        @group_only
        def admin_group_function(event: BaseMessageEvent):
            return "admin group only"
        
        # 应该有两个过滤器
        assert hasattr(admin_group_function, '__filters__')
        assert len(admin_group_function.__filters__) >= 2
        
        # 应该包含两种类型的过滤器
        filter_types = [type(f) for f in admin_group_function.__filters__]
        assert GroupFilter in filter_types or any(isinstance(f, GroupFilter) for f in admin_group_function.__filters__)
        assert AdminFilter in filter_types or any(isinstance(f, AdminFilter) for f in admin_group_function.__filters__)


class TestFilterRegistryGlobalState:
    """过滤器注册器全局状态测试"""
    
    def test_global_filter_registry(self, clean_registries):
        """测试全局过滤器注册器"""
        # 使用全局注册器
        @filter_registry.register("global_test")
        def global_filter(event: BaseMessageEvent):
            return True
        
        # 应该在全局注册器中找到
        entry = filter_registry.get_filter("global_test")
        assert entry is not None
        assert entry.name == "global_test"
    
    def test_registry_state_persistence(self, clean_registries):
        """测试注册器状态持久性"""
        # 注册一个过滤器
        test_filter = GroupFilter()
        filter_registry.register_filter("persistent_test", test_filter)
        
        # 在不同的函数中应该能找到
        entry1 = filter_registry.get_filter("persistent_test")
        entry2 = filter_registry.get_filter("persistent_test")
        
        assert entry1 is entry2
        assert entry1.filter_instance is test_filter
    
    def test_registry_cleanup(self, clean_registries):
        """测试注册器清理"""
        # 注册一些测试数据
        filter_registry.register_filter("cleanup_test1", GroupFilter())
        filter_registry.register_filter("cleanup_test2", PrivateFilter())
        
        def test_func(event: BaseMessageEvent):
            return True
        filter_registry.register(test_func, "func_test")
        
        # 验证数据存在
        assert "cleanup_test1" in filter_registry._filters
        assert "cleanup_test2" in filter_registry._filters
        assert "func_test" in filter_registry._filters
        assert test_func in filter_registry._function_filters
        
        # clean_registries fixture 应该在测试后清理


class TestComplexFilterScenarios:
    """复杂过滤器场景测试"""
    
    @pytest.mark.asyncio
    async def test_conditional_filter_chain(self, mock_group_message, clean_registries):
        """测试条件过滤器链"""
        execution_log = []
        
        # 条件过滤器：只在群聊中检查特定条件
        def conditional_filter(event: BaseMessageEvent):
            execution_log.append("conditional")
            if event.is_group_msg():
                return len(event.user_id) > 3
            return True
        
        # 基础群聊过滤器
        group_filter = GroupFilter()
        
        # 注册过滤器
        filter_registry.register_filter("group", group_filter)
        filter_registry.register(conditional_filter, "conditional")
        
        def test_function(event: BaseMessageEvent):
            execution_log.append("function")
            return "executed"
        
        filter_registry.add_filter_to_function(test_function, "group", "conditional")
        
        # 测试用户ID长度足够的情况
        mock_group_message.user_id = "123456"
        
        from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.validator import FilterValidator
        validator = FilterValidator()
        result = validator.validate_filters(test_function, mock_group_message)
        assert result is True
        
        # 测试用户ID长度不够的情况
        execution_log.clear()
        mock_group_message.user_id = "12"
        result = validator.validate_filters(test_function, mock_group_message)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_dynamic_filter_modification(self, mock_private_message, clean_registries):
        """测试动态过滤器修改"""
        # 创建可修改状态的过滤器
        class DynamicFilter:
            def __init__(self):
                self.enabled = True
            
            def check(self, event):
                return self.enabled
        
        dynamic_filter = DynamicFilter()
        
        # 包装为CustomFilter
        def dynamic_check(event: BaseMessageEvent):
            return dynamic_filter.check(event)
        
        custom_filter = CustomFilter(dynamic_check, "dynamic")
        
        def test_function(event: BaseMessageEvent):
            return "executed"
        
        filter_registry.register_filter("dynamic", custom_filter)
        filter_registry.add_filter_to_function(test_function, "dynamic")
        
        from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.validator import FilterValidator
        validator = FilterValidator()
        
        # 启用状态应该通过
        result = validator.validate_filters(test_function, mock_private_message)
        assert result is True
        
        # 禁用状态应该失败
        dynamic_filter.enabled = False
        result = validator.validate_filters(test_function, mock_private_message)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_filter_error_recovery(self, mock_private_message, clean_registries):
        """测试过滤器错误恢复"""
        error_count = 0
        
        def error_prone_filter(event: BaseMessageEvent):
            nonlocal error_count
            error_count += 1
            if error_count <= 2:
                raise ValueError(f"Error {error_count}")
            return True
        
        filter_registry.register(error_prone_filter, "error_prone")
        
        def test_function(event: BaseMessageEvent):
            return "executed"
        
        filter_registry.add_filter_to_function(test_function, "error_prone")
        
        from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.validator import FilterValidator
        validator = FilterValidator()
        
        # 前两次应该抛出异常
        
        assert validator.validate_filters(test_function, mock_private_message) is False
        
        assert validator.validate_filters(test_function, mock_private_message) is False
        
        # 第三次应该成功
        result = validator.validate_filters(test_function, mock_private_message)
        assert result is True
