# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-03-21 18:06:59
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-05-24 16:09:44
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议 
# -------------------------
from typing import Dict, List
from .permission_tree import RuleTree, LiteralTree

class Role:
    """角色类，管理权限规则"""
    def __init__(self, name: str):
        self.name = name
        self.allow_tree = RuleTree()
        self.deny_tree = RuleTree()

    def add_permission(self, permission_pattern: str) -> None:
        """添加允许权限规则"""
        self.allow_tree.add_permission(permission_pattern)
        
    def deny_permission(self, permission_pattern: str) -> None:
        """添加拒绝权限规则"""
        self.deny_tree.add_permission(permission_pattern)

    def has_permission(self, path: str) -> bool:
        """检查是否拥有某权限，优先检查拒绝权限"""
        if self.deny_tree.match(path):
            return False
        return self.allow_tree.match(path)

class User:
    """用户类，关联多个角色"""
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.roles: List[Role] = []

    def assign_role(self, role: Role) -> None:
        """分配角色"""
        if role not in self.roles:
            self.roles.append(role)

    def check_permission(self, path: str) -> bool:
        """验证权限"""
        for role in self.roles:
            if role.has_permission(path):
                return True
        return False

class PermissionManager:
    """RBAC权限管理核心类"""
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.global_permissions = LiteralTree()

    def __str__(self):
        return "\033[1m\033[33mGlobal Permissio\033[0m\n" + str(self.global_permissions)

    def register_permission(self, permission: str) -> None:
        """注册具体权限"""
        self.global_permissions.add_permission(permission)

    def is_permission_registered(self, permission_pattern: str) -> bool:
        """检查权限模式是否匹配任何已注册的权限"""
        return bool(self.global_permissions.match(permission_pattern))

    def get_matched_permissions(self, permission_pattern: str) -> List[str]:
        """获取与模式匹配的所有已注册权限"""
        return self.global_permissions.match(permission_pattern)

    def create_role(self, role_name: str) -> Role:
        """创建角色"""
        if role_name not in self.roles:
            self.roles[role_name] = Role(role_name)
        return self.roles[role_name]

    def assign_role(self, user: User, role_name: str) -> None:
        """为用户分配角色"""
        role = self.roles.get(role_name)
        if role:
            user.assign_role(role)

    def assign_permission(self, role_name: str, permission_pattern: str, deny: bool = False) -> None:
        """为角色分配权限规则，只有模式匹配到已注册权限时才能分配"""
        role = self.roles.get(role_name)
        matched_permissions = self.get_matched_permissions(permission_pattern)
        if role and matched_permissions:
            if deny:
                role.deny_permission(permission_pattern)
            else:
                role.add_permission(permission_pattern)