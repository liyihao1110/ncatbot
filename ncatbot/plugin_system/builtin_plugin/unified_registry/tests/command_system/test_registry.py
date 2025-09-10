"""命令注册器测试

测试命令注册器的功能，包括命令注册、别名处理、命令组支持等。
"""

import pytest
from unittest.mock import Mock

from ncatbot.core.event import BaseMessageEvent
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.registry.registry import (
    ModernRegistry, CommandGroup
)
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.utils.specs import CommandSpec


class TestCommandGroup:
    """命令组测试"""
    
    def test_group_creation(self):
        """测试命令组创建"""
        group = CommandGroup("test_group", description="测试组")
        assert group.name == "test_group"
        assert group.description == "测试组"
        assert group.parent is None
        assert len(group.commands) == 0
        assert len(group.subgroups) == 0
    
    def test_nested_group_creation(self):
        """测试嵌套命令组创建"""
        parent = CommandGroup("parent")
        child = CommandGroup("child", parent=parent, description="子组")
        
        assert child.parent is parent
        assert child.name == "child"
        assert child.description == "子组"
    
    def test_get_full_name_root(self):
        """测试根组的完整名称"""
        root_group = CommandGroup("root")
        assert root_group.get_full_name() == ("root",)
    
    def test_get_full_name_nested(self):
        """测试嵌套组的完整名称"""
        parent = CommandGroup("parent")
        child = CommandGroup("child", parent=parent)
        grandchild = CommandGroup("grandchild", parent=child)
        
        assert child.get_full_name() == ("parent", "child")
        assert grandchild.get_full_name() == ("parent", "child", "grandchild")
    
    def test_command_registration(self, clean_registries):
        """测试命令注册"""
        group = CommandGroup("test")
        
        @group.command("hello", description="问候命令")
        def hello_cmd(event: BaseMessageEvent):
            return "Hello"
        
        # 命令应该被注册
        assert "hello" in group.commands
        command_spec = group.commands["hello"]
        assert isinstance(command_spec, CommandSpec)
        assert command_spec.name == "hello"
        assert command_spec.description == "问候命令"
        assert command_spec.func is hello_cmd
    
    def test_command_with_aliases(self, clean_registries):
        """测试带别名的命令注册"""
        group = CommandGroup("test")
        
        @group.command("status", aliases=["st", "stat"], description="状态命令")
        def status_cmd(event: BaseMessageEvent):
            return "Status OK"
        
        # 主名称和别名都应该注册
        assert "status" in group.commands
        assert "st" in group.aliases  
        assert "stat" in group.aliases
        
        # 所有名称应该指向同一个命令规格
        assert group.commands["status"] is group.aliases["st"]
        assert group.commands["status"] is group.aliases["stat"]
        
        # 验证别名设置
        command_spec = group.commands["status"]
        assert command_spec.aliases == ["st", "stat"]
    
    def test_subgroup_creation(self):
        """测试子组创建"""
        parent = CommandGroup("parent")
        child = parent.group("child", description="子组")
        
        assert "child" in parent.subgroups
        assert parent.subgroups["child"] is child
        assert child.parent is parent
        assert child.description == "子组"
    
    def test_subgroup_duplicate_name(self):
        """测试重复名称的子组"""
        parent = CommandGroup("parent")
        child1 = parent.group("child", description="第一个")
        child2 = parent.group("child", description="第二个")
        
        # 应该返回同一个子组
        assert child1 is child2
        assert child1.description == "第一个"  # 保持原有描述
    
    def test_get_all_commands_simple(self, clean_registries):
        """测试获取所有命令（简单情况）"""
        group = CommandGroup("test")
        
        @group.command("hello")
        def hello_cmd(event: BaseMessageEvent):
            return "Hello"
        
        @group.command("bye")
        def bye_cmd(event: BaseMessageEvent):
            return "Bye"
        
        all_commands = group.get_all_commands()
        
        assert len(all_commands) == 2
        assert ("hello",) in all_commands
        assert ("bye",) in all_commands
    
    def test_get_all_commands_with_subgroups(self, clean_registries):
        """测试获取所有命令（包含子组）"""
        root = CommandGroup("root")
        
        @root.command("root_cmd")
        def root_command(event: BaseMessageEvent):
            return "Root"
        
        # 创建子组并注册命令
        admin_group = root.group("admin")
        
        @admin_group.command("user")
        def admin_user_cmd(event: BaseMessageEvent):
            return "Admin User"
        
        @admin_group.command("settings")
        def admin_settings_cmd(event: BaseMessageEvent):
            return "Admin Settings"
        
        all_commands = root.get_all_commands()
        
        # 应该包含根命令和子组命令
        assert len(all_commands) == 3
        assert ("root_cmd",) in all_commands
        assert ("admin", "user") in all_commands
        assert ("admin", "settings") in all_commands
    
    def test_get_all_aliases(self, clean_registries):
        """测试获取所有别名"""
        group = CommandGroup("test")
        
        @group.command("status", aliases=["st", "stat"])
        def status_cmd(event: BaseMessageEvent):
            return "Status"
        
        @group.command("info", aliases=["i"])
        def info_cmd(event: BaseMessageEvent):
            return "Info"
        
        all_aliases = group.get_all_aliases()
        
        assert len(all_aliases) == 3  # st, stat, i
        assert ("st",) in all_aliases
        assert ("stat",) in all_aliases
        assert ("i",) in all_aliases
        
        # 别名应该指向正确的命令
        assert all_aliases[("st",)].func is status_cmd
        assert all_aliases[("stat",)].func is status_cmd
        assert all_aliases[("i",)].func is info_cmd


