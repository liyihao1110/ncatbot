"""命令路由器"""

from typing import Dict, Callable, Optional, Tuple, List, TYPE_CHECKING
from .group import CommandGroup
from ..analyzer import FuncAnalyser
from ncatbot.utils import get_log

if TYPE_CHECKING:
    from ncatbot.core.event import BaseMessageEvent

LOG = get_log(__name__)

class CommandRouter:
    """命令路由器
    
    负责命令的路由和参数解析
    """
    
    def __init__(self):
        """初始化命令路由器"""
        self.command_map: Dict[tuple[str, ...], Callable] = {}
        self.alias_map: Dict[tuple[str, ...], Callable] = {}
        self.command_group_map: Dict[tuple[str, ...], CommandGroup] = {}
        self.max_length = 0
        self.initialized = False
    
    def initialize(self, root_registry: CommandGroup):
        """初始化命令映射
        
        Args:
            root_registry: 根命令注册器
        """
        if self.initialized:
            return
        
        LOG.debug("初始化命令路由器")
        
        # 清空映射
        self.command_map.clear()
        self.alias_map.clear()
        self.command_group_map.clear()
        self.max_length = 0
        
        # 构建命令映射
        self._build_command_map(root_registry)
        
        # 验证命令前缀冲突
        self._validate_prefixes()
        
        self.initialized = True
        LOG.debug(f"命令路由器初始化完成，注册了 {len(self.command_map)} 个命令，{len(self.alias_map)} 个别名")
    
    def _build_command_map(self, current_node: CommandGroup):
        """递归构建命令映射表
        
        Args:
            current_node: 当前命令组节点
        """
        # 添加命令组到映射
        group_path = current_node.build_path("")[:-1] if current_node.name else ()
        self.command_group_map[group_path] = current_node
        
        # 添加命令到映射
        for command_name, func in current_node.command_map.items():
            path = current_node.build_path(command_name)
            self.command_map[path] = func
            self.max_length = max(self.max_length, len(command_name))
            
            # 添加别名到映射
            if hasattr(func, "__alias__"):
                for alias in func.__alias__:
                    self.alias_map[(alias,)] = func
        
        # 递归处理子组
        for child in current_node.children:
            self._build_command_map(child)
    
    def _validate_prefixes(self):
        """验证命令前缀冲突"""
        def check_prefix(command: tuple[str, ...], func: Callable) -> bool:
            """检查命令前缀冲突"""
            for existing_command in self.command_map.keys():
                if existing_command != command:
                    # 检查是否为前缀关系
                    min_len = min(len(command), len(existing_command))
                    if command[:min_len] == existing_command[:min_len]:
                        LOG.warning(f"命令前缀冲突: {command} 和 {existing_command}")
                        return False
            
            for existing_alias in self.alias_map.keys():
                if existing_alias != command:
                    min_len = min(len(command), len(existing_alias))
                    if command[:min_len] == existing_alias[:min_len]:
                        LOG.warning(f"命令与别名前缀冲突: {command} 和别名 {existing_alias}")
                        return False
            
            return True
        
        # 检查所有命令
        for command_path, func in self.command_map.items():
            check_prefix(command_path, func)
        
        # 检查所有别名
        for alias_path, func in self.alias_map.items():
            check_prefix(alias_path, func)
    
    def find_command(self, event: "BaseMessageEvent") -> Optional[Tuple[Callable, List]]:
        """查找并解析命令
        
        Args:
            event: 消息事件
            
        Returns:
            Optional[Tuple[Callable, List]]: (命令函数, 解析后的参数) 或 None
        """
        if not self.initialized:
            LOG.warning("命令路由器未初始化")
            return None
        
        # 检查消息格式
        if len(event.message.filter_text()) == 0:
            return None
        
        if event.message.messages[0].msg_seg_type != "text":
            return None
        
        # 构建激活器
        text_parts = event.message.messages[0].text.split(" ")
        activators = self._build_activators(text_parts)
        
        # 尝试匹配命令
        for activator in activators:
            # 检查命令映射
            if activator in self.command_map:
                func = self.command_map[activator]
                success, args = FuncAnalyser(func, ignore=activator).convert_args(event)
                if success:
                    LOG.debug(f"匹配到命令: {activator}")
                    return func, args
            
            # 检查别名映射
            if activator in self.alias_map:
                func = self.alias_map[activator]
                success, args = FuncAnalyser(func, ignore=activator).convert_args(event)
                if success:
                    LOG.debug(f"匹配到别名命令: {activator}")
                    return func, args
        
        return None
    
    def _build_activators(self, text_parts: List[str]) -> List[tuple[str, ...]]:
        """构建命令激活器列表
        
        Args:
            text_parts: 文本部分列表
            
        Returns:
            List[tuple[str, ...]]: 激活器列表
        """
        activators = []
        for i in range(len(text_parts)):
            activators.append(tuple(text_parts[:i+1]))
        return activators
    
    def clear(self):
        """清理路由器状态"""
        self.initialized = False
        self.command_map.clear()
        self.alias_map.clear()
        self.command_group_map.clear()
        self.max_length = 0
