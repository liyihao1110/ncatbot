"""现代化命令注册器

核心注册器类，管理命令定义、路由和执行。
"""

from typing import Callable, Dict, List, Optional, Tuple
from ..analyzer.func_analyzer import FuncAnalyser
from ..utils import (
    CommandRegistrationError,
    ErrorHandler,
    CommandSpec,
)
from ncatbot.utils import get_log

LOG = get_log(__name__)


class CommandGroup:
    """命令组

    支持嵌套的命令组织结构。
    """

    def __init__(
        self,
        name: str,
        parent: Optional["CommandGroup"] = None,
        description: str = "",
        prefixes: Optional[List[str]] = None,
    ):
        self.name = name
        self.parent = parent
        self.description = description
        self.commands: Dict[Tuple[str, ...], CommandSpec] = {}
        self.aliases: Dict[Tuple[str, ...], CommandSpec] = {}
        self.subgroups: Dict[str, "CommandGroup"] = {}

        # 可继承的配置
        self.prefixes: List[str] = prefixes

    def command(
        self,
        name: str,
        aliases: Optional[List[str]] = None,
        description: Optional[str] = None,
        prefixes: Optional[List[str]] = None,
    ):
        """命令装饰器"""

        def decorator(func: Callable) -> Callable:
            # 验证装饰器 - 延迟导入避免循环导入

            command_spec = FuncAnalyser(func).analyze()
            command_spec.aliases = aliases if aliases else []
            command_spec.description = description if description else ""
            command_spec.name = name
            command_spec.prefixes = prefixes if prefixes else self.prefixes
            func.__is_command__ = True
            # 注册命令
            self._register_command(command_spec)

            LOG.debug(f"注册命令: {name} (组: {self.get_full_name()})")
            return func

        return decorator

    def group(
        self, name: str, description: str = "", prefixes: Optional[List[str]] = None
    ) -> "CommandGroup":
        """创建子命令组"""
        if name in self.subgroups:
            return self.subgroups[name]
        subgroup = CommandGroup(
            name,
            parent=self,
            description=description,
            prefixes=prefixes if prefixes else self.prefixes,
        )
        self.subgroups[name] = subgroup
        return subgroup

    def set_prefixes(self, prefixes: List[str]):
        """设置前缀"""
        self.prefixes = prefixes

    def _register_command(self, command_spec: CommandSpec):
        """注册命令"""
        # 检查名称冲突
        if command_spec.name in self.commands:
            raise CommandRegistrationError(
                command_spec.name, f"命令名称 '{command_spec.name}' 已存在"
            )

        # 注册主名称
        self.commands[command_spec.name] = command_spec

        # 注册别名
        for aliases in command_spec.aliases:
            self.aliases[aliases] = command_spec

    def get_full_name(self) -> Tuple[str, ...]:
        """获取完整组名"""
        if self.parent:
            return self.parent.get_full_name() + (self.name,)
        return (self.name,)

    def get_all_commands(self) -> Dict[Tuple[str, ...], CommandSpec]:
        """获取所有命令（包括子组）"""
        commands = {(k,): v for k, v in self.commands.items()}
        for subgroup in self.subgroups.values():
            subgroup_commands = subgroup.get_all_commands()
            # 添加组前缀
            for name, cmd_def in subgroup_commands.items():
                full_name = (subgroup.name,) + name
                commands[full_name] = cmd_def
        return commands

    def get_all_aliases(self) -> Dict[Tuple[str, ...], CommandSpec]:
        """获取所有别名"""
        all_aliases = {}
        for command_group in self.subgroups.values():
            all_aliases.update(command_group.get_all_aliases())
        for command in self.commands.values():
            for aliases in command.aliases:
                all_aliases[(aliases,)] = command
        return all_aliases

    def revoke_plugin(self, plugin_name: str):
        """撤销插件的命令"""
        deleted_commands = []
        for command in self.commands.values():
            if command.plugin_name == plugin_name:
                deleted_commands.append(command.name)

        for cmd_name in deleted_commands:
            del self.commands[cmd_name]

        for subgroup in self.subgroups.values():
            subgroup.revoke_plugin(plugin_name)

        deleted_aliases = []
        for alias in self.aliases.values():
            if alias.plugin_name == plugin_name:
                deleted_aliases.extend(alias.aliases)

        deleted_aliases = set(deleted_aliases)

        for alias_name in deleted_aliases:
            del self.aliases[alias_name]


class ModernRegistry:
    """现代化命令注册器

    提供完整的命令管理功能。
    """

    root_group = CommandGroup("root")
    error_handler = ErrorHandler()
    command_registries: List["ModernRegistry"] = []

    def __init__(self, prefixes: Optional[List[str]] = None):
        self.prefixes: List[str] = prefixes if prefixes else ["/", "!"]
        self.command_registries.append(self)
        LOG.debug("现代化命令注册器初始化完成")

    def command(self, name: str, aliases: list = None, description: str = "", **kwargs):
        """注册根级命令"""
        if "prefixes" not in kwargs:
            kwargs["prefixes"] = self.prefixes
        return self.root_group.command(
            name, aliases=aliases, description=description, **kwargs
        )

    def group(
        self, name: str, description: str = "", prefixes: Optional[List[str]] = None
    ) -> CommandGroup:
        """创建根级命令组"""
        return self.root_group.group(
            name, description, prefixes=prefixes if prefixes else self.prefixes
        )

    def get_all_commands(self) -> Dict[Tuple[str, ...], CommandSpec]:
        """获取所有命令"""
        return self.root_group.get_all_commands()

    def get_all_aliases(self) -> Dict[Tuple[str, ...], CommandSpec]:
        """获取所有别名"""
        return self.root_group.get_all_aliases()

    @classmethod
    def get_registry(cls, prefixes: Optional[List[str]] = None) -> "ModernRegistry":
        """获取注册器"""
        new_registry = cls(prefixes)
        return new_registry


# 创建全局实例
command_registry = ModernRegistry()
