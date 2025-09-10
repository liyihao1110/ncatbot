"""内置过滤器测试

测试各种内置过滤器的功能，包括群聊、私聊、管理员、Root和自定义过滤器。
"""

import pytest
from unittest.mock import Mock

from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.builtin import (
    GroupFilter, PrivateFilter, AdminFilter, RootFilter, CustomFilter
)
from ncatbot.utils.assets.literals import PermissionGroup


class TestGroupFilter:
    """群聊过滤器测试"""
    
    def test_group_filter_creation(self):
        """测试群聊过滤器创建"""
        filter_instance = GroupFilter()
        assert filter_instance.name == "GroupFilter"
    
    def test_group_filter_check_group_message(self, mock_group_message):
        """测试群聊过滤器检查群聊消息"""
        filter_instance = GroupFilter()
        result = filter_instance.check(mock_group_message)
        assert result is True
    
    def test_group_filter_check_private_message(self, mock_private_message):
        """测试群聊过滤器检查私聊消息"""
        filter_instance = GroupFilter()
        result = filter_instance.check(mock_private_message)
        assert result is False
    
    def test_group_filter_as_decorator(self, sample_command_function):
        """测试群聊过滤器作为装饰器使用"""
        filter_instance = GroupFilter()
        
        # 应用过滤器
        filter_instance(sample_command_function)
                
        # 函数应该有过滤器标记
        assert hasattr(sample_command_function, '__filters__')
        assert len(sample_command_function.__filters__) > 0
        assert any(isinstance(f, GroupFilter) for f in sample_command_function.__filters__)


class TestPrivateFilter:
    """私聊过滤器测试"""
    
    def test_private_filter_creation(self):
        """测试私聊过滤器创建"""
        filter_instance = PrivateFilter()
        assert filter_instance.name == "PrivateFilter"
    
    def test_private_filter_check_private_message(self, mock_private_message):
        """测试私聊过滤器检查私聊消息"""
        filter_instance = PrivateFilter()
        result = filter_instance.check(mock_private_message)
        assert result is True
    
    def test_private_filter_check_group_message(self, mock_group_message):
        """测试私聊过滤器检查群聊消息"""
        filter_instance = PrivateFilter()
        result = filter_instance.check(mock_group_message)
        assert result is False


class TestAdminFilter:
    """管理员过滤器测试"""
    
    def test_admin_filter_creation(self):
        """测试管理员过滤器创建"""
        filter_instance = AdminFilter()
        assert filter_instance.name == "AdminFilter"
    
    def test_admin_filter_no_manager(self, mock_private_message):
        """测试管理员过滤器在没有管理器时的行为"""
        filter_instance = AdminFilter()
        
        # 当没有全局访问管理器时应该返回 False
        with pytest.MonkeyPatch().context() as m:
            from ncatbot.utils import status
            m.setattr(status, 'global_access_manager', None)
            
            result = filter_instance.check(mock_private_message)
            assert result is False
    
    def test_admin_filter_with_admin_user(self, mock_private_message, mock_status_manager):
        """测试管理员过滤器检查管理员用户"""
        filter_instance = AdminFilter()
        
        # 模拟用户有管理员权限
        mock_status_manager.user_has_role.return_value = True
        
        result = filter_instance.check(mock_private_message)
        assert result is True
        
        # 验证调用参数
        mock_status_manager.user_has_role.assert_called_with(
            mock_private_message.user_id, 
            PermissionGroup.ADMIN.value
        )
    
    def test_admin_filter_with_normal_user(self, mock_private_message, mock_status_manager):
        """测试管理员过滤器检查普通用户"""
        filter_instance = AdminFilter()
        
        # 模拟用户没有管理员权限
        mock_status_manager.user_has_role.return_value = False
        
        result = filter_instance.check(mock_private_message)
        assert result is False


