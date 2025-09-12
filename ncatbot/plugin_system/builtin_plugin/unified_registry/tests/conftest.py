"""全局测试配置和fixtures

为 unified_registry 模块提供通用的测试配置、模拟对象和fixtures。
"""

import pytest
import pytest_asyncio
import asyncio
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, AsyncMock
from dataclasses import dataclass

from ncatbot.utils.testing import TestClient, TestHelper, EventFactory
from ncatbot.plugin_system.builtin_plugin.unified_registry import UnifiedRegistryPlugin
from ncatbot.plugin_system.builtin_plugin.unified_registry.filter_system import (
    filter_registry, GroupFilter, PrivateFilter, AdminFilter, CustomFilter
)
from ncatbot.plugin_system import command_registry
from ncatbot.core.event.message_segment import MessageArray, Text, At, Image
from ncatbot.core.event import BaseMessageEvent


# EventFactory will be used instead of Mock classes


@pytest.fixture(scope="session")
def event_loop():
    """提供事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_client():
    """提供配置好的测试客户端"""
    # 在创建客户端前设置测试配置，避免用户输入
    from ncatbot.utils import ncatbot_config
    original_bt_uin = ncatbot_config.bt_uin
    original_root = ncatbot_config.root
    
    # 设置测试用的QQ号
    ncatbot_config.bt_uin = "123456789"  # 测试用的机器人QQ号
    ncatbot_config.root = "987654321"    # 测试用的root QQ号
    
    try:
        client = TestClient(load_plugin=False)
        client.start()
        yield client
    finally:
        # 恢复原始配置
        ncatbot_config.bt_uin = original_bt_uin
        ncatbot_config.root = original_root


@pytest_asyncio.fixture
async def test_helper(test_client):
    """提供测试辅助类"""
    helper = TestHelper(test_client)
    return helper


@pytest_asyncio.fixture
async def unified_plugin(test_client):
    """提供统一注册插件实例"""
    test_client.register_plugin(UnifiedRegistryPlugin)
    plugins = test_client.get_registered_plugins()
    plugin = next((p for p in plugins if isinstance(p, UnifiedRegistryPlugin)), None)
    assert plugin is not None, "UnifiedRegistryPlugin 应该被注册"
    yield plugin
    # 清理
    test_client.unregister_plugin(plugin)


# Event fixtures will use EventFactory instead


@pytest.fixture
def sample_command_function():
    """提供示例命令函数"""
    def hello_command(event, name: str = "World"):
        """简单的问候命令"""
        return f"Hello {name}!"
    
    # 标记为命令
    hello_command.__is_command__ = True
    return hello_command


@pytest.fixture
def sample_filter_function():
    """提供示例过滤器函数"""
    def time_filter(event):
        """时间过滤器：只在白天允许"""
        import datetime
        return datetime.datetime.now().hour < 20
    
    return time_filter


@pytest.fixture
def sample_complex_command():
    """提供复杂命令函数"""
    def deploy_command(event, app_name: str, env: str = "dev", verbose: bool = False):
        """部署命令示例"""
        result = f"Deploying {app_name} to {env}"
        if verbose:
            result += " (verbose mode)"
        return result
    
    # 标记为命令
    deploy_command.__is_command__ = True
    return deploy_command


@pytest.fixture
def mock_filters():
    """提供模拟过滤器集合"""
    return {
        'group_filter': GroupFilter(),
        'private_filter': PrivateFilter(),
        'admin_filter': AdminFilter(),
        'custom_filter': CustomFilter(lambda event: True, "always_pass")
    }


@pytest.fixture
def clean_registries():
    """清理注册器状态"""
    # 保存原始状态
    original_filter_filters = filter_registry._filters.copy()
    original_filter_functions = filter_registry._function_filters.copy()
    original_commands = command_registry.root_group.commands.copy()
    original_subgroups = command_registry.root_group.subgroups.copy()
    
    yield
    
    # 恢复原始状态
    filter_registry._filters.clear()
    filter_registry._filters.update(original_filter_filters)
    filter_registry._function_filters.clear()
    filter_registry._function_filters.extend(original_filter_functions)
    
    command_registry.root_group.commands.clear()
    command_registry.root_group.commands.update(original_commands)
    command_registry.root_group.subgroups.clear()
    command_registry.root_group.subgroups.update(original_subgroups)


@pytest.fixture
def mock_status_manager():
    """模拟状态管理器"""
    from unittest.mock import Mock
    from ncatbot.utils import status
    
    # 保存原始状态
    original_manager = status.global_access_manager
    
    # 创建模拟管理器
    mock_manager = Mock()
    mock_manager.user_has_role.return_value = False
    status.global_access_manager = mock_manager
    
    yield mock_manager
    
    # 恢复原始状态
    status.global_access_manager = original_manager


@pytest.fixture
def mock_group_message():
    """群聊消息模拟对象"""
    return EventFactory.create_group_message(
        message="test message",
        user_id="123456",
        group_id="789012"
    )


@pytest.fixture
def mock_private_message():
    """私聊消息模拟对象"""
    return EventFactory.create_private_message(
        message="test message", 
        user_id="123456"
    )


class AsyncTestCase:
    """异步测试基类"""
    
    def run_async(self, coro):
        """运行异步协程"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)
