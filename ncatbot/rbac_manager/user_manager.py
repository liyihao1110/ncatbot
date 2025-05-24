# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-05-24 16:11:15
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-05-24 16:27:08
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议 
# -------------------------
from typing import Dict, Optional, List
from .RBAC_manager import User, PermissionManager

class UserManager:
    """用户管理器，提供用户管理和权限验证功能"""
    def __init__(self, permission_manager: PermissionManager):
        self.users: Dict[str, User] = {}
        self.permission_manager = permission_manager

    def __str__(self) -> str:
        result = ["\033[1m\033[33mUsers:\033[0m"]
        for user_id, user in self.users.items():
            result.append(f"  {user_id}:")
            for role in user.roles:
                result.append(f"    - {role.name}")
        return "\n".join(result)

    def create_user(self, user_id: str) -> User:
        """创建用户，如果已存在则返回现有用户"""
        if user_id not in self.users:
            self.users[user_id] = User(user_id)
        return self.users[user_id]

    def get_user(self, user_id: str) -> Optional[User]:
        """获取用户"""
        return self.users.get(user_id)

    def assign_role(self, user_id: str, role_name: str) -> bool:
        """为用户分配角色"""
        user = self.get_user(user_id)
        if user:
            self.permission_manager.assign_role(user, role_name)
            return True
        return False

    def check_permission(self, user_id: str, permission: str) -> bool:
        """检查用户是否拥有某个权限"""
        user = self.get_user(user_id)
        return bool(user and user.check_permission(permission))

    def get_user_roles(self, user_id: str) -> List[str]:
        """获取用户的所有角色名称"""
        user = self.get_user(user_id)
        return [role.name for role in user.roles] if user else []
