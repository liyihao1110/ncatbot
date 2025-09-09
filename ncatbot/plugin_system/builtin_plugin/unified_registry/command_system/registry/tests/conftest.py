"""测试配置和共享fixture"""

import pytest
from typing import Any
from unittest.mock import Mock
from dataclasses import dataclass


@dataclass
class MockEvent:
    """模拟事件对象"""
    user_id: int = 123
    message_type: str = "group"
    is_admin: bool = False
    is_root: bool = False


@dataclass 
class MockMessageSegment:
    """模拟消息段对象"""
    msg_seg_type: str = "at"
    qq: int = 123
    file: str = ""
    
    @property
    def type(self):
        return self.msg_seg_type


@pytest.fixture
def mock_event():
    """提供模拟事件"""
    return MockEvent()


@pytest.fixture
def mock_admin_event():
    """提供模拟管理员事件"""
    return MockEvent(user_id=999, is_admin=True)


@pytest.fixture
def mock_message_segment():
    """提供模拟消息段"""
    return MockMessageSegment()


@pytest.fixture
def mock_image_segment():
    """提供模拟图片消息段"""
    return MockMessageSegment(msg_seg_type="image", file="test.jpg")


@pytest.fixture
def sample_function():
    """提供样例函数"""
    def test_func(event, name: str, age: int = 18, verbose: bool = False):
        """测试函数
        
        Args:
            event: 事件对象
            name: 用户名
            age: 年龄（默认18）
            verbose: 是否详细模式
        """
        return f"Hello {name}, age {age}, verbose={verbose}"
    
    return test_func


@pytest.fixture
def complex_function():
    """提供复杂函数"""
    def complex_func(event, target, data: str, count: int = 1, 
                    format: str = "json", force: bool = False):
        """复杂测试函数"""
        return f"Processing {target}: {data} x{count} as {format}, force={force}"
    
    return complex_func
