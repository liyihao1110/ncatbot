"""过滤器验证器测试

测试过滤器验证器的功能，包括单个过滤器验证、多重过滤器链验证等。
"""

import pytest
from unittest.mock import Mock

from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.validator import FilterValidator
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.builtin import (
    GroupFilter, PrivateFilter, AdminFilter, RootFilter, CustomFilter
)


class TestFilterValidator:
    """过滤器验证器核心功能测试"""
    
    def test_validator_creation(self):
        """测试验证器创建"""
        validator = FilterValidator()
        assert validator is not None
    
    def test_validate_filters_no_filters(self, mock_private_message):
        """测试验证没有过滤器的函数"""
        validator = FilterValidator()
        
        def test_func(event):
            return "test"
        
        # 没有__filters__属性的函数应该通过验证
        result = validator.validate_filters(test_func, mock_private_message)
        assert result is True
    
    def test_validate_filters_empty_filters(self, mock_private_message):
        """测试验证空过滤器列表的函数"""
        validator = FilterValidator()
        
        def test_func(event):
            return "test"
        test_func.__filters__ = []
        
        # 空过滤器列表应该通过验证
        result = validator.validate_filters(test_func, mock_private_message)
        assert result is True
    
    def test_validate_single_filter_pass(self, mock_group_message):
        """测试单个过滤器验证通过"""
        validator = FilterValidator()
        group_filter = GroupFilter()
        
        def test_func(event):
            return "test"
        test_func.__filters__ = [group_filter]
        
        # 群聊消息应该通过群聊过滤器
        result = validator.validate_filters(test_func, mock_group_message)
        assert result is True
    
    def test_validate_single_filter_fail(self, mock_private_message):
        """测试单个过滤器验证失败"""
        validator = FilterValidator()
        group_filter = GroupFilter()
        
        def test_func(event):
            return "test"
        test_func.__filters__ = [group_filter]
        
        # 私聊消息不应该通过群聊过滤器
        result = validator.validate_filters(test_func, mock_private_message)
        assert result is False
    
    def test_validate_multiple_filters_all_pass(self, mock_group_message, mock_status_manager):
        """测试多重过滤器全部通过"""
        validator = FilterValidator()
        group_filter = GroupFilter()
        admin_filter = AdminFilter()
        
        # 模拟管理员权限
        mock_status_manager.user_has_role.return_value = True
        
        def test_func(event):
            return "test"
        test_func.__filters__ = [group_filter, admin_filter]
        
        # 群聊消息且有管理员权限应该通过
        result = validator.validate_filters(test_func, mock_group_message)
        assert result is True
    
    def test_validate_multiple_filters_partial_fail(self, mock_private_message, mock_status_manager):
        """测试多重过滤器部分失败"""
        validator = FilterValidator()
        group_filter = GroupFilter()
        admin_filter = AdminFilter()
        
        # 模拟管理员权限
        mock_status_manager.user_has_role.return_value = True
        
        def test_func(event):
            return "test"
        test_func.__filters__ = [group_filter, admin_filter]
        
        # 私聊消息虽然有管理员权限，但不通过群聊过滤器
        result = validator.validate_filters(test_func, mock_private_message)
        assert result is False
    
    def test_validate_custom_filter_pass(self, mock_private_message):
        """测试自定义过滤器通过"""
        validator = FilterValidator()
        
        def always_true_filter(event):
            return True
        
        custom_filter = CustomFilter(always_true_filter, "always_true")
        
        def test_func(event):
            return "test"
        test_func.__filters__ = [custom_filter]
        
        # 自定义过滤器返回True应该通过
        result = validator.validate_filters(test_func, mock_private_message)
        assert result is True
    
    def test_validate_custom_filter_fail(self, mock_private_message):
        """测试自定义过滤器失败"""
        validator = FilterValidator()
        
        def always_false_filter(event):
            return False
        
        custom_filter = CustomFilter(always_false_filter, "always_false")
        
        def test_func(event):
            return "test"
        test_func.__filters__ = [custom_filter]
        
        # 自定义过滤器返回False应该失败
        result = validator.validate_filters(test_func, mock_private_message)
        assert result is False
    
    def test_validate_filter_with_logic(self, mock_private_message):
        """测试包含逻辑的过滤器"""
        validator = FilterValidator()
        
        def user_id_filter(event):
            # 只允许特定用户ID
            return event.user_id == "123456"
        
        custom_filter = CustomFilter(user_id_filter, "user_id_check")
        
        def test_func(event):
            return "test"
        test_func.__filters__ = [custom_filter]
        
        # 匹配的用户ID应该通过
        mock_private_message.user_id = "123456"
        result = validator.validate_filters(test_func, mock_private_message)
        assert result is True
        
        # 不匹配的用户ID应该失败
        mock_private_message.user_id = "999999"
        result = validator.validate_filters(test_func, mock_private_message)
        assert result is False
    
    def test_validate_complex_filter_chain(self, mock_group_message, mock_status_manager):
        """测试复杂过滤器链"""
        validator = FilterValidator()
        
        # 创建多个过滤器
        group_filter = GroupFilter()
        admin_filter = AdminFilter()
        
        def time_filter(event):
            # 模拟时间过滤器：只在白天允许
            return True  # 简化为总是通过
        
        custom_time_filter = CustomFilter(time_filter, "time_check")
        
        # 模拟管理员权限
        mock_status_manager.user_has_role.return_value = True
        
        def test_func(event):
            return "test"
        test_func.__filters__ = [group_filter, admin_filter, custom_time_filter]
        
        # 所有条件都满足应该通过
        result = validator.validate_filters(test_func, mock_group_message)
        assert result is True
    
    def test_validate_filter_exception_handling(self, mock_private_message):
        """测试过滤器异常处理"""
        validator = FilterValidator()
        
        def error_filter(event):
            raise ValueError("Filter error")
        
        custom_filter = CustomFilter(error_filter, "error_filter")
        
        def test_func(event):
            return "test"
        test_func.__filters__ = [custom_filter]
        
        # 过滤器抛出异常时的行为（根据实现可能需要调整）
        assert validator.validate_filters(test_func, mock_private_message) is False
    
    def test_validate_mixed_filter_types(self, mock_group_message, mock_status_manager):
        """测试混合过滤器类型"""
        validator = FilterValidator()
        
        # 混合内置过滤器和自定义过滤器
        group_filter = GroupFilter()
        
        def custom_logic(event):
            return len(event.user_id) > 3  # 用户ID长度大于3
        
        custom_filter = CustomFilter(custom_logic, "id_length_check")
        
        # 模拟足够长的用户ID
        mock_group_message.user_id = "123456"
        
        def test_func(event):
            return "test"
        test_func.__filters__ = [group_filter, custom_filter]
        
        # 群聊消息且用户ID足够长应该通过
        result = validator.validate_filters(test_func, mock_group_message)
        assert result is True
        
        # 用户ID太短应该失败
        mock_group_message.user_id = "12"
        result = validator.validate_filters(test_func, mock_group_message)
        assert result is False


