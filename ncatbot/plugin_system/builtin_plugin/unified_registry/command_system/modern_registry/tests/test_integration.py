"""综合集成测试

测试完整的命令系统工作流程，包括：
- 真实命令注册
- Mock事件解析
- 命令调用和参数传递
- 互斥选项验证
- 错误处理流程
- 多类型参数处理
"""

import pytest
from unittest.mock import Mock, patch
from typing import Union, Optional
from dataclasses import dataclass

from .. import registry as modern_registry
from ..type_system import CommonUnionTypes
from ..exceptions import (
    CommandNotFoundError, ArgumentError, OptionError,
    MutuallyExclusiveError, ValidationError, TypeConversionError
)
from .conftest import MockEvent, MockMessageSegment
from ncatbot.core.event.message_segment.message_segment import MessageSegment


@dataclass
class MockAt(MockMessageSegment):
    """模拟@用户消息段"""
    qq: int = 123456
    
    def __post_init__(self):
        self.msg_seg_type = "at"


@dataclass  
class MockImage(MockMessageSegment):
    """模拟图片消息段"""
    file: str = "test.jpg"
    
    def __post_init__(self):
        self.msg_seg_type = "image"


@dataclass
class MockText(MockMessageSegment):
    """模拟文本消息段"""
    text: str = "hello"
    
    def __post_init__(self):
        self.msg_seg_type = "text"


