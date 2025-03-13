# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-24 21:52:42
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-04 20:02:25
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, MIT License
# -------------------------
from typing import Dict, List, Optional, Set, Tuple


class TrieNode:
    """Trie树的节点

    Attributes:
        children (Dict[str, TrieNode]): 普通子节点映射，保存精确匹配的路径段
        star (Optional[TrieNode]): 单级通配符 `*` 指针，允许匹配任意一个路径段
        star_star (Optional[TrieNode]): 多级通配符 `**` 指针，允许匹配任意数量的路径段
        is_end (bool): 标志该节点是否为权限路径的终点
        granted_by (Set[str]): 拥有该权限节点权限的角色集合
    """

    def __init__(self) -> None:
        """初始化Trie树的节点"""
        self.children: Dict[str, TrieNode] = {}  # 普通子节点映射，保存精确匹配的路径段
        self.star: Optional[TrieNode] = None  # 单级通配符*指针，允许匹配任意一个路径段
        self.star_star: Optional[TrieNode] = (
            None  # 多级通配符**指针，允许匹配任意数量的路径段
        )
        self.is_end: bool = False  # 标志是否是权限路径的终点
        self.granted_by: Set[str] = set()  # 拥有该权限节点权限的角色集合

    def to_dict(self) -> dict:
        """将节点序列化为字典"""
        return {
            "children": {key: node.to_dict() for key, node in self.children.items()},
            "star": self.star.to_dict() if self.star else None,
            "star_star": self.star_star.to_dict() if self.star_star else None,
            "is_end": self.is_end,
            "granted_by": list(self.granted_by),
        }

    @staticmethod
    def from_dict(data: dict) -> "TrieNode":
        """从字典反序列化为节点"""
        node = TrieNode()
        node.children = (
            {key: TrieNode.from_dict(child) for key, child in data["children"].items()}
            if data["children"]
            else {}
        )
        node.star = TrieNode.from_dict(data["star"]) if data["star"] else None
        node.star_star = (
            TrieNode.from_dict(data["star_star"]) if data["star_star"] else None
        )
        node.is_end = data["is_end"]
        node.granted_by = set(data["granted_by"])
        return node


