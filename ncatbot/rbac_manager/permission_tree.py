# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-05-05 14:35:02
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-05-24 16:05:51
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议 
# -------------------------
from typing import Dict, List
from .permission_parser import ChoiceGroup, Literal, Parser, RegexSegment, Segment, Wildcard

class BaseTree:
    """权限树基类，提供基本的树操作功能"""
    def __init__(self) -> None:
        self.root: Dict[str, dict | None] = {}

    def __contains__(self, path: str) -> bool:
        return self.match(path)
    
    def __str__(self):
        return visualize_tree(self, ansi = True)

class RuleTree(BaseTree):
    """支持规则匹配的权限树，优化了通配符 ** 的多级匹配"""
    
    def add_permission(self, path: str) -> None:
        """添加规则路径"""
        permission = Parser.parse(path)
        current = self.root
        for seg in permission:
            key = seg if isinstance(seg, (Wildcard, Literal)) else str(seg)
            current = current.setdefault(key, {})
        current[None] = None  # 标记终点

    def match(self, path: str) -> bool:
        """匹配字面量路径是否满足规则"""
        target = [Literal(s) for s in path.split('.')]
        return self._dfs(self.root, target, 0)

    def _dfs(self, node: dict, segments: List[Segment], idx: int) -> bool:
        if idx == len(segments):
            return None in node
        
        current_segment = segments[idx]
        
        # 处理 ** 通配符的贪婪匹配
        for key in list(node.keys()):
            if key is None:
                continue
            
            # ** 可以匹配当前及后续所有层级
            if isinstance(key, Wildcard) and key.scope == "**":
                # 尝试匹配剩余所有可能路径
                for i in range(idx, len(segments)+1):
                    if self._dfs(node[key], segments, i):
                        return True
            
            # 普通通配符或字面量匹配
            elif key.match(current_segment.value):
                if self._dfs(node[key], segments, idx+1):
                    return True
        
        return False

class LiteralTree(BaseTree):
    """存储字面量路径，支持规则路径匹配，并返回所有匹配的权限路径"""

    def add_permission(self, path: str) -> bool:
        """添加字面量路径，如果包含非字面量段则返回False"""
        try:
            permission = Parser.parse(path)
            # 检查是否包含非字面量段
            if any(not isinstance(seg, Literal) for seg in permission):
                return False
                
            current = self.root
            for seg in permission:
                current = current.setdefault(seg, {})
            current[None] = None  # 标记路径终点
            return True
        except:
            return False

    def match(self, path: str) -> List[str]:
        """用规则路径匹配存储的字面量，并返回所有匹配的权限路径"""
        rule = Parser.parse(path)
        return self._dfs(self.root, rule.patterns, 0, [])

    def _dfs(self, node: dict, rule_segments: List[Segment], idx: int, current_path: List[Segment]) -> List[str]:
        if idx == len(rule_segments):
            if None in node:
                return ['.'.join(seg.value for seg in current_path)]
            return []

        current_rule = rule_segments[idx]
        matches = []

        # 处理 ** 通配符
        if isinstance(current_rule, Wildcard) and current_rule.scope == "**":
            for key in node:
                if key is not None:
                    matches.extend(self._dfs(node[key], rule_segments, idx, current_path + [key]))
                    matches.extend(self._dfs(node[key], rule_segments, idx + 1, current_path + [key]))
            return matches

        # 普通匹配
        for key in node:
            if key is None:
                continue
            if current_rule.match(key.value):
                matches.extend(self._dfs(node[key], rule_segments, idx + 1, current_path + [key]))
        return matches


def visualize_tree(tree: BaseTree, ansi: bool = True) -> str:
    """使用 ANSI 颜色代码可视化权限树结构，支持启用/禁用颜色"""
    result = []

    def _visualize_node(name: Segment, node: dict | None, prefix: str, is_last: bool) -> None:
        if not name:
            return
        # 确定连接符号
        connector = "└── " if is_last else "├── "

        # 根据是否启用 ANSI 颜色代码设置颜色
        if ansi:
            if isinstance(name, Wildcard):
                color_code = "\033[31m" if name.scope == "**" else "\033[34m"
            elif isinstance(name, Literal):
                color_code = "\033[36m"
            elif isinstance(name, ChoiceGroup):
                color_code = "\033[32m"
            elif isinstance(name, RegexSegment):
                color_code = "\033[33m"
            else:
                color_code = "\033[0m"
            name_str = f"{color_code}{name}\033[0m"
        else:
            name_str = str(name)

        # 添加当前节点到结果
        result.append(f"{prefix}{connector}{name_str}")

        # 递归终止条件
        if node is None or not isinstance(node, dict):
            return

        # 准备子节点缩进前缀
        children = list(node.items())
        for index, (child_name, child_node) in enumerate(children):
            is_last_child = index == len(children) - 1
            new_prefix = prefix + ("    " if is_last else "│   ")
            _visualize_node(child_name, child_node, new_prefix, is_last_child)

    # 处理根节点为空的情况
    if not tree.root:
        if ansi:
            result.append("\033[33m(empty tree)\033[0m")
        else:
            result.append("(empty tree)")
    else:
        # 从根节点开始遍历
        root_children = list(tree.root.items())
        for index, (name, node) in enumerate(root_children):
            is_last = index == len(root_children) - 1
            _visualize_node(name, node, "", is_last)

    return "\n".join(result)