class TestIntegrationScenarios:
    """综合测试场景"""
    
    def setup_method(self):
        """每个测试前重置注册器"""
        # 创建新的注册器实例避免测试间干扰
        from ..registry import ModernRegistry
        self.registry = ModernRegistry()
        self.registry.configure(prefix="/", case_sensitive=False)
        
        # 存储调用结果用于验证
        self.call_results = []
        
    def test_basic_command_flow(self):
        """测试基础命令流程"""
        # 注册简单命令
        @self.registry.command("hello", description="简单问候")
        def hello_cmd(event):
            self.call_results.append(("hello", event, {}))
            return "Hello World!"
        
        # 测试命令查找
        cmd_def = self.registry.find_command("/hello")
        assert cmd_def is not None
        assert cmd_def.name == "hello"
        assert cmd_def.description == "简单问候"
        
        # 模拟调用
        mock_event = MockEvent()
        result = cmd_def.func(mock_event)
        
        assert result == "Hello World!"
        assert len(self.call_results) == 1
        assert self.call_results[0][0] == "hello"
        assert self.call_results[0][1] is mock_event
    
    def test_command_with_positional_parameters(self):
        """测试带位置参数的命令"""
        @self.registry.command("greet", description="个性化问候")
        def greet_cmd(event, name: str, age: int = 18):
            self.call_results.append(("greet", event, {"name": name, "age": age}))
            return f"Hello {name}, you are {age} years old!"
        
        cmd_def = self.registry.find_command("/greet")
        assert cmd_def is not None
        
        # 验证参数规格
        pos_params = cmd_def.get_positional_parameters()
        assert len(pos_params) == 2
        
        name_param = next(p for p in pos_params if p.name == "name")
        age_param = next(p for p in pos_params if p.name == "age")
        
        assert name_param.type == str
        assert name_param.required is True
        assert age_param.type == int
        assert age_param.default == 18
        assert age_param.required is False
    
    def test_command_with_options(self):
        """测试带选项的命令"""
        @self.registry.command("deploy", description="部署应用")
        @self.registry.option("-v", "--verbose", help="详细输出")
        @self.registry.option("-f", "--force", help="强制部署")
        @self.registry.option("--env", type=str, default="dev", help="环境")
        def deploy_cmd(event, app_name: str, verbose=False, force=False, env="dev"):
            self.call_results.append(("deploy", event, {
                "app_name": app_name,
                "verbose": verbose, 
                "force": force,
                "env": env
            }))
            return f"Deploying {app_name} to {env}"
        
        cmd_def = self.registry.find_command("/deploy")
        assert cmd_def is not None
        assert len(cmd_def.options) == 3
        
        # 验证选项规格
        option_names = {opt.long_name or opt.short_name for opt in cmd_def.options}
        assert "--verbose" in option_names
        assert "--force" in option_names  
        assert "--env" in option_names
    
    def test_mutually_exclusive_options(self):
        """测试互斥选项"""
        @self.registry.command("backup", description="备份数据")
        @self.registry.option_group(1, name="输出格式", mutually_exclusive=True, required=True)
        @self.registry.option("--json", group=1, help="JSON格式")
        @self.registry.option("--xml", group=1, help="XML格式")
        @self.registry.option("--yaml", group=1, help="YAML格式")
        def backup_cmd(event, json=False, xml=False, yaml=False):
            format_type = "json" if json else "xml" if xml else "yaml" if yaml else "none"
            self.call_results.append(("backup", event, {"format": format_type}))
            return f"Backup in {format_type} format"
        
        cmd_def = self.registry.find_command("/backup")
        assert cmd_def is not None
        assert len(cmd_def.option_groups) == 1
        
        # 验证选项组
        group = cmd_def.option_groups[0]
        assert group.name == "输出格式"
        assert group.mutually_exclusive is True
        assert group.required is True
        assert len(group.options) == 3
    
    def test_multi_type_parameters(self):
        """测试多类型参数"""
        @self.registry.command("send", description="发送消息")
        @self.registry.param("target", type=CommonUnionTypes.USER_IDENTIFIER, help="目标用户")
        @self.registry.param("content", type=CommonUnionTypes.STR_OR_IMAGE, help="消息内容")
        def send_cmd(event, target: Union[str, MessageSegment], 
                    content: Union[str, MessageSegment]):
            self.call_results.append(("send", event, {
                "target": target,
                "content": content,
                "target_type": type(target).__name__,
                "content_type": type(content).__name__
            }))
            return f"Message sent to {target}"
        
        cmd_def = self.registry.find_command("/send")
        assert cmd_def is not None
        
        # 验证参数规格  
        named_params = cmd_def.get_named_parameters()
        assert len(named_params) == 2
        
        target_param = next(p for p in named_params if p.name == "target")
        content_param = next(p for p in named_params if p.name == "content")
        
        assert target_param.is_multi_type()
        assert content_param.is_multi_type()
        
        # 验证联合类型
        target_union = target_param.get_union_type()
        content_union = content_param.get_union_type()
        
        assert str in target_union.types
        assert MessageSegment in target_union.types
        assert str in content_union.types
        assert MessageSegment in content_union.types
    
    def test_nested_command_groups(self):
        """测试嵌套命令组"""
        # 创建管理员命令组
        admin_group = self.registry.group("admin", description="管理员命令")
        
        # 创建用户管理子组
        user_group = admin_group.group("user", description="用户管理")
        
        @user_group.command("create", description="创建用户")
        def create_user_cmd(event, username: str, email: str):
            self.call_results.append(("create_user", event, {
                "username": username,
                "email": email
            }))
            return f"User {username} created"
        
        @user_group.command("delete", description="删除用户")
        def delete_user_cmd(event, user_id: int):
            self.call_results.append(("delete_user", event, {"user_id": user_id}))
            return f"User {user_id} deleted"
        
        # 验证嵌套结构
        assert "admin" in self.registry.root_group.subgroups
        assert "user" in admin_group.subgroups
        assert user_group.parent is admin_group
        assert admin_group.parent is self.registry.root_group
        
        # 验证命令查找
        create_cmd = self.registry.find_command("/admin user create")
        delete_cmd = self.registry.find_command("/admin user delete")
        
        assert create_cmd is not None
        assert delete_cmd is not None
        assert create_cmd.name == "create"
        assert delete_cmd.name == "delete"
    
    def test_command_aliases(self):
        """测试命令别名"""
        @self.registry.command("status", aliases=["st", "stat", "info"], description="查看状态")
        def status_cmd(event):
            self.call_results.append(("status", event, {}))
            return "System status: OK"
        
        # 测试所有别名都能找到同一个命令
        cmd1 = self.registry.find_command("/status")
        cmd2 = self.registry.find_command("/st")
        cmd3 = self.registry.find_command("/stat")
        cmd4 = self.registry.find_command("/info")
        
        assert cmd1 is not None
        assert cmd2 is not None
        assert cmd3 is not None
        assert cmd4 is not None
        
        # 都应该是同一个命令定义对象
        assert cmd1 is cmd2 is cmd3 is cmd4
        assert cmd1.name == "status"