class TestFilterValidatorEdgeCases:
    """过滤器验证器边界情况测试"""
    
    def test_validate_none_function(self, mock_private_message):
        """测试验证None函数"""
        validator = FilterValidator()
        
        # 传入None应该有适当的处理
        result = validator.validate_filters(None, mock_private_message)
        # 根据实现，可能返回True或抛出异常
        assert result is True or result is False
    
    def test_validate_invalid_filter_object(self, mock_private_message):
        """测试验证无效过滤器对象"""
        validator = FilterValidator()
        
        def test_func(event):
            return "test"
        # 添加一个无效的过滤器对象
        test_func.__filters__ = ["invalid_filter"]  # 字符串而不是过滤器对象
        
        # 应该有适当的错误处理
        assert validator.validate_filters(test_func, mock_private_message) is False
    
    def test_validate_large_filter_chain(self, mock_private_message):
        """测试验证大量过滤器链"""
        validator = FilterValidator()
        
        # 创建大量过滤器
        filters = []
        for i in range(100):
            def filter_func(event, index=i):
                return index % 2 == 0  # 偶数索引通过
            
            filters.append(CustomFilter(filter_func, f"filter_{i}"))
        
        def test_func(event):
            return "test"
        test_func.__filters__ = filters
        
        # 由于有奇数索引的过滤器返回False，整体应该失败
        result = validator.validate_filters(test_func, mock_private_message)
        assert result is False


class TestFilterValidatorIntegration:
    """过滤器验证器集成测试"""
    
    def test_validator_with_real_filters(self, mock_group_message, mock_private_message, mock_status_manager):
        """测试验证器与真实过滤器的集成"""
        validator = FilterValidator()
        
        # 创建真实的过滤器组合
        group_filter = GroupFilter()
        private_filter = PrivateFilter()
        admin_filter = AdminFilter()
        
        # 模拟管理员权限
        mock_status_manager.user_has_role.return_value = True
        
        # 测试群聊+管理员组合
        def group_admin_func(event):
            return "group admin"
        group_admin_func.__filters__ = [group_filter, admin_filter]
        
        # 群聊消息应该通过
        result = validator.validate_filters(group_admin_func, mock_group_message)
        assert result is True
        
        # 私聊消息应该失败（因为不是群聊）
        result = validator.validate_filters(group_admin_func, mock_private_message)
        assert result is False
        
        # 测试私聊+管理员组合
        def private_admin_func(event):
            return "private admin"
        private_admin_func.__filters__ = [private_filter, admin_filter]
        
        # 私聊消息应该通过
        result = validator.validate_filters(private_admin_func, mock_private_message)
        assert result is True
        
        # 群聊消息应该失败（因为不是私聊）
        result = validator.validate_filters(private_admin_func, mock_group_message)
        assert result is False
