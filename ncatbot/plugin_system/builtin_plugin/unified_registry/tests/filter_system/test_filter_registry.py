"""过滤器注册器测试

测试过滤器注册器的功能，包括过滤器实例注册、函数注册、查找等。
"""

import pytest
from unittest.mock import Mock

from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.registry import (
    FilterRegistry, FilterEntry
)
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system.builtin import (
    GroupFilter, PrivateFilter, CustomFilter
)


class TestFilterRegistry:
    """过滤器注册器核心功能测试"""
    
    def test_registry_creation(self):
        """测试注册器创建"""
        registry = FilterRegistry()
        assert len(registry._filters) == 0
        assert len(registry._function_filters) == 0
    
    def test_register_filter_instance(self, clean_registries):
        """测试注册过滤器实例"""
        registry = FilterRegistry()
        group_filter = GroupFilter()
        
        # 注册过滤器实例
        registry.register_filter("group_test", group_filter)
        
        # 验证注册成功
        assert "group_test" in registry._filters
        entry = registry._filters["group_test"]
        assert isinstance(entry, FilterEntry)
        assert entry.name == "group_test"
        assert entry.filter_instance is group_filter
    
    def test_register_filter_with_metadata(self, clean_registries):
        """测试注册带元数据的过滤器"""
        registry = FilterRegistry()
        private_filter = PrivateFilter()
        metadata = {"author": "test", "version": "1.0"}
        
        # 注册带元数据的过滤器
        registry.register_filter("private_test", private_filter, metadata)
        
        # 验证元数据
        entry = registry._filters["private_test"]
        assert entry.metadata == metadata
    
    def test_register_filter_overwrite_warning(self, clean_registries, caplog):
        """测试重复注册过滤器的警告"""
        registry = FilterRegistry()
        filter1 = GroupFilter()
        filter2 = PrivateFilter()
        
        # 第一次注册
        registry.register_filter("test_filter", filter1)
        
        # 第二次注册同名过滤器
        registry.register_filter("test_filter", filter2)
        
        # 应该有警告日志
        assert "过滤器 test_filter 已存在，将被覆盖" in caplog.text
        
        # 第二个过滤器应该覆盖第一个
        entry = registry._filters["test_filter"]
        assert entry.filter_instance is filter2
    
    def test_register_function_direct(self, clean_registries):
        """测试直接注册过滤器函数"""
        registry = FilterRegistry()
        
        def test_filter(event):
            return True
        
        # 直接注册函数
        decorated_func = registry.register(test_filter)
        
        # 函数应该被标记
        assert hasattr(decorated_func, '__is_filter__')
        assert decorated_func.__is_filter__ is True
        
        # 应该添加到函数过滤器列表
        assert test_filter in registry._function_filters
        
        # 应该创建相应的自定义过滤器
        assert "test_filter" in registry._filters
        entry = registry._filters["test_filter"]
        assert isinstance(entry.filter_instance, CustomFilter)
    
    def test_register_function_as_decorator(self, clean_registries):
        """测试将注册器用作装饰器"""
        registry = FilterRegistry()
        
        @registry.register("custom_name")
        def test_filter(event):
            return True
        
        # 函数应该被标记
        assert hasattr(test_filter, '__is_filter__')
        assert test_filter.__is_filter__ is True
        
        # 应该使用自定义名称
        assert "custom_name" in registry._filters
    
    def test_register_function_callable(self, clean_registries):
        """测试注册器作为可调用对象"""
        registry = FilterRegistry()
        
        @registry("callable_filter")
        def test_filter(event):
            return True
        
        # 应该正常注册
        assert "callable_filter" in registry._filters
        assert test_filter in registry._function_filters
    
    def test_add_filter_to_function(self, clean_registries):
        """测试为函数添加过滤器"""
        registry = FilterRegistry()
        group_filter = GroupFilter()
        private_filter = PrivateFilter()
        
        # 注册过滤器实例
        registry.register_filter("group", group_filter)
        registry.register_filter("private", private_filter)
        
        def test_func(event):
            return "test"
        
        # 添加过滤器（通过名称和实例）
        result = registry.add_filter_to_function(test_func, "group", private_filter)
        
        # 函数应该有过滤器
        assert hasattr(result, '__filters__')
        filters = result.__filters__
        assert len(filters) == 2
        assert group_filter in filters
        assert private_filter in filters
    
    def test_add_filter_to_function_not_found(self, clean_registries, caplog):
        """测试添加不存在的过滤器"""
        registry = FilterRegistry()
        
        def test_func(event):
            return "test"
        
        # 尝试添加不存在的过滤器
        registry.add_filter_to_function(test_func, "nonexistent")
        
        # 应该有错误日志
        assert "未找到名为 nonexistent 的过滤器" in caplog.text
    
    def test_add_filter_unsupported_type(self, clean_registries, caplog):
        """测试添加不支持类型的过滤器"""
        registry = FilterRegistry()
        
        def test_func(event):
            return "test"
        
        # 尝试添加无效类型的过滤器
        registry.add_filter_to_function(test_func, 123)  # 数字类型
        
        # 应该有错误日志
        assert "不支持的过滤器类型" in caplog.text
    
    def test_get_filter(self, clean_registries):
        """测试获取过滤器条目"""
        registry = FilterRegistry()
        group_filter = GroupFilter()
        
        # 注册过滤器
        registry.register_filter("test_group", group_filter)
        
        # 获取存在的过滤器
        entry = registry.get_filter("test_group")
        assert entry is not None
        assert entry.name == "test_group"
        assert entry.filter_instance is group_filter
        
        # 获取不存在的过滤器
        entry = registry.get_filter("nonexistent")
        assert entry is None
    
    def test_get_filter_instance(self, clean_registries):
        """测试获取过滤器实例"""
        registry = FilterRegistry()
        private_filter = PrivateFilter()
        
        # 注册过滤器
        registry.register_filter("test_private", private_filter)
        
        # 获取存在的过滤器实例
        instance = registry.get_filter_instance("test_private")
        assert instance is private_filter
        
        # 获取不存在的过滤器实例
        instance = registry.get_filter_instance("nonexistent")
        assert instance is None
    
    def test_list_filters(self, clean_registries):
        """测试列出所有过滤器"""
        registry = FilterRegistry()
        group_filter = GroupFilter()
        private_filter = PrivateFilter()
        
        # 注册多个过滤器
        registry.register_filter("group", group_filter)
        registry.register_filter("private", private_filter)
        
        # 列出所有过滤器
        filters = registry.list_filters()
        assert len(filters) == 2
        
        # 验证内容
        names = [entry.name for entry in filters]
        assert "group" in names
        assert "private" in names
    
    def test_list_filter_functions(self, clean_registries):
        """测试列出所有过滤器函数"""
        registry = FilterRegistry()
        
        def filter1(event):
            return True
        
        def filter2(event):
            return False
        
        # 注册函数
        registry.register(filter1)
        registry.register(filter2)
        
        # 列出所有函数
        functions = registry.list_filter_functions()
        assert len(functions) == 2
        assert filter1 in functions
        assert filter2 in functions
    
    def test_filters_decorator(self, clean_registries):
        """测试filters装饰器"""
        registry = FilterRegistry()
        group_filter = GroupFilter()
        private_filter = PrivateFilter()
        
        # 注册过滤器
        registry.register_filter("group", group_filter)
        registry.register_filter("private", private_filter)
        
        @registry.filters("group", private_filter)
        def test_func(event):
            return "test"
        
        # 函数应该有过滤器
        assert hasattr(test_func, '__filters__')
        # Note: 这里测试可能需要根据实际实现调整