class PermissionTrie:
    """权限树，用于权限管理

    Attributes:
        root (TrieNode): 权限Trie树的根节点
        case_sensitive (bool): 是否区分大小写，决定路径规范化的方式
    """

    def __init__(self, case_sensitive: bool = False) -> None:
        """初始化权限树

        Args:
            case_sensitive (bool, optional): 是否区分大小写，默认为 False
        """
        self.root: TrieNode = TrieNode()  # 初始化根节点
        self.case_sensitive: bool = case_sensitive  # 设置是否区分大小写

    def normalize_path(self, path: str) -> str:
        """
        路径规范化
            如果对应设置为不区分大小写 则统一使用小写
            去除路径中的空字符
        """
        segments = []
        for seg in path.strip().split("."):
            if seg:  # 跳过空字符
                segments.append(seg if self.case_sensitive else seg.lower())
        return ".".join(segments)

    def remove_permission(self, path: str, role: str) -> bool:
        """移除特定角色授予的权限路径"""
        # 规范化权限路径
        path = self.normalize_path(path)
        segments = path.split(".") if path else []

        # 权限路径合法性校验
        try:
            self._validate_path(segments)
        except ValueError:
            return False  # 非法路径

        # 定位到目标节点，并记录路径
        traversal_path = [
            (self.root, None, None)
        ]  # (当前节点, 父节点, 进入当前节点的类型)
        current = self.root
        removed = False

        for seg in segments:
            # 根据当前节点类型选择下一节点
            if seg == "*":
                next_node = current.star
                seg_type = "star"
            elif seg == "**":
                next_node = current.star_star
                seg_type = "star_star"
            else:
                next_node = current.children.get(seg)
                seg_type = "child"

            if not next_node:
                return False  # 当前节点不存在

            traversal_path.append((next_node, current, seg_type))
            current = next_node

        # 检查是否到达有效权限终点
        if not current.is_end:
            return False

        # 移除角色授权记录
        if role not in current.granted_by:
            return False

        current.granted_by.remove(role)
        removed = True

        # 如果仍有其他角色授权，保留节点
        if current.granted_by:
            return removed

        # 标记当前节点不再作为权限终点，并尝试清理无效节点
        current.is_end = False
        self._cleanup_nodes(traversal_path)
        return removed

    def _validate_path(self, segments: List[str]) -> None:
        """
        校验路径格式
            多级通配符**只能出现一次，并且必须位于权限路径末尾
        """
        star_star_positions = [i for i, seg in enumerate(segments) if seg == "**"]
        if len(star_star_positions) > 1:
            raise ValueError("权限路径中最多只能包含一个**通配符")
        if star_star_positions and star_star_positions[0] != len(segments) - 1:
            raise ValueError("**通配符必须位于权限路径末尾")

    def _cleanup_nodes(
        self, traversal_path: List[Tuple[TrieNode, TrieNode, str]]
    ) -> None:
        """反向遍历权限路径，清理不再需要的节点"""
        # 从子节点向上清理
        for i in range(len(traversal_path) - 1, 0, -1):
            current_node, parent_node, seg_type = traversal_path[i]

            # 如果当前节点有子节点或授权记录，保留
            retain_cond = (
                current_node.is_end
                or current_node.children
                or current_node.star
                or current_node.star_star
            )
            if retain_cond:
                break  # 不再继续清理

            # 根据进入类型删除节点引用
            if seg_type == "star":
                parent_node.star = None
            elif seg_type == "star_star":
                parent_node.star_star = None
            elif seg_type == "child":
                # 找到对应的子节点并删除
                for key, node in parent_node.children.items():
                    if node is current_node:
                        del parent_node.children[key]
                        break

            current_node = parent_node  # 继续处理父节点

    def add_permission(self, path: str, role: str) -> None:
        """添加权限路径并记录授权角色"""
        path = self.normalize_path(path)
        segments = path.split(".") if path else []

        # 路径合法性校验
        self._validate_path(segments)

        current = self.root
        for i, seg in enumerate(segments):
            is_last = i == len(segments) - 1

            if seg == "*":
                # 单级通配符
                if not current.star:
                    current.star = TrieNode()
                current = current.star
            elif seg == "**":
                # 多级通配符，添加到当前节点
                if not current.star_star:
                    current.star_star = TrieNode()
                current = current.star_star
            else:
                # 普通段，添加到子节点
                if seg not in current.children:
                    current.children[seg] = TrieNode()
                current = current.children[seg]

        current.is_end = True
        current.granted_by.add(role)

    def has_permission(self, path: str) -> bool:
        """检查权限是否被授予"""
        path = self.normalize_path(path)
        segments = path.split(".") if path else []
        return self._check_segments(segments, 0, self.root)

    def _check_segments(self, segments: List[str], index: int, node: TrieNode) -> bool:
        """递归检查路径段是否匹配"""
        # 所有段匹配完成，判断是否到达权限终点
        if index == len(segments):
            return node.is_end

        current_seg = segments[index]
        if not self.case_sensitive:  # 如果忽略大小写
            current_seg = current_seg.lower()

        # 尝试精确匹配
        if current_seg in node.children:
            if self._check_segments(segments, index + 1, node.children[current_seg]):
                return True

        # 尝试单级通配符匹配
        if node.star:
            # 单级通配符允许匹配当前段
            if self._check_segments(segments, index + 1, node.star):
                return True

        # 尝试多级通配符匹配
        if node.star_star:
            # 多级通配符允许匹配当前段及后续所有段，或只匹配当前段
            return node.star_star.is_end or self._check_segments(
                segments, index + 1, node.star_star
            )

        # 未匹配到任何段
        return False

    def visualize(self) -> str:
        """打印可视化树结构"""
        lines: List[str] = [f"{Color.RED}*{Color.RESET}"]
        self._visualize(self.root, lines, "", "", True)
        return "\n".join(lines)

    def _visualize(
        self,
        node: TrieNode,
        lines: List[str],
        prefix: str,
        child_prefix: str,
        is_last: bool,
    ) -> None:
        """递归构建可视化字符串"""
        # 添加当前节点到展示行
        if prefix:
            line_end = (
                f"{Color.GREEN}○{Color.RESET}"
                if not node.is_end
                else f"{Color.YELLOW}●{Color.RESET}"
            )
            lines.append(prefix + " " + line_end)

        # 构建子节点列表
        children = []
        for name, child in node.children.items():
            children.append(("child", name, child))
        if node.star:
            children.append(("star", "*", node.star))
        if node.star_star:
            children.append(("star_star", "**", node.star_star))

        # 遍历子节点
        for i, (type_, name, child) in enumerate(children):
            is_last_child = i == len(children) - 1
            new_child_prefix = "│   " if not is_last_child else "    "
            next_prefix = child_prefix + (
                new_child_prefix if (is_last or len(children) - 1 == 0) else "    "
            )

            # 构建节点连接符号
            connector = "└──" if is_last_child else "├──"
            next_line_prefix = (
                Color.GREEN + child_prefix + connector + " " + Color.RESET + name
            )

            self._visualize(child, lines, next_line_prefix, next_prefix, is_last_child)

    def to_dict(self) -> dict:
        """将权限树序列化为为字典"""
        return {"root": self.root.to_dict(), "case_sensitive": self.case_sensitive}

    def permission_exist(self):
        pass

    def create_permission(self, path: str):
        pass

    @staticmethod
    def from_dict(data: dict) -> "PermissionTrie":
        """从字典反序列化为权限树"""
        trie = PermissionTrie(data["case_sensitive"])
        trie.root = TrieNode.from_dict(data["root"])
        return trie
