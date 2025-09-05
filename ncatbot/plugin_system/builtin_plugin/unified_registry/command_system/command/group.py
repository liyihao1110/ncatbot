"""命令组模块"""

from typing import Dict, Callable, List, Optional

class CommandGroup:
    """命令组类
    
    用于组织和管理命令的层次结构。
    支持嵌套的命令组和命令别名。
    """
    
    def __init__(self, parent: Optional["CommandGroup"] = None, name: Optional[str] = None):
        """初始化命令组
        
        Args:
            parent: 父命令组
            name: 命令组名称
        """
        self.parent: Optional["CommandGroup"] = parent
        self.command_map: Dict[str, Callable] = {}
        self.command_group_map: Dict[str, "CommandGroup"] = {}
        self.children: List["CommandGroup"] = []
        self.name = name

    def command(self, name: str, alias: Optional[List[str]] = None):
        """注册命令装饰器
        
        Args:
            name: 命令名称
            alias: 直接别名，跳过中间的一大堆 command_group
        """
        def decorator(func: Callable):
            if self.command_map.get(name, None) is not None:
                raise ValueError(f"命令已存在: {name}")
            from ncatbot.plugin_system.builtin_plugin.unified_registry.command_system.analyzer.func_analyzer import FuncAnalyser
            try:
                FuncAnalyser(func)
            except Exception as e:
                raise e
            self.command_map[name] = func
            if alias is not None:
                setattr(func, "__alias__", alias)
            return func
        return decorator
    
    def command_group(self, name: str) -> "CommandGroup":
        """创建子命令组
        
        Args:
            name: 子命令组名称
            
        Returns:
            CommandGroup: 新创建的子命令组
        """
        if self.command_group_map.get(name, None) is not None:
            raise ValueError(f"命令组已存在: {name}")
        self.command_group_map[name] = CommandGroup(self, name)
        command_group = CommandGroup(self, name)
        self.children.append(command_group)
        return command_group
    
    def build_path(self, command_name: str) -> tuple[str, ...]:
        """构建命令路径
        
        Args:
            command_name: 命令名称
            
        Returns:
            tuple[str, ...]: 命令路径元组
        """
        if self.parent is None:
            if command_name:
                return (command_name,)
            else:
                return ()
        else:
            parent_path = self.parent.build_path("")
            if command_name:
                return parent_path + (self.name, command_name)
            else:
                return parent_path + (self.name,)
    
    def get_all_commands(self) -> Dict[tuple[str, ...], Callable]:
        """获取所有命令的映射
        
        Returns:
            Dict[tuple[str, ...], Callable]: 命令路径到函数的映射
        """
        commands = {}
        
        # 添加当前组的命令
        for command_name, func in self.command_map.items():
            path = self.build_path(command_name)
            commands[path] = func
        
        # 递归添加子组的命令
        for child in self.children:
            commands.update(child.get_all_commands())
        
        return commands
    
    def get_all_aliases(self) -> Dict[tuple[str, ...], Callable]:
        """获取所有别名的映射
        
        Returns:
            Dict[tuple[str, ...], Callable]: 别名路径到函数的映射
        """
        aliases = {}
        
        # 添加当前组的别名
        for func in self.command_map.values():
            if hasattr(func, "__alias__"):
                for alias in func.__alias__:
                    aliases[(alias,)] = func
        
        # 递归添加子组的别名
        for child in self.children:
            aliases.update(child.get_all_aliases())
        
        return aliases
