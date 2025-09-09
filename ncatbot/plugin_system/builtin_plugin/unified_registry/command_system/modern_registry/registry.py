"""现代化命令注册器

核心注册器类，管理命令定义、路由和执行。
"""

from typing import Callable, Dict, List, Optional, Any, Union, Type
from dataclasses import dataclass, field
import inspect

from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.analyzer.func_analyzer import FuncAnalyser
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.analyzer.specs import CommonadSpec

from .decorators import option, param, option_group
from .exceptions import (
    CommandRegistrationError, CommandNotFoundError, ArgumentError,
    ErrorHandler, ErrorContext
)
from ncatbot.utils import get_log

LOG = get_log(__name__)


class CommandGroup:
    """命令组
    
    支持嵌套的命令组织结构。
    """
    
    def __init__(self, name: str, parent: Optional['CommandGroup'] = None, description: str = ""):
        self.name = name
        self.parent = parent
        self.description = description
        self.commands: Dict[str, Callable] = {}
        self.subgroups: Dict[str, 'CommandGroup'] = {}
    
    def command(self, name: str, 
               aliases: Optional[List[str]] = None,
               description: Optional[str] = None,
    ):
        """命令装饰器"""
        def decorator(func: Callable) -> Callable:
            # 验证装饰器
            command_spec = FuncAnalyser(func).analyze()
            command_spec.alias = aliases
            command_spec.description = description
            command_spec.basename = name
            # 注册命令
            self._register_command(command_spec)
            
            # TODO: 分析部分注解, 自动生成装饰注册器
            
            LOG.debug(f"注册命令: {name} (组: {self.get_full_name()})")
            return func
        
        return decorator
    
    def group(self, name: str, description: str = "") -> 'CommandGroup':
        """创建子命令组"""
        if name in self.subgroups:
            return self.subgroups[name]
        
        subgroup = CommandGroup(name, parent=self, description=description)
        self.subgroups[name] = subgroup
        return subgroup
    
    def _register_command(self, command_spec: CommonadSpec):
        """注册命令"""
        # 检查名称冲突
        if command_spec.basename in self.commands:
            raise CommandRegistrationError(
                command_spec.basename,
                f"命令名称 '{command_spec.basename}' 已存在"
            )
        
        # 注册主名称
        self.commands[command_spec.basename] = command_spec
        
        # 注册别名
        for alias in command_spec.alias:
            self.commands[alias] = command_spec
    
    def get_full_name(self) -> str:
        """获取完整组名"""
        if self.parent:
            return f"{self.parent.get_full_name()}.{self.name}"
        return self.name
    
    def find_command(self, name: str) -> Optional[CommonadSpec]:
        """查找命令"""
        return self.commands.get(name)
    
    def get_all_commands(self) -> Dict[str, CommonadSpec]:  
        """获取所有命令（包括子组）"""
        commands = self.commands.copy()
        for subgroup in self.subgroups.values():
            subgroup_commands = subgroup.get_all_commands()
            # 添加组前缀
            for name, cmd_def in subgroup_commands.items():
                full_name = f"{subgroup.name} {name}"
                commands[full_name] = cmd_def
        return commands


class ModernRegistry:
    """现代化命令注册器
    
    提供完整的命令管理功能。
    """
    
    def __init__(self):
        self.root_group = CommandGroup("root")
        self.error_handler = ErrorHandler()
        
        # 全局配置
        self.config = {
            'prefix': '/',
            'case_sensitive': False,
            'auto_help': True,
            'strict_typing': True,
            'allow_unknown_options': False,
            'debug': False
        }
        
        LOG.debug("现代化命令注册器初始化完成")
    
    def command(self, name: str, **kwargs):
        """注册根级命令"""
        return self.root_group.command(name, **kwargs)
    
    def group(self, name: str, description: str = "") -> CommandGroup:
        """创建根级命令组"""
        return self.root_group.group(name, description)
    
    def configure(self, **kwargs):
        """配置注册器"""
        self.config.update(kwargs)
        self.root_group.configure(**kwargs)
    
    def find_command(self, command_text: str) -> Optional[CommonadSpec]:
        """查找命令
        
        Args:
            command_text: 命令文本，如 "/deploy myapp --env=prod"
            
        Returns:
            Optional[CommonadSpec]: 找到的命令定义
        """
        # 检查并移除前缀
        if not command_text.startswith(self.config['prefix']):
            return None  # 必须有前缀
        
        command_text = command_text[len(self.config['prefix']):]
        
        # 分割命令和参数
        parts = command_text.strip().split()
        if not parts:
            return None
        
        # 尝试匹配命令
        # 先尝试完整匹配，再尝试前缀匹配
        return self._find_command_recursive(parts, self.root_group)
    
    def _find_command_recursive(self, parts: List[str], group: CommandGroup) -> Optional[CommonadSpec]:
        """递归查找命令"""
        if not parts:
            return None
        
        first_part = parts[0]
        
        # 在当前组查找命令
        cmd_def = group.find_command(first_part)
        if cmd_def:
            return cmd_def
        
        # 在子组查找
        if first_part in group.subgroups and len(parts) > 1:
            subgroup = group.subgroups[first_part]
            return self._find_command_recursive(parts[1:], subgroup)
        
        return None
    
    def get_all_commands(self) -> List[CommonadSpec]:
        """获取所有命令"""
        all_commands = self.root_group.get_all_commands()
        # 手动去重（因为别名会重复）
        seen = set()
        unique_commands = []
        for cmd_def in all_commands.values():
            if id(cmd_def) not in seen:
                seen.add(id(cmd_def))
                unique_commands.append(cmd_def)
        return unique_commands
    
    def get_command_names(self) -> List[str]:
        """获取所有命令名称"""
        commands = self.get_all_commands()
        names = []
        for cmd_def in commands:
            names.extend(cmd_def.basename)
        return sorted(list(set(names)))
    
    def validate_command_text(self, command_text: str) -> tuple[bool, Optional[str]]:
        """验证命令文本格式
        
        Returns:
            tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        if not command_text.strip():
            return False, "命令不能为空"
        
        if not command_text.startswith(self.config['prefix']):
            return False, f"命令必须以 '{self.config['prefix']}' 开头"
        
        return True, None
    
    def format_error(self, error: Exception, context: Optional[Dict] = None) -> str:
        """格式化错误信息"""
        if isinstance(error, CommandNotFoundError):
            # 提供可用命令列表
            available_commands = self.get_command_names()
            error.available_commands = available_commands
        
        error_context = None
        if context:
            error_context = ErrorContext(**context)
        
        return self.error_handler.format_error(error, error_context)
    
    # 便捷的装饰器方法（委托给root_group）
    def option(self, *args, **kwargs):
        """选项装饰器"""
        return option(*args, **kwargs)
    
    def param(self, *args, **kwargs):
        """参数装饰器"""
        return param(*args, **kwargs)
    
    def option_group(self, *args, **kwargs):
        """选项组装饰器"""
        return option_group(*args, **kwargs)
    
    # 权限装饰器功能已移除


# 创建全局实例
registry = ModernRegistry()
