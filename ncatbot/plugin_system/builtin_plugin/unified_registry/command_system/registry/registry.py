"""现代化命令注册器

核心注册器类，管理命令定义、路由和执行。
"""

from typing import Callable, Dict, List, Optional

from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.analyzer.func_analyzer import FuncAnalyser
from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.utils import CommandSpec

from .exceptions import (
    CommandRegistrationError,
    ErrorHandler
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
        self.commands: Dict[str, CommandSpec] = {}
        self.subgroups: Dict[str, 'CommandGroup'] = {}
    
    def command(self, name: str, 
               aliases: Optional[List[str]] = None,
               description: Optional[str] = None,):
        """命令装饰器"""
        def decorator(func: Callable) -> Callable:
            # 验证装饰器
            command_spec = FuncAnalyser(func).analyze()
            command_spec.aliases = aliases
            command_spec.description = description
            command_spec.name = name
            # 注册命令
            self._register_command(command_spec)
                        
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
    
    def _register_command(self, command_spec: CommandSpec):
        """注册命令"""
        # 检查名称冲突
        if command_spec.name in self.commands:
            raise CommandRegistrationError(
                command_spec.name,
                f"命令名称 '{command_spec.name}' 已存在"
            )
        
        # 注册主名称
        self.commands[command_spec.name] = command_spec
        
        # 注册别名
        for alias in command_spec.aliases:
            self.commands[alias] = command_spec
    
    def get_full_name(self) -> str:
        """获取完整组名"""
        if self.parent:
            return f"{self.parent.get_full_name()} {self.name}"
        return self.name
    
    def get_all_commands(self) -> Dict[str, CommandSpec]:  
        """获取所有命令（包括子组）"""
        commands = self.commands.copy()
        for subgroup in self.subgroups.values():
            subgroup_commands = subgroup.get_all_commands()
            # 添加组前缀
            for name, cmd_def in subgroup_commands.items():
                full_name = f"{subgroup.name} {name}"
                commands[full_name] = cmd_def
        return commands

    def get_all_aliases(self) -> Dict[str, CommandSpec]:
        """获取所有别名"""
        aliases = {}
        for command_group in self.subgroups.values():
            aliases.update(command_group.get_all_aliases())
        for command in self.commands.values():
            for alias in command.aliases:
                aliases[alias] = command
        return aliases


class ModernRegistry:
    """现代化命令注册器
    
    提供完整的命令管理功能。
    """
    
    def __init__(self):
        self.root_group = CommandGroup("root")
        self.error_handler = ErrorHandler()
        LOG.debug("现代化命令注册器初始化完成")
    
    def command(self, name: str, **kwargs):
        """注册根级命令"""
        return self.root_group.command(name, **kwargs)
    
    def group(self, name: str, description: str = "") -> CommandGroup:
        """创建根级命令组"""
        return self.root_group.group(name, description)
    
    def get_all_commands(self) -> Dict[str, CommandSpec]:
        """获取所有命令"""
        return self.root_group.get_all_commands()
    
    def get_all_aliases(self) -> Dict[str, CommandSpec]:
        """获取所有别名"""
        return self.root_group.get_all_aliases()

# 创建全局实例
command_registry = ModernRegistry()
