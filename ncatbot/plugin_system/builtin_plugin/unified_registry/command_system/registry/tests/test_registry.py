"""注册器系统测试

测试命令注册器的核心功能。
"""

import pytest
from unittest.mock import Mock

from ..registry import ModernRegistry, CommandGroup, CommandDefinition
from ..decorators import option, param
from ..type_system import CommonUnionTypes
from ..exceptions import CommandRegistrationError, CommandNotFoundError
from .conftest import MockEvent


class TestCommandDefinition:
    """命令定义测试"""
    
    def test_command_definition_creation(self):
        """测试命令定义创建"""
        def test_func(event):
            pass
        
        cmd_def = CommandDefinition(
            name="test",
            func=test_func,
            description="测试命令"
        )
        
        assert cmd_def.name == "test"
        assert cmd_def.func is test_func
        assert cmd_def.description == "测试命令"
        assert len(cmd_def.parameters) == 0
        assert len(cmd_def.options) == 0
        assert len(cmd_def.aliases) == 0
        assert cmd_def.strict_mode is True
        assert cmd_def.auto_help is True
    
    def test_get_all_names(self):
        """测试获取所有名称"""
        def test_func(event):
            pass
        
        cmd_def = CommandDefinition(
            name="test",
            func=test_func,
            aliases=["t", "test_cmd"]
        )
        
        names = cmd_def.get_all_names()
        assert "test" in names
        assert "t" in names
        assert "test_cmd" in names
        assert len(names) == 3
    
    def test_get_positional_parameters(self):
        """测试获取位置参数"""
        from ..specs import ParameterSpec
        
        def test_func(event):
            pass
        
        pos_param = ParameterSpec(name="pos", type=str, is_positional=True)
        named_param = ParameterSpec(name="named", type=str, is_named=True, is_positional=False)
        
        cmd_def = CommandDefinition(
            name="test",
            func=test_func,
            parameters=[pos_param, named_param]
        )
        
        pos_params = cmd_def.get_positional_parameters()
        assert len(pos_params) == 1
        assert pos_params[0].name == "pos"
    
    def test_get_named_parameters(self):
        """测试获取命名参数"""
        from ..specs import ParameterSpec
        
        def test_func(event):
            pass
        
        pos_param = ParameterSpec(name="pos", type=str, is_positional=True)
        named_param = ParameterSpec(name="named", type=str, is_named=True, is_positional=False)
        
        cmd_def = CommandDefinition(
            name="test",
            func=test_func,
            parameters=[pos_param, named_param]
        )
        
        named_params = cmd_def.get_named_parameters()
        assert len(named_params) == 1
        assert named_params[0].name == "named"


class TestCommandGroup:
    """命令组测试"""
    
    def test_command_group_creation(self):
        """测试命令组创建"""
        group = CommandGroup("test_group", description="测试组")
        
        assert group.name == "test_group"
        assert group.description == "测试组"
        assert group.parent is None
        assert len(group.commands) == 0
        assert len(group.subgroups) == 0
        assert group.default_config['strict_mode'] is True
    
    def test_nested_command_group(self):
        """测试嵌套命令组"""
        parent = CommandGroup("parent")
        child = CommandGroup("child", parent=parent)
        
        assert child.parent is parent
        assert child.get_full_name() == "parent.child"
    
    def test_command_registration(self):
        """测试命令注册"""
        group = CommandGroup("test")
        
        @group.command("hello", description="问候命令")
        def hello_cmd(event):
            return "Hello"
        
        assert "hello" in group.commands
        assert group.commands["hello"].name == "hello"
        assert group.commands["hello"].func is hello_cmd
    
    def test_command_with_aliases(self):
        """测试带别名的命令"""
        group = CommandGroup("test")
        
        @group.command("status", aliases=["st", "stat"])
        def status_cmd(event):
            return "OK"
        
        # 主名称和别名都应该注册
        assert "status" in group.commands
        assert "st" in group.commands
        assert "stat" in group.commands
        # 都应该指向同一个命令定义
        assert group.commands["status"] is group.commands["st"]
        assert group.commands["status"] is group.commands["stat"]
    
    def test_subgroup_creation(self):
        """测试子组创建"""
        parent = CommandGroup("parent")
        child = parent.group("child", description="子组")
        
        assert "child" in parent.subgroups
        assert parent.subgroups["child"] is child
        assert child.parent is parent
        assert child.description == "子组"
    
    def test_configuration_inheritance(self):
        """测试配置继承"""
        parent = CommandGroup("parent")
        parent.configure(strict_mode=False, auto_help=False)
        
        child = parent.group("child")
        
        # 子组应该继承父组的配置
        assert child.default_config['strict_mode'] is False
        assert child.default_config['auto_help'] is False
    
    def test_command_conflict_detection(self):
        """测试命令冲突检测"""
        group = CommandGroup("test")
        
        @group.command("hello")
        def hello1(event):
            pass
        
        # 尝试注册同名命令应该失败
        with pytest.raises(CommandRegistrationError):
            @group.command("hello")
            def hello2(event):
                pass