class TestErrorHandlingScenarios:
    """错误处理测试场景"""
    
    def setup_method(self):
        """每个测试前重置注册器"""
        from ..registry import ModernRegistry
        self.registry = ModernRegistry()
        self.registry.configure(prefix="/")
    
    def test_command_not_found_error(self):
        """测试命令不存在错误"""
        @self.registry.command("deploy")
        def deploy_cmd(event):
            pass
        
        @self.registry.command("backup")  
        def backup_cmd(event):
            pass
        
        # 测试不存在的命令
        result = self.registry.find_command("/deploi")  # 拼写错误
        assert result is None
        
        # 测试错误格式化
        available_commands = self.registry.get_command_names()
        error = CommandNotFoundError("deploi", available_commands)
        formatted = self.registry.format_error(error)
        
        assert "❌" in formatted
        assert "deploi" in formatted
        assert "deploy" in formatted  # 应该建议相似的命令
    
    def test_missing_prefix_error(self):
        """测试缺少前缀错误"""
        @self.registry.command("test")
        def test_cmd(event):
            pass
        
        # 没有前缀的命令应该找不到
        result = self.registry.find_command("test")
        assert result is None
        
        # 验证命令文本验证
        valid, error = self.registry.validate_command_text("test")
        assert valid is False
        assert "必须以" in error and "/" in error
    
    def test_type_conversion_scenarios(self):
        """测试类型转换场景"""
        @self.registry.command("age_check")
        def age_check_cmd(event, age: int):
            return f"Age: {age}"
        
        cmd_def = self.registry.find_command("/age_check")
        assert cmd_def is not None
        
        # 验证参数类型
        pos_params = cmd_def.get_positional_parameters()
        age_param = next(p for p in pos_params if p.name == "age")
        assert age_param.type == int
    
    def test_multi_type_conversion_error_scenarios(self):
        """测试多类型转换错误场景"""
        @self.registry.command("flexible")
        @self.registry.param("input", type=[str, int], help="灵活输入")
        def flexible_cmd(event, input: Union[str, int]):
            return f"Input: {input} (type: {type(input).__name__})"
        
        cmd_def = self.registry.find_command("/flexible")
        assert cmd_def is not None
        
        # 验证多类型参数
        named_params = cmd_def.get_named_parameters()
        input_param = next(p for p in named_params if p.name == "input")
        assert input_param.is_multi_type()
        
        union_type = input_param.get_union_type()
        assert str in union_type.types
        assert int in union_type.types