class TestRootFilter:
    """Root权限过滤器测试"""
    
    def test_root_filter_creation(self):
        """测试Root过滤器创建"""
        filter_instance = RootFilter()
        assert filter_instance.name == "RootFilter"
    
    def test_root_filter_no_manager(self, mock_private_message):
        """测试Root过滤器在没有管理器时的行为"""
        filter_instance = RootFilter()
        
        # 当没有全局访问管理器时应该返回 False
        with pytest.MonkeyPatch().context() as m:
            from ncatbot.utils import status
            m.setattr(status, 'global_access_manager', None)
            
            result = filter_instance.check(mock_private_message)
            assert result is False
    
    def test_root_filter_with_root_user(self, mock_private_message, mock_status_manager):
        """测试Root过滤器检查Root用户"""
        filter_instance = RootFilter()
        
        # 模拟用户有Root权限
        mock_status_manager.user_has_role.return_value = True
        
        result = filter_instance.check(mock_private_message)
        assert result is True
        
        # 验证调用参数
        mock_status_manager.user_has_role.assert_called_with(
            mock_private_message.user_id,
            PermissionGroup.ROOT.value
        )
    
    def test_root_filter_with_normal_user(self, mock_private_message, mock_status_manager):
        """测试Root过滤器检查普通用户"""
        filter_instance = RootFilter()
        
        # 模拟用户没有Root权限
        mock_status_manager.user_has_role.return_value = False
        
        result = filter_instance.check(mock_private_message)
        assert result is False


class TestCustomFilter:
    """自定义过滤器测试"""
    
    def test_custom_filter_creation(self):
        """测试自定义过滤器创建"""
        def test_filter_func(event):
            return True
        
        filter_instance = CustomFilter(test_filter_func, "test_filter")
        assert filter_instance.name == "test_filter"
        assert filter_instance.filter_func is test_filter_func
    
    def test_custom_filter_auto_name(self):
        """测试自定义过滤器自动命名"""
        def named_filter_func(event):
            return True
        
        filter_instance = CustomFilter(named_filter_func)
        assert filter_instance.name == "named_filter_func"
    
    def test_custom_filter_check_true(self, mock_private_message):
        """测试自定义过滤器返回True"""
        def always_true_filter(event):
            return True
        
        filter_instance = CustomFilter(always_true_filter)
        result = filter_instance.check(mock_private_message)
        assert result is True
    
    def test_custom_filter_check_false(self, mock_private_message):
        """测试自定义过滤器返回False"""
        def always_false_filter(event):
            return False
        
        filter_instance = CustomFilter(always_false_filter)
        result = filter_instance.check(mock_private_message)
        assert result is False
    
    def test_custom_filter_with_logic(self, mock_private_message, mock_group_message):
        """测试自定义过滤器包含逻辑"""
        def time_based_filter(event):
            # 模拟时间过滤器：只在用户ID末尾是偶数时通过
            return int(event.user_id) % 2 == 0
        
        filter_instance = CustomFilter(time_based_filter)
        
        # 测试偶数用户ID
        mock_private_message.user_id = "123456"  # 偶数
        result = filter_instance.check(mock_private_message)
        assert result is True
        
        # 测试奇数用户ID
        mock_private_message.user_id = "123457"  # 奇数
        result = filter_instance.check(mock_private_message)
        assert result is False
    
    def test_custom_filter_exception_handling(self, mock_private_message):
        """测试自定义过滤器异常处理"""
        def error_filter(event):
            raise ValueError("Test error")
        
        filter_instance = CustomFilter(error_filter)
        
        # 异常应该被向上传播（或根据实现决定如何处理）
        with pytest.raises(ValueError):
            filter_instance.check(mock_private_message)


class TestFilterComposition:
    """过滤器组合测试"""
    
    def test_multiple_filters_and_logic(self, mock_group_message, mock_status_manager):
        """测试多个过滤器的AND逻辑"""
        # 创建组合过滤器：群聊 + 管理员
        group_filter = GroupFilter()
        admin_filter = AdminFilter()
        
        # 模拟管理员权限
        mock_status_manager.user_has_role.return_value = True
        
        # 群聊消息且是管理员
        result1 = group_filter.check(mock_group_message)
        result2 = admin_filter.check(mock_group_message)
        
        assert result1 is True  # 群聊过滤器通过
        assert result2 is True  # 管理员过滤器通过
        
        # 组合结果
        combined_result = result1 and result2
        assert combined_result is True
    
    def test_filter_chain_failure(self, mock_private_message, mock_status_manager):
        """测试过滤器链失败"""
        # 创建组合过滤器：群聊 + 管理员
        group_filter = GroupFilter()
        admin_filter = AdminFilter()
        
        # 模拟管理员权限
        mock_status_manager.user_has_role.return_value = True
        
        # 私聊消息但要求群聊
        result1 = group_filter.check(mock_private_message)
        result2 = admin_filter.check(mock_private_message)
        
        assert result1 is False  # 群聊过滤器失败
        assert result2 is True   # 管理员过滤器通过
        
        # 组合结果应该失败
        combined_result = result1 and result2
        assert combined_result is False
