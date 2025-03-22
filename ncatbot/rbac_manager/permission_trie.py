# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-24 21:52:42
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-22 17:06:48
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
from Fcatbot import Color
from Fcatbot.utils import visualize_tree
from .RBAC_manager import PermissionPath

class Trie:
    def __init__(self, case_sensitive: bool = True):
        self.trie = {}
        self.case_sensitive = case_sensitive    # 设置是否区分大小写

    def __str__(self):
        return '\n'.join([f'{Color.RED}*{Color.RESET}'] + visualize_tree(self.trie))

    def format_path(self, path: str) -> PermissionPath:
        if self.case_sensitive:
            return PermissionPath(path)
        else:
            return PermissionPath(path.lower())

    def add_path(self, path: str):
        path = self.format_path(path)
        if '*' in path or '**' in path:
            raise ValueError(f"创建路径不能使用[*]或[**]")
        
        current_node = self.trie  # 从根节点开始
        for node in path:
            if node in current_node:
                current_node = current_node[node]  # 移动到子节点
            else:
                current_node[node] = {}  # 创建新节点
                current_node = current_node[node]  # 移动到新节点

    def del_path(self, path, max_mod: bool = True):
        self.check_path(path, True)
        formatted_path = self.format_path(path)

        def helper(current_node, remaining_path, parent_chain):
            # 递归终止条件: 路径处理完毕
            if not remaining_path:
                if parent_chain:  # 如果有父节点
                    # 获取直接父节点和当前节点key（如父是 {"a": {}}, current_key是 "a"）
                    parent_dict, key = parent_chain[-1]
                    if key in parent_dict:
                        # 删除当前节点（比如删除 "a.b.c" 中的 "c"）
                        del parent_dict[key]
                        # 如果开启最大修改模式,向上回溯删除孤链
                        if max_mod:
                            # 从倒数第二个父节点开始向上检查（因为已经处理完当前层）
                            for i in range(len(parent_chain)-2, -1, -1):
                                current_parent, current_key = parent_chain[i]
                                # 如果父节点中的当前key对应的字典已经为空
                                if current_key in current_parent and not current_parent.get(current_key, {}):
                                    # 删除该孤节点（比如删除 "a.b" 因为 "a.b.c" 被删且没有其他子节点）
                                    del current_parent[current_key]
                                else:
                                    break  # 遇到非空节点则停止向上删除
                return

            # 分解路径: 当前层 + 剩余路径（比如 ["a", "*", "c"] -> 当前层是 "a",剩余是 ["*", "c"]）
            current_part = remaining_path[0]
            remaining = remaining_path[1:]

            # 处理通配符 *
            if current_part == '*':
                # 遍历当前节点的所有子节点（用 tuple 避免迭代时修改字典的问题）
                for key in tuple(current_node.keys()):
                    next_node = current_node[key]
                    # 递归处理子节点,携带父节点链信息（比如父链增加 (current_node, key)）
                    helper(next_node, remaining, parent_chain + [(current_node, key)])
            
            # 处理通配符 **
            elif current_part == '**':
                # 删除当前节点的所有子节点（比如 "a.**" 删除a的所有子节点和它们的后代）
                for key in tuple(current_node.keys()):
                    del current_node[key]
                
                # 如果开启最大修改模式,可能需要删除当前节点自身（如果它变成空节点）
                if parent_chain and max_mod:
                    parent_dict, key_in_parent = parent_chain[-1]
                    # 检查父节点中当前key对应的字典是否为空（比如删除 "a.**" 后检查 "a" 是否为空）
                    if key_in_parent in parent_dict and not parent_dict.get(key_in_parent, {}):
                        # 删除父节点中的当前key（比如删除 "a"）
                        del parent_dict[key_in_parent]
                        # 继续向上检查孤链（比如如果 "a" 被删,检查它的父节点是否需要删除）
                        for i in range(len(parent_chain)-2, -1, -1):
                            current_parent, current_key = parent_chain[i]
                            if current_key in current_parent and not current_parent.get(current_key, {}):
                                del current_parent[current_key]
                            else:
                                break  # 遇到非空节点则停止
                return  # ** 通配符处理完毕后直接返回,不再处理剩余路径（因为已经删除了所有后代）
            
            # 处理普通节点
            else:
                if current_part in current_node:
                    next_node = current_node[current_part]
                    # 携带当前节点信息进入下一层递归
                    helper(next_node, remaining, parent_chain + [(current_node, current_part)])

        # 从根节点开始递归处理,初始父节点链为空
        helper(self.trie, formatted_path, [])

    @classmethod
    def _check_path_in_trie(cls, trie: dict, path: PermissionPath, complete: bool = False):
        """路径匹配实现"""
        current_node = trie
        path_len = len(path)
        
        # 使用迭代代替递归，提高性能
        for i, node in enumerate(path):
            # 快速处理 ** 通配符
            if node == '**':
                return True if not complete or i == path_len - 1 else False
                
            # 处理 * 通配符
            elif node == '*':
                if i == path_len - 1:  # 路径最后一个节点
                    return bool(current_node) if complete else True
                    
                # 检查所有可能的子路径
                remaining = path[i+1:]
                return any(
                    cls._check_path_in_trie(current_node[child], remaining, complete)
                    for child in current_node
                )
                
            # 普通节点匹配
            elif node not in current_node:
                return False
                
            current_node = current_node[node]
            
        return not complete or not current_node

    def check_path(self, path: str, complete: bool = False):
        formatted_path = self.format_path(path)
        return self._check_path_in_trie(self.trie, formatted_path, complete)