class TestModernRegistry:
    """现代化注册器测试"""
    
    def test_registry_initialization(self):
        """测试注册器初始化"""
        registry = ModernRegistry()
        
        assert registry.root_group is not None
        assert registry.error_handler is not None
        assert registry.config['prefix'] == '/'
        assert registry.config['case_sensitive'] is False
    
    def test_root_command_registration(self):
        """测试根级命令注册"""
        registry = ModernRegistry()
        
        @registry.command("hello")
        def hello_cmd(event):
            return "Hello"
        
        # 应该注册到根组
        assert "hello" in registry.root_group.commands
    
    def test_group_creation(self):
        """测试组创建"""
        registry = ModernRegistry()
        
        admin_group = registry.group("admin", description="管理员命令")
        
        assert "admin" in registry.root_group.subgroups
        assert registry.root_group.subgroups["admin"] is admin_group
        assert admin_group.description == "管理员命令"
    
    def test_configuration(self):
        """测试配置"""
        registry = ModernRegistry()
        
        registry.configure(
            prefix="!",
            case_sensitive=True,
            debug=True
        )
        
        assert registry.config['prefix'] == "!"
        assert registry.config['case_sensitive'] is True
        assert registry.config['debug'] is True
    
    def test_command_finding_basic(self):
        """测试基础命令查找"""
        registry = ModernRegistry()
        
        @registry.command("hello")
        def hello_cmd(event):
            return "Hello"
        
        # 查找存在的命令
        cmd_def = registry.find_command("/hello")
        assert cmd_def is not None
        assert cmd_def.name == "hello"
        
        # 查找不存在的命令
        cmd_def = registry.find_command("/unknown")
        assert cmd_def is None
    
    def test_command_finding_with_prefix(self):
        """测试带前缀的命令查找"""
        registry = ModernRegistry()
        registry.configure(prefix="!")
        
        @registry.command("test")
        def test_cmd(event):
            pass
        
        # 带前缀的查找
        cmd_def = registry.find_command("!test")
        assert cmd_def is not None
        assert cmd_def.name == "test"
        
        # 不带前缀应该找不到
        cmd_def = registry.find_command("test")
        assert cmd_def is None
    
    def test_nested_command_finding(self):
        """测试嵌套命令查找"""
        registry = ModernRegistry()
        
        admin_group = registry.group("admin")
        
        @admin_group.command("user")
        def admin_user_cmd(event):
            pass
        
        # 查找嵌套命令
        cmd_def = registry.find_command("/admin user")
        assert cmd_def is not None
        assert cmd_def.name == "user"
    
    def test_get_all_commands(self):
        """测试获取所有命令"""
        registry = ModernRegistry()
        
        @registry.command("hello")
        def hello_cmd(event):
            pass
        
        admin_group = registry.group("admin")
        
        @admin_group.command("user")
        def admin_user_cmd(event):
            pass
        
        all_commands = registry.get_all_commands()
        command_names = [cmd.name for cmd in all_commands]
        
        assert "hello" in command_names
        assert "user" in command_names
    
    def test_get_command_names(self):
        """测试获取命令名称列表"""
        registry = ModernRegistry()
        
        @registry.command("hello", aliases=["hi"])
        def hello_cmd(event):
            pass
        
        @registry.command("bye")
        def bye_cmd(event):
            pass
        
        names = registry.get_command_names()
        
        assert "hello" in names
        assert "hi" in names  # 别名也应该包含
        assert "bye" in names
        assert len(set(names)) >= 3  # 去重后至少有3个
    
    def test_validate_command_text(self):
        """测试命令文本验证"""
        registry = ModernRegistry()
        
        # 有效的命令文本
        valid, error = registry.validate_command_text("/hello")
        assert valid is True
        assert error is None
        
        # 空命令文本
        valid, error = registry.validate_command_text("")
        assert valid is False
        assert "不能为空" in error
        
        # 没有前缀的命令文本
        valid, error = registry.validate_command_text("hello")
        assert valid is False
        assert "必须以" in error and "/" in error
    
    def test_error_formatting(self):
        """测试错误格式化"""
        registry = ModernRegistry()
        
        @registry.command("hello")
        def hello_cmd(event):
            pass
        
        # 创建一个命令不存在错误
        error = CommandNotFoundError("helo", ["hello", "help"])
        formatted = registry.format_error(error)
        
        assert "❌" in formatted
        assert "helo" in formatted
        assert "hello" in formatted  # 应该包含可用命令


class TestComplexCommandRegistration:
    """复杂命令注册测试"""
    
    def test_command_with_decorators(self):
        """测试带装饰器的命令"""
        registry = ModernRegistry()
        
        @registry.command("deploy", description="部署应用")
        @option("-v", "--verbose", help="详细输出")
        @param("env", type=str, default="dev", help="环境")
        def deploy_cmd(event, app_name: str, env="dev", verbose=False):
            return f"Deploy {app_name} to {env}"
        
        cmd_def = registry.find_command("/deploy")
        assert cmd_def is not None
        assert cmd_def.description == "部署应用"
        assert len(cmd_def.options) > 0
        assert len(cmd_def.parameters) > 0
    
    def test_multi_level_groups(self):
        """测试多级命令组"""
        registry = ModernRegistry()
        
        admin_group = registry.group("admin")
        db_group = admin_group.group("db")
        
        @db_group.command("backup")
        def db_backup_cmd(event):
            return "Backup database"
        
        # 应该能通过完整路径找到
        cmd_def = registry.find_command("/admin db backup")
        assert cmd_def is not None
        assert cmd_def.name == "backup"
    
    def test_command_aliases_in_groups(self):
        """测试组内命令别名"""
        registry = ModernRegistry()
        
        admin_group = registry.group("admin")
        
        @admin_group.command("status", aliases=["st", "stat"])
        def admin_status_cmd(event):
            return "Admin status"
        
        # 所有别名都应该能找到
        cmd_def1 = registry.find_command("/admin status")
        cmd_def2 = registry.find_command("/admin st")
        cmd_def3 = registry.find_command("/admin stat")
        
        assert cmd_def1 is not None
        assert cmd_def2 is not None  
        assert cmd_def3 is not None
        assert cmd_def1 is cmd_def2 is cmd_def3


if __name__ == "__main__":
    pytest.main([__file__])