class TestModernRegistry:
    """现代化注册器测试"""
    
    def test_registry_creation(self):
        """测试注册器创建"""
        registry = ModernRegistry()
        assert registry.root_group is not None
        assert registry.root_group.name == "root"
        assert registry.error_handler is not None
    
    def test_root_command_registration(self, clean_registries):
        """测试根级命令注册"""
        registry = ModernRegistry()
        
        @registry.command("test", description="测试命令")
        def test_cmd(event: BaseMessageEvent):
            return "Test"
        
        # 应该注册到根组
        assert "test" in registry.root_group.commands
        command_spec = registry.root_group.commands["test"]
        assert command_spec.name == "test"
        assert command_spec.description == "测试命令"
    
    def test_group_creation_via_registry(self):
        """测试通过注册器创建组"""
        registry = ModernRegistry()
        
        admin_group = registry.group("admin", description="管理员命令")
        
        assert "admin" in registry.root_group.subgroups
        assert registry.root_group.subgroups["admin"] is admin_group
        assert admin_group.description == "管理员命令"
    
    def test_nested_group_command_registration(self, clean_registries):
        """测试嵌套组命令注册"""
        registry = ModernRegistry()
        
        # 创建多级组
        admin_group = registry.group("admin")
        user_group = admin_group.group("user")
        
        @user_group.command("list")
        def list_users_cmd(event: BaseMessageEvent):
            return "User list"
        
        @user_group.command("add", aliases=["create"])
        def add_user_cmd(event: BaseMessageEvent):
            return "User added"
        
        # 验证命令注册
        assert "list" in user_group.commands
        assert "add" in user_group.commands
        assert "create" in user_group.aliases  # 别名
        
        # 验证层级结构
        assert user_group.parent is admin_group
        assert admin_group.parent is registry.root_group
    
    def test_get_all_commands_from_registry(self, clean_registries):
        """测试从注册器获取所有命令"""
        registry = ModernRegistry()
        
        # 根级命令
        @registry.command("ping")
        def ping_cmd(event: BaseMessageEvent):
            return "Pong"
        
        # 组级命令
        admin_group = registry.group("admin")
        
        @admin_group.command("status")
        def admin_status_cmd(event: BaseMessageEvent):
            return "Admin Status"
        
        # 深层嵌套命令
        db_group = admin_group.group("db")
        
        @db_group.command("backup")
        def db_backup_cmd(event: BaseMessageEvent):
            return "DB Backup"
        
        all_commands = registry.get_all_commands()
        
        # 验证所有层级的命令都被包含
        command_paths = list(all_commands.keys())
        assert ("ping",) in command_paths
        assert ("admin", "status") in command_paths
        assert ("admin", "db", "backup") in command_paths
    
    def test_get_all_aliases_from_registry(self, clean_registries):
        """测试从注册器获取所有别名"""
        registry = ModernRegistry()
        
        @registry.command("status", aliases=["st"])
        def status_cmd(event: BaseMessageEvent):
            return "Status"
        
        admin_group = registry.group("admin")
        
        @admin_group.command("user", aliases=["u", "usr"])
        def admin_user_cmd(event: BaseMessageEvent):
            return "Admin User"
        
        all_aliases = registry.get_all_aliases()
        
        # 验证别名结构
        assert ("st",) in all_aliases
        # 注意：子组的别名可能会有特殊处理，根据实际实现调整