class TestComplexWorkflows:
    """复杂工作流测试"""
    
    def setup_method(self):
        """每个测试前重置注册器"""
        from ..registry import ModernRegistry
        self.registry = ModernRegistry()
        self.call_log = []
    
    def test_comprehensive_command_system(self):
        """测试完整的命令系统工作流"""
        
        # 1. 创建复杂的命令结构
        admin_group = self.registry.group("admin", description="管理员功能")
        
        @admin_group.command("deploy", description="部署系统", aliases=["dp"])
        @self.registry.option("-e", "--env", type=str, default="dev", help="部署环境")
        @self.registry.option("-v", "--verbose", help="详细日志")
        @self.registry.option("--dry-run", help="试运行")
        @self.registry.option_group(1, name="部署模式", mutually_exclusive=True)
        @self.registry.option("--fast", group=1, help="快速部署")
        @self.registry.option("--safe", group=1, help="安全部署")
        @self.registry.param("target", type=CommonUnionTypes.STR_OR_AT, help="部署目标")
        def deploy_cmd(event, app_name: str, target, env="dev", verbose=False, 
                      dry_run=False, fast=False, safe=False):
            self.call_log.append({
                "command": "admin.deploy",
                "app_name": app_name,
                "target": target,
                "env": env,
                "verbose": verbose,
                "dry_run": dry_run,
                "fast": fast,
                "safe": safe,
                "target_type": type(target).__name__
            })
            return f"Deploying {app_name} to {env}"
        
        # 2. 创建多类型参数命令
        @self.registry.command("notify", description="发送通知")
        @self.registry.param("recipient", type=CommonUnionTypes.USER_IDENTIFIER, help="接收者")
        @self.registry.param("message", type=CommonUnionTypes.STR_OR_IMAGE, help="消息内容")
        @self.registry.option("--urgent", help="紧急通知")
        @self.registry.option("--delay", type=int, default=0, help="延迟秒数")
        def notify_cmd(event, recipient, message, urgent=False, delay=0):
            self.call_log.append({
                "command": "notify",
                "recipient": recipient,
                "message": message,
                "urgent": urgent,
                "delay": delay,
                "recipient_type": type(recipient).__name__,
                "message_type": type(message).__name__
            })
            return "Notification sent"
        
        # 3. 验证命令注册
        deploy_cmd_def = self.registry.find_command("/admin deploy")
        deploy_alias_def = self.registry.find_command("/admin dp")
        notify_cmd_def = self.registry.find_command("/notify")
        
        assert deploy_cmd_def is not None
        assert deploy_alias_def is not None
        assert notify_cmd_def is not None
        assert deploy_cmd_def is deploy_alias_def  # 别名指向同一个命令
        
        # 4. 验证命令结构
        assert len(deploy_cmd_def.options) == 5
        assert len(deploy_cmd_def.option_groups) == 1
        assert len(deploy_cmd_def.get_positional_parameters()) == 1
        assert len(deploy_cmd_def.get_named_parameters()) == 1
        
        assert len(notify_cmd_def.options) == 2
        assert len(notify_cmd_def.get_named_parameters()) == 2
        
        # 5. 验证选项组
        deploy_group = deploy_cmd_def.option_groups[0]
        assert deploy_group.mutually_exclusive is True
        assert deploy_group.name == "部署模式"
        assert len(deploy_group.options) == 2
        
        # 6. 验证多类型参数
        notify_params = notify_cmd_def.get_named_parameters()
        recipient_param = next(p for p in notify_params if p.name == "recipient")
        message_param = next(p for p in notify_params if p.name == "message")
        
        assert recipient_param.is_multi_type()
        assert message_param.is_multi_type()
        
        # 7. 模拟复杂调用场景
        mock_event = MockEvent()
        mock_at = MockAt(qq=123456)
        mock_image = MockImage(file="notification.jpg")
        
        # 调用带多种参数的命令
        deploy_result = deploy_cmd_def.func(
            mock_event, "myapp", mock_at, 
            env="prod", verbose=True, safe=True
        )
        
        notify_result = notify_cmd_def.func(
            mock_event, mock_at, mock_image,
            urgent=True, delay=10
        )
        
        # 8. 验证调用结果
        assert deploy_result == "Deploying myapp to prod"
        assert notify_result == "Notification sent"
        assert len(self.call_log) == 2
        
        # 验证部署命令调用记录
        deploy_log = self.call_log[0]
        assert deploy_log["command"] == "admin.deploy"
        assert deploy_log["app_name"] == "myapp"
        assert deploy_log["env"] == "prod"
        assert deploy_log["verbose"] is True
        assert deploy_log["safe"] is True
        assert deploy_log["target_type"] == "MockAt"
        
        # 验证通知命令调用记录
        notify_log = self.call_log[1]
        assert notify_log["command"] == "notify"
        assert notify_log["urgent"] is True
        assert notify_log["delay"] == 10
        assert notify_log["recipient_type"] == "MockAt"
        assert notify_log["message_type"] == "MockImage"
    
    def test_error_handling_workflow(self):
        """测试错误处理工作流"""
        
        # 1. 注册带验证的命令
        @self.registry.command("validate")
        @self.registry.param("score", type=int, validator=lambda x: 0 <= x <= 100, help="分数(0-100)")
        def validate_cmd(event, score: int):
            return f"Score: {score}"
        
        # 2. 注册互斥选项命令
        @self.registry.command("format")
        @self.registry.option_group(1, mutually_exclusive=True, required=True)
        @self.registry.option("--json", group=1)
        @self.registry.option("--xml", group=1)
        def format_cmd(event, json=False, xml=False):
            return "formatted"
        
        # 3. 验证命令查找错误
        unknown_cmd = self.registry.find_command("/unknown")
        assert unknown_cmd is None
        
        # 4. 验证前缀错误
        no_prefix_cmd = self.registry.find_command("validate")
        assert no_prefix_cmd is None
        
        # 5. 获取所有命令用于错误报告
        all_commands = self.registry.get_all_commands()
        command_names = self.registry.get_command_names()
        
        assert len(all_commands) >= 2
        assert "validate" in command_names
        assert "format" in command_names
        
        # 6. 测试错误格式化
        error = CommandNotFoundError("validat", command_names)
        formatted_error = self.registry.format_error(error)
        
        assert isinstance(formatted_error, str)
        assert "❌" in formatted_error
        assert "validat" in formatted_error


