# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-24 21:56:27
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-06 18:54:56
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, MIT License 
# -------------------------
from .Trie import PermissionTrie
from .Role import Role
from .User import User
from typing import Dict

class RBACManager:
    """
    * RBAC管理类，负责管理角色、用户和权限操作
    ! 警告: 没有进行完全的安全检查
    """
    def __init__(self, case_sensitive: bool = False) -> None:
        """
        初始化 RBAC 管理器
        
        Args:
            case_sensitive (False): 是否区分大小写
        """
        self.roles: Dict[str, Role] = {}        # 角色映射
        self.users: Dict[str, User] = {}         # 用户映射
        self.case_sensitive: bool = case_sensitive  # 是否区分大小写

    def create_role(self, role_name: str) -> None:
        """
        创建新角色
        
        Args:
            role_name (str): 角色名称
        Raises:
            ValueError: 如果角色已存在
        """
        if role_name in self.roles:
            raise ValueError(f"角色 {role_name} 已经存在")
        
        self.roles[role_name] = Role(role_name)

    def add_role_parent(self, role_name: str, parent_name: str) -> None:
        """
        为角色添加父角色
        
        Args:
            role_name (str): 子角色名称
            parent_name (str): 父角色名称
        Raises:
            ValueError: 如果子角色或父角色不存在
        """
        role = self.roles.get(role_name)
        parent = self.roles.get(parent_name)
        if not role or not parent:
            raise ValueError(f"角色 {role_name} 或 {parent_name} 没有找到, 请先创建")
        
        role.add_parent(parent)

    def revoke_permission(self, role_name: str, path: str) -> None:
        """
        移除角色的权限
        
        Args:
            role_name (str): 角色名称
            path (str): 权限路径
        Raises:
            ValueError: 如果角色不存在
        """
        role = self.roles.get(role_name)
        if not role:
            raise ValueError(f"角色 {role_name} 没有找到, 请先创建")
        
        role.remove_permission(path)

    def assign_permission(self, role_name: str, path: str) -> None:
        """
        为角色添加权限
        
        Args:
            role_name (str): 角色名称
            path (str): 权限路径
        Raises:
            ValueError: 如果角色不存在或权限路径无效
        """
        role = self.roles.get(role_name)
        if not role:
            raise ValueError("角色不存在")

        try:
            role.permissions.add_permission(path, role.name)
            
        except ValueError as e:
            raise ValueError(f"无效权限路径 '{path}': {e}")

    def create_user(self, user_name: str) -> None:
        """
        创建新用户
        
        Args:
            user_name (str): 用户名称
        Raises:
            ValueError: 如果用户已存在
        """
        if user_name in self.users:
            raise ValueError(f"用户 {user_name} 已经存在")
        
        self.users[user_name] = User(user_name)

    def assign_role_to_user(self, user_name: str, role_name: str) -> None:
        """
        为用户分配角色
        
        Args:
            user_name (str): 用户名称
            role_name (str): 角色名称
        Raises:
            ValueError: 如果用户或角色不存在
        """
        user = self.users.get(user_name)
        role = self.roles.get(role_name)
        if not user:
            raise ValueError(f"用户 {user_name} 没有找到, 请先创建")
        
        if not role:
            raise ValueError(f"角色 {role_name} 没有找到, 请先创建")
        
        user.roles.append(role)

    def has_user_permission(self, user_name: str, path: str) -> bool:
        """
        检查用户是否拥有某权限
        
        Args:
            user_name (str): 用户名称
            path (str): 权限路径
        Returns:
            bool: 是否拥有权限
        """
        user = self.users.get(user_name)
        if not user:
            return False
        
        for role in user.roles:
            if role.permissions.has_permission(path):
                return True
        return False

    def to_dict(self) -> dict:
        """将权限管理器序列化为字典"""
        return {
            "roles": {
                name: {
                    "name": role.name,
                    "parents": [p.name for p in role.parents],
                    "permissions": role.permissions.to_dict()
                }
                for name, role in self.roles.items()
            },
            "users": {
                name: {
                    "name": user.name,
                    "roles": [r.name for r in user.roles]
                }
                for name, user in self.users.items()
            },
            "case_sensitive": self.case_sensitive
        }

    @staticmethod
    def from_dict(data: dict) -> 'RBACManager':
        """从字典反序列化为权限管理器"""
        manager = RBACManager(data['case_sensitive'])
        
        # 创建所有角色的基本对象
        for role_name, role_data in data['roles'].items():
            role = Role(role_name)
            role.permissions = PermissionTrie.from_dict(role_data['permissions'])
            manager.roles[role_name] = role
        
        # 建立角色之间的父子关系
        for role_name, role_data in data['roles'].items():
            role = manager.roles[role_name]
            for parent_name in role_data['parents']:
                parent_role = manager.roles[parent_name]
                role.parents.append(parent_role)
        
        # 创建用户并关联角色
        for user_name, user_data in data['users'].items():
            user = User(user_name)
            for role_name in user_data['roles']:
                user.roles.append(manager.roles[role_name])
            manager.users[user_name] = user
        
        return manager