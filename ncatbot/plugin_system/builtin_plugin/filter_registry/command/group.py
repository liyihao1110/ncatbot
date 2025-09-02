"""命令组模块"""

from typing import Dict, Callable, List


class CommandGroup:
    """命令组类
    
    用于组织和管理命令的层次结构。
    支持嵌套的命令组和命令别名。
    
    TODO: 精细权限控制
    """
    
    def __init__(self, parent: "CommandGroup" = None, name: str = None):
        self.parent: "CommandGroup" = parent
        self.command_map: Dict[str, Callable] = {}
        self.command_group_map: Dict[str, "CommandGroup"] = {}
        self.children: List["CommandGroup"] = []
        self.name = name
        # self.path = (name,) if parent is None else parent.path + (name,)

    def command(self, name: str, alias: List[str] = None):
        """注册命令装饰器
        
        Args:
            name: 命令名称
            alias: 直接别名，跳过中间的一大堆 command_group
        """
        def decorator(func: Callable):
            self.command_map[name] = func
            if alias is not None:
                setattr(func, "__alias__", alias)
            return func
        return decorator
    
    def command_group(self, name: str):
        """创建子命令组
        
        Args:
            name: 子命令组名称
            
        Returns:
            CommandGroup: 新创建的子命令组
        """
        command_group = CommandGroup(self, name)
        self.children.append(command_group)
        return command_group
    
    def build_path(self, command_name) -> tuple[str, ...]:
        """构建命令路径
        
        Args:
            command_name: 命令名称
            
        Returns:
            tuple[str, ...]: 命令的完整路径
        """
        if self.parent is None:
            return (command_name,)
        return self.parent.build_path(self.name) + (command_name,)