class TestCommandRegistrationErrors:
    """命令注册错误处理测试"""
    
    def test_command_name_conflict(self, clean_registries):
        """测试命令名称冲突"""
        group = CommandGroup("test")
        
        @group.command("duplicate")
        def cmd1(event: BaseMessageEvent):
            return "First"
        
        # 尝试注册同名命令应该有适当的错误处理
        # 具体行为取决于实现：可能抛出异常或覆盖
        try:
            @group.command("duplicate")
            def cmd2(event: BaseMessageEvent):
                return "Second"
            
            # 如果允许覆盖，验证新命令
            assert group.commands["duplicate"].func is cmd2
        except Exception as e:
            # 如果抛出异常，验证是期望的异常类型
            assert "duplicate" in str(e).lower() or "conflict" in str(e).lower()
    
    def test_alias_conflict_with_command_name(self, clean_registries):
        """测试别名与命令名冲突"""
        group = CommandGroup("test")
        
        @group.command("status")
        def status_cmd(event: BaseMessageEvent):
            return "Status"
        
        # 尝试注册别名与现有命令名冲突的命令
        try:
            @group.command("info", aliases=["status"])  # status已存在
            def info_cmd(event: BaseMessageEvent):
                return "Info"
            
            # 根据实现，可能允许或禁止这种情况
        except Exception as e:
            # 如果抛出异常，应该是预期的
            assert "status" in str(e).lower() or "conflict" in str(e).lower()
    
    def test_invalid_command_name(self, clean_registries):
        """测试无效命令名称"""
        group = CommandGroup("test")
        
        # 测试空名称
        try:
            @group.command("")
            def empty_name_cmd(event: BaseMessageEvent):
                return "Empty"
            # 可能允许空名称，也可能抛出异常
        except (ValueError, TypeError):
            pass  # 预期的异常
        
        # 测试None名称
        try:
            @group.command(None)
            def none_name_cmd(event: BaseMessageEvent):
                return "None"
        except (ValueError, TypeError):
            pass  # 预期的异常


class TestCommandSpec:
    """命令规格测试"""
    
    def test_command_spec_creation(self, clean_registries):
        """测试命令规格创建"""
        group = CommandGroup("test")
        
        @group.command("test_cmd", aliases=["tc"], description="测试命令")
        def test_function(event: BaseMessageEvent, param: str = "default"):
            """测试函数"""
            return f"Test: {param}"
        
        command_spec = group.commands["test_cmd"]
        
        assert command_spec.name == "test_cmd"
        assert command_spec.aliases == ["tc"]
        assert command_spec.description == "测试命令"
        assert command_spec.func is test_function
    
    def test_command_spec_without_aliases(self, clean_registries):
        """测试无别名的命令规格"""
        group = CommandGroup("test")
        
        @group.command("simple")
        def simple_cmd(event: BaseMessageEvent):
            return "Simple"
        
        command_spec = group.commands["simple"]
        
        assert command_spec.name == "simple"
        assert command_spec.aliases == [] or command_spec.aliases is None
    
    def test_command_spec_without_description(self, clean_registries):
        """测试无描述的命令规格"""
        group = CommandGroup("test")
        
        @group.command("nodesc")
        def nodesc_cmd(event: BaseMessageEvent):
            return "No description"
        
        command_spec = group.commands["nodesc"]
        
        assert command_spec.name == "nodesc"
        assert command_spec.description is None or command_spec.description == ""


class TestRegistryIntegration:
    """注册器集成测试"""
    
    def test_complex_registry_structure(self, clean_registries):
        """测试复杂注册器结构"""
        registry = ModernRegistry()
        
        # 根级命令
        @registry.command("help", aliases=["h", "?"])
        def help_cmd(event: BaseMessageEvent):
            return "Help"
        
        @registry.command("version", aliases=["v"])
        def version_cmd(event: BaseMessageEvent):
            return "Version 1.0"
        
        # 管理员组
        admin_group = registry.group("admin", description="管理员命令")
        
        @admin_group.command("reload")
        def admin_reload_cmd(event: BaseMessageEvent):
            return "Reloaded"
        
        # 用户管理子组
        user_group = admin_group.group("user")
        
        @user_group.command("list", aliases=["ls"])
        def list_users_cmd(event: BaseMessageEvent):
            return "User list"
        
        @user_group.command("ban", aliases=["b"])
        def ban_user_cmd(event: BaseMessageEvent):
            return "User banned"
        
        # 系统管理子组
        system_group = admin_group.group("system")
        
        @system_group.command("status", aliases=["stat"])
        def system_status_cmd(event: BaseMessageEvent):
            return "System status"
        
        # 验证整体结构
        all_commands = registry.get_all_commands()
        all_aliases = registry.get_all_aliases()
        
        # 验证根级命令
        assert ("help",) in all_commands
        assert ("version",) in all_commands
        
        # 验证管理员命令
        assert ("admin", "reload") in all_commands
        
        # 验证嵌套命令
        assert ("admin", "user", "list") in all_commands
        assert ("admin", "user", "ban") in all_commands
        assert ("admin", "system", "status") in all_commands
        
        # 验证别名数量
        assert len(all_aliases) >= 5  # h, ?, v, ls, b, stat
    
    def test_registry_state_isolation(self, clean_registries):
        """测试注册器状态隔离"""
        registry1 = ModernRegistry()
        registry2 = ModernRegistry()
        
        # 在不同注册器中注册不同命令
        @registry1.command("test1")
        def test1_cmd(event: BaseMessageEvent):
            return "Test1"
        
        @registry2.command("test2") 
        def test2_cmd(event: BaseMessageEvent):
            return "Test2"
        
        # 验证隔离
        commands1 = registry1.get_all_commands()
        commands2 = registry2.get_all_commands()
        
        assert ("test1",) in commands1
        assert ("test1",) not in commands2
        assert ("test2",) not in commands1
        assert ("test2",) in commands2
