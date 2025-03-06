# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-24 21:55:06
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-04 20:42:07
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, MIT License 
# -------------------------
from collections import deque
from .Role import Role
from typing import List

class User:
    """
    用户类
    包含用户名称和关联的角色
    """
    def __init__(self, user_name: str) -> None:
        self.name: str = user_name
        self.roles: List[Role] = []   # 用户关联的角色列表

    def has_permission(self, path: str) -> bool:
        """
        检查用户是否拥有指定权限
        
        Args:
            path: 权限
        """
        visited_roles = set()  # 记录已访问的角色
        queue = deque(self.roles)
        while queue:
            role = queue.popleft()
            if role in visited_roles:
                continue
            visited_roles.add(role)
            # 检查当前角色的权限Trie树
            if role.permissions.has_permission(path):
                return True
            # 将所有父角色加入队列
            queue.extend(role.get_all_parents())
        return False

    def to_dict(self) -> dict:
        """
        将用户序列化为字典
        
        为避免循环引用, 角色引用由RBACManager处理(无法单独使用)
        """
        return {
            "name": self.name
        }

    @staticmethod
    def from_dict(data: dict) -> 'User':
        """从字典反序列化为用户"""
        return User(data["name"])