class TestPerformanceAndScaling:
    """性能和扩展性测试"""
    
    def setup_method(self):
        """每个测试前重置注册器"""
        from ..registry import ModernRegistry
        self.registry = ModernRegistry()
    
    def test_large_command_registry(self):
        """测试大量命令注册的性能"""
        
        # 注册多个命令组和命令
        for group_idx in range(5):
            group = self.registry.group(f"group{group_idx}", description=f"第{group_idx}组")
            
            for cmd_idx in range(10):
                cmd_name = f"cmd{cmd_idx}"
                
                @group.command(cmd_name, description=f"命令{cmd_idx}")
                @self.registry.option(f"--opt{cmd_idx}", help=f"选项{cmd_idx}")
                @self.registry.param(f"param{cmd_idx}", type=str, help=f"参数{cmd_idx}")
                def dynamic_cmd(event, **kwargs):
                    return f"执行 {cmd_name}"
        
        # 验证命令数量
        all_commands = self.registry.get_all_commands()
        assert len(all_commands) == 50  # 5组 × 10命令
        
        # 验证查找性能（应该很快）
        import time
        start_time = time.time()
        
        for group_idx in range(5):
            for cmd_idx in range(10):
                cmd_path = f"/group{group_idx} cmd{cmd_idx}"
                cmd_def = self.registry.find_command(cmd_path)
                assert cmd_def is not None
        
        end_time = time.time()
        lookup_time = end_time - start_time
        
        # 50个命令查找应该在合理时间内完成（< 0.1秒）
        assert lookup_time < 0.1
        
        # 验证命令名称获取（去重后的名称）
        command_names = self.registry.get_command_names()
        assert len(command_names) == 10  # 只有10个不同的命令名（cmd0-cmd9）
        assert set(command_names) == {f'cmd{i}' for i in range(10)}
    
    def test_deep_nesting_performance(self):
        """测试深层嵌套的性能"""
        
        # 创建深层嵌套结构
        current_group = self.registry
        group_path = []
        
        for depth in range(5):
            group_name = f"level{depth}"
            group_path.append(group_name)
            current_group = current_group.group(group_name, description=f"第{depth}层")
        
        # 在最深层添加命令
        @current_group.command("deep", description="深层命令")
        def deep_cmd(event):
            return "深层执行"
        
        # 验证深层查找
        deep_path = "/" + " ".join(group_path) + " deep"
        cmd_def = self.registry.find_command(deep_path)
        
        assert cmd_def is not None
        assert cmd_def.name == "deep"
        
        # 验证路径构建
        assert current_group.get_full_name() == ".".join(["root"] + group_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