class TestFilterRegistryValidation:
    """过滤器注册器验证测试"""
    
    def test_validate_filter_function(self, clean_registries):
        """测试过滤器函数验证"""
        registry = FilterRegistry()
        
        def valid_filter(event):
            return True
        
        # 目前验证是空实现，应该不抛出异常
        registry._validate_filter_function(valid_filter)
    
    def test_function_filters_class_attribute(self):
        """测试函数过滤器类属性"""
        # 验证类属性存在
        assert hasattr(FilterRegistry, '_function_filters')
        assert isinstance(FilterRegistry._function_filters, dict)


class TestFilterRegistryIntegration:
    """过滤器注册器集成测试"""
    
    def test_registry_workflow(self, clean_registries):
        """测试完整的注册器工作流"""
        registry = FilterRegistry()
        
        # 1. 注册过滤器实例
        group_filter = GroupFilter()
        registry.register_filter("group_only", group_filter)
        
        # 2. 注册过滤器函数
        @registry.register("time_check")
        def time_filter(event):
            return True
        
        # 3. 为函数添加过滤器
        def target_function(event):
            return "result"
        
        registry.add_filter_to_function(target_function, "group_only", "time_check")
        
        # 4. 验证结果
        assert "group_only" in registry._filters
        assert "time_check" in registry._filters
        assert hasattr(target_function, '__filters__')
        assert len(target_function.__filters__) == 2
    
    def test_multiple_registries_isolation(self, clean_registries):
        """测试多个注册器实例的隔离"""
        registry1 = FilterRegistry()
        registry2 = FilterRegistry()
        
        # 在不同注册器中注册过滤器
        registry1.register_filter("test", GroupFilter())
        registry2.register_filter("test", PrivateFilter())
        
        # 验证隔离
        entry1 = registry1.get_filter("test")
        entry2 = registry2.get_filter("test")
        
        assert isinstance(entry1.filter_instance, GroupFilter)
        assert isinstance(entry2.filter_instance, PrivateFilter)
        
        # 一个注册器不应该能看到另一个的过滤器
        assert registry1.get_filter("test") is not None
        assert registry2.get_filter("test") is not None
        assert entry1 is not entry2
