# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-03-06 18:30:02
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-22 17:11:43
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
import os
import json
from functools import lru_cache
from typing import Dict, Literal, Set

from ncatbot.utils.assets.literals import PermissionGroup
from ncatbot.utils import ncatbot_config
from ncatbot.plugin_system.rbac.rbac_path import PermissionPath
from ncatbot.plugin_system.rbac.rbac_trie import Trie


class _RBACManager:
    def __init__(self, case_sensitive: bool = True, default_role: str = None):
        self.case_sensitive = case_sensitive
        self.roles: Dict = {}
        self.users: Dict = {}
        self.permissions_trie: Trie = Trie(self.case_sensitive)
        self.default_role = default_role
        self.role_users: Dict[str, Set[str]] = {}
        self.role_inheritance = {}  # 存储角色继承关系 {role: [inherited_roles]}

    def __str__(self):
        return self.permissions_trie.__str__()

    def refresh_cache(self, user_name: str = None, role_name: str = None):
        """
        刷新权限缓存（当权限数据变化时调用）
        策略: 清除相关用户或角色的缓存计算结果
        """
        if user_name:  # 清除指定用户的缓存
            self._get_user_permissions.cache_clear()
        elif role_name:  # 清除所有关联该角色的用户的缓存
            for user in self.users.values():
                if role_name in user["role_list"]:
                    self._get_user_permissions.cache_clear()
                    break
        else:  # 全局刷新
            self._get_user_permissions.cache_clear()

    @lru_cache(maxsize=128)
    def _get_user_permissions(self, user_name: str) -> Dict[str, Set[str]]:
        """
        获取用户的最终权限集合（带缓存）,并自动清理无效权限
        返回结构: {"white": {所有白名单权限路径}, "black": {所有黑名单权限路径}}
        """
        user = self.users[user_name]
        white = set()
        black = set()

        # 处理用户直接权限
        valid_user_white = []
        for path in user["white_permissions_list"]:
            if self.check_availability(permissions_path=path):
                valid_user_white.append(path)
        # 更新用户的白名单
        if len(valid_user_white) != len(user["white_permissions_list"]):
            self.users[user_name]["white_permissions_list"] = valid_user_white
            self.refresh_cache(user_name=user_name)  # 使缓存失效

        valid_user_black = []
        for path in user["black_permissions_list"]:
            if self.check_availability(permissions_path=path):
                valid_user_black.append(path)
        if len(valid_user_black) != len(user["black_permissions_list"]):
            self.users[user_name]["black_permissions_list"] = valid_user_black
            self.refresh_cache(user_name=user_name)

        white.update(valid_user_white)
        black.update(valid_user_black)

        # 获取用户所有角色（包括继承的角色）的权限
        processed_roles = set()

        def process_role_permissions(role_name):
            if role_name in processed_roles:
                return
            processed_roles.add(role_name)

            role = self.roles.get(role_name, {})
            # 处理当前角色的权限
            valid_role_white = []
            for path in role.get("white_permissions_list", []):
                if self.check_availability(permissions_path=path):
                    valid_role_white.append(path)
            if len(valid_role_white) != len(role.get("white_permissions_list", [])):
                role["white_permissions_list"] = valid_role_white
                self.refresh_cache(role_name=role_name)
            white.update(valid_role_white)

            valid_role_black = []
            for path in role.get("black_permissions_list", []):
                if self.check_availability(permissions_path=path):
                    valid_role_black.append(path)
            if len(valid_role_black) != len(role.get("black_permissions_list", [])):
                role["black_permissions_list"] = valid_role_black
                self.refresh_cache(role_name=role_name)
            black.update(valid_role_black)

            # 处理继承的角色
            for inherited_role in self.role_inheritance.get(role_name, []):
                process_role_permissions(inherited_role)

        # 处理用户的所有角色
        for role_name in user["role_list"]:
            process_role_permissions(role_name)

        return {"white": white, "black": black}

    def check_permission(self, user_name: str, path: str, strict: bool = False) -> bool:
        """
        检查用户是否拥有某路径的权限
        规则优先级: 黑名单 > 白名单 > 默认拒绝

        Args:
            user_name: 用户名
            path: 权限路径
            strict: 是否严格匹配。True时仅允许完全匹配，False时允许通配符匹配
        """
        if not self.check_availability(user_name=user_name):
            raise ValueError(f"用户 {user_name} 不存在")

        permissions = self._get_user_permissions(user_name)
        formatted_path = self.permissions_trie.format_path(path)

        # 快速路径: 精确匹配黑名单
        if formatted_path.row_path in permissions["black"]:
            return False

        # 快速路径: 精确匹配白名单
        if formatted_path.row_path in permissions["white"]:
            return True

        if strict:
            return False

        # 通配符匹配
        for black_path in permissions["black"]:
            if self._is_path_covered(black_path, formatted_path):
                return False

        for white_path in permissions["white"]:
            if self._is_path_covered(white_path, formatted_path):
                return True

        return False

    def _is_path_covered(self, pattern: str, target: PermissionPath) -> bool:
        """
        判断权限路径是否被某个模式覆盖（支持通配符）
        示例: pattern="a.*.c" 可以匹配 target="a.x.c"
        """
        pattern_path = self.permissions_trie.format_path(pattern)
        return pattern_path.matching_path(target.row_path)

    def check_availability(
        self, user_name: str = None, role_name: str = None, permissions_path: str = None
    ):
        """检查用户、角色或权限路径是否存在"""
        result = []
        if user_name:
            result.append(user_name in self.users)
        if role_name:
            result.append(role_name in self.roles)
        if permissions_path:
            if not self.case_sensitive:
                permissions_path = permissions_path.lower()
            result.append(
                self.permissions_trie.check_path(permissions_path, complete=True)
            )
        return all(result)

    def add_permissions(self, permissions_path: str):
        """添加权限路径到 Trie 树"""
        if not self.check_availability(permissions_path=permissions_path):
            self.permissions_trie.add_path(permissions_path)

    def del_permissions(self, permissions_path: str):
        self.permissions_trie.del_path(permissions_path)
        self.refresh_cache()

    def add_role(self, role_name: str, force: bool = False):
        if not force and self.check_availability(role_name=role_name):
            raise IndexError(f"角色 {role_name} 已经存在")
        self.refresh_cache(role_name=role_name)
        self.roles[role_name] = {
            "white_permissions_list": [],
            "black_permissions_list": [],
        }
        self.role_users[role_name] = set()

    def add_user(self, user_name: str, force: bool = False):
        if not force and self.check_availability(user_name=user_name):
            raise IndexError(f"用户 {user_name} 已经存在")
        self.refresh_cache(user_name=user_name)
        self.role_users[self.default_role].add(user_name)
        self.users[user_name] = {
            "white_permissions_list": [],
            "black_permissions_list": [],
            "role_list": [self.default_role] if self.default_role else [],
        }

    def del_role(self, role_name: str):
        """删除角色时同时清理继承关系"""
        self.refresh_cache(role_name=role_name)
        # 删除该角色作为继承者的记录
        if role_name in self.role_inheritance:
            del self.role_inheritance[role_name]
        # 删除其他角色对该角色的继承
        for role in self.role_inheritance:
            if role_name in self.role_inheritance[role]:
                self.role_inheritance[role].remove(role_name)
        for user in self.role_users[role_name]:
            self.users[user]["role_list"].remove(role_name)
        del self.roles[role_name]
        del self.role_users[role_name]

    def del_user(self, user_name: str):
        self.refresh_cache(user_name=user_name)
        self.role_users[self.default_role].remove(user_name)
        del self.users[user_name]

    def assign_permissions_to_role(
        self,
        role_name: str,
        permissions_path: str,
        mode: Literal["white", "black"] = "white",
    ):
        """为角色分配权限(能够处理重复分配)"""
        if not self.check_availability(role_name=role_name):
            raise IndexError(f"角色 {role_name} 不存在")
        if not self.check_availability(permissions_path=permissions_path):
            raise ValueError(
                f"权限路径 {permissions_path} 不存在,无法分配给角色 {role_name}"
            )
        self.refresh_cache(role_name=role_name)
        if permissions_path not in self.roles[role_name][f"{mode}_permissions_list"]:
            self.roles[role_name][f"{mode}_permissions_list"].append(permissions_path)

    def assign_permissions_to_user(
        self, user_name: str, permissions_path: str, mode: Literal["white", "black"]
    ):
        """为用户直接分配权限,确保权限路径存在"""
        if not self.check_availability(user_name=user_name):
            raise IndexError(f"用户 {user_name} 不存在")
        if not self.check_availability(permissions_path=permissions_path):
            raise ValueError(
                f"权限路径 {permissions_path} 不存在,无法分配给用户 {user_name}"
            )
        self.refresh_cache(user_name=user_name)
        self.users[user_name][f"{mode}_permissions_list"].append(permissions_path)

    def assign_role_to_user(self, role_name: str, user_name: str):
        if not self.check_availability(user_name=user_name, role_name=role_name):
            raise IndexError(f"角色 {role_name} 或用户 {user_name} 不存在")
        self.refresh_cache(role_name=role_name, user_name=user_name)
        if role_name not in self.users[user_name]["role_list"]:
            self.users[user_name]["role_list"].append(role_name)
            self.role_users[role_name].add(user_name)

    def unassign_permissions_to_role(
        self, role_name: str, permissions_path: str, mode: Literal["white", "black"]
    ):
        if not self.check_availability(role_name=role_name):
            raise IndexError(f"角色 {role_name} 不存在")
        self.refresh_cache(role_name=role_name)
        if permissions_path in self.roles[role_name][f"{mode}_permissions_list"]:
            self.roles[role_name][f"{mode}_permissions_list"].remove(permissions_path)

    def unassign_permissions_to_user(
        self, user_name: str, permissions_path: str, mode: Literal["white", "black"]
    ):
        if not self.check_availability(user_name=user_name):
            raise IndexError(f"用户 {user_name} 不存在")
        self.refresh_cache(user_name=user_name)
        self.users[user_name][f"{mode}_permissions_list"].remove(permissions_path)

    def unassign_role_to_user(self, role_name: str, user_name: str):
        if not self.check_availability(user_name=user_name, role_name=role_name):
            raise IndexError(f"角色 {role_name} 或用户 {user_name} 不存在")
        self.refresh_cache(role_name=role_name, user_name=user_name)
        self.users[user_name]["role_list"].remove(role_name)
        self.role_users[role_name].remove(user_name)

    def _check_circular_inheritance(
        self, role: str, inherited_role: str, visited: set = None
    ) -> bool:
        """检查是否存在循环继承"""
        if visited is None:
            visited = set()
        if role in visited:
            return True
        visited.add(role)

        # 检查继承链上的所有角色
        for parent in self.role_inheritance.get(inherited_role, []):
            if self._check_circular_inheritance(inherited_role, parent, visited.copy()):
                return True
        return False

    def set_role_inheritance(self, role: str, inherited_role: str):
        """设置角色继承关系"""
        if not self.check_availability(role_name=role) or not self.check_availability(
            role_name=inherited_role
        ):
            raise IndexError(f"角色 {role} 或 {inherited_role} 不存在")

        if role == inherited_role:
            raise ValueError("角色不能继承自身")

        if self._check_circular_inheritance(role, inherited_role):
            raise ValueError(f"检测到循环继承: {role} -> {inherited_role}")

        if role not in self.role_inheritance:
            self.role_inheritance[role] = []

        if inherited_role not in self.role_inheritance[role]:
            self.role_inheritance[role].append(inherited_role)
            self.refresh_cache(role_name=role)

    def remove_role_inheritance(self, role: str, inherited_role: str):
        """移除角色继承关系"""
        if (
            role in self.role_inheritance
            and inherited_role in self.role_inheritance[role]
        ):
            self.role_inheritance[role].remove(inherited_role)
            self.refresh_cache(role_name=role)

    def to_dict(self) -> dict:
        """将RBACManager实例转换为可序列化字典"""
        return {
            # 保存配置参数
            "case_sensitive": self.case_sensitive,
            "default_role": self.default_role,
            # 保存角色数据（包含权限列表）
            "roles": {
                role_name: {
                    "white_permissions_list": role_data["white_permissions_list"],
                    "black_permissions_list": role_data["black_permissions_list"],
                }
                for role_name, role_data in self.roles.items()
            },
            "role_users": {
                role_name: list(users)
                for role_name, users in self.role_users.items()
            },
            # 保存用户数据（包含直接权限和角色关联）
            "users": {
                user_name: {
                    "white_permissions_list": user_data["white_permissions_list"],
                    "black_permissions_list": user_data["black_permissions_list"],
                    "role_list": user_data["role_list"],
                }
                for user_name, user_data in self.users.items()
            },
            # 保存权限树所有有效路径
            "permissions_trie_paths": self.permissions_trie.trie,
            # 保存角色继承关系
            "role_inheritance": self.role_inheritance,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "_RBACManager":
        """从字典重建RBACManager实例"""
        # 检查全局配置
        

        instance = cls()
        instance.case_sensitive = data.get("case_sensitive", True)
        instance.default_role = data.get("default_role", None)
        trie_paths = data.get("permissions_trie_paths", [])
        instance.permissions_trie.trie = trie_paths

        # 恢复角色继承关系
        instance.role_inheritance = data.get("role_inheritance", {})

        # 恢复角色数据
        for role_name, role_data in data.get("roles", {}).items():
            instance.roles[role_name] = {
                "white_permissions_list": [
                    p
                    for p in role_data["white_permissions_list"]
                    if instance.permissions_trie.check_path(p)
                ],
                "black_permissions_list": [
                    p
                    for p in role_data["black_permissions_list"]
                    if instance.permissions_trie.check_path(p)
                ],
            }
        
        # 恢复角色/用户对照表
        for role_name, users in data.get("role_users", {}).items():
            instance.role_users[role_name] = set(users)
            for user in users:
                instance.role_users[role_name].add(user)

        # 恢复用户数据
        valid_roles = set(instance.roles.keys())
        for user_name, user_data in data.get("users", {}).items():
            instance.users[user_name] = {
                "white_permissions_list": [
                    p
                    for p in user_data["white_permissions_list"]
                    if instance.permissions_trie.check_path(p)
                ],
                "black_permissions_list": [
                    p
                    for p in user_data["black_permissions_list"]
                    if instance.permissions_trie.check_path(p)
                ],
                "role_list": [
                    r
                    for r in user_data["role_list"]
                    if r in valid_roles or r == instance.default_role
                ],
            }

        # 强制刷新所有缓存
        instance.refresh_cache()
        return instance
    

class RBACManager:
    manager: _RBACManager = None
    def __init__(self, path):
        if os.path.exists(path):
            self.manager = _RBACManager.from_dict(json.load(open(path, "r", encoding="utf-8")))
        else:
            self.manager = _RBACManager(default_role=PermissionGroup.USER.value)
            
        self.add_role(PermissionGroup.USER.value)
        self.add_role(PermissionGroup.ADMIN.value)
        self.add_role(PermissionGroup.ROOT.value)
        self.set_role_inheritance(PermissionGroup.ADMIN.value, PermissionGroup.ROOT.value)
        self.set_role_inheritance(PermissionGroup.USER.value, PermissionGroup.ADMIN.value)
        self.unassign_root_roles()
        self.assign_role_to_user(ncatbot_config.root, PermissionGroup.ROOT.value)
    
    def set_role_inheritance(self, role: str, inherited_role: str):
        if not self.role_exists(role) or not self.role_exists(inherited_role):
            raise IndexError(f"角色 {role} 或 {inherited_role} 不存在")
        self.manager.set_role_inheritance(role, inherited_role)
    
    def unassign_root_roles(self):
        for user in self.manager.role_users[PermissionGroup.ROOT.value]:
            self.manager.users[user]["role_list"].remove(PermissionGroup.ROOT.value)
        self.manager.role_users[PermissionGroup.ROOT.value] = set()
    
    def save(self, path):
        # TODO 编码问题
        json.dump(self.manager.to_dict(), open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    
    def load(self, path):
        self.manager = _RBACManager.from_dict(json.load(open(path, "r", encoding="utf-8")))
    
    def user_exists(self, user_name: str) -> bool:
        return self.manager.check_availability(user_name=user_name)
    
    def role_exists(self, role_name: str) -> bool:
        return self.manager.check_availability(role_name=role_name)
    
    def permission_path_exists(self, permissions_path: str) -> bool:
        return self.manager.check_availability(permissions_path=permissions_path)
    
    def check_permission(self, user_name: str, path: str, create_user_if_not_exists: bool = True) -> bool:
        if not self.user_exists(user_name):
            if create_user_if_not_exists:
                self.add_user(user_name)
            else:
                raise IndexError(f"用户 {user_name} 不存在")
        return self.manager.check_permission(user_name, path)
    
    def user_has_role(self, user_name: str, role_name: str) -> bool:
        return role_name in self.manager.users[user_name]["role_list"]
    
    def add_role(self, role_name: str, ignore_if_exists: bool = True):
        if self.role_exists(role_name):
            if ignore_if_exists:
                return
            else:
                raise IndexError(f"角色 {role_name} 已存在")
        else:
            self.manager.add_role(role_name)
        if not ignore_if_exists:
            raise IndexError(f"角色 {role_name} 已存在")
    
    def add_user(self, user_name: str, role_list: list[str] = None, ignore_if_exists: bool = True):
        if self.user_exists(user_name):
            if ignore_if_exists:
                return
            else:
                raise IndexError(f"用户 {user_name} 已存在")
        else:
            self.manager.add_user(user_name)
        if role_list:
            for role in role_list:
                if not self.role_exists(role):
                    raise IndexError(f"角色 {role} 不存在")
                if not self.user_has_role(user_name, role):
                    self.manager.assign_role_to_user(role_list, user_name)
    
    def assign_role_to_user(self, user_name: str, role_name: str, create_user_if_not_exists: bool = True):
        if not self.user_exists(user_name):
            if create_user_if_not_exists:
                self.add_user(user_name)
            else:
                raise IndexError(f"用户 {user_name} 不存在")
        if not self.role_exists(role_name):
            raise IndexError(f"角色 {role_name} 不存在")
        if not self.user_has_role(user_name, role_name):
            self.manager.assign_role_to_user(role_name, user_name)
    
    def assign_permissions_to_role(self, role_name: str, permissions_path: str, mode: Literal["white", "black"] = "white", create_path_if_not_exists: bool = True):
        if not self.role_exists(role_name):
            raise IndexError(f"角色 {role_name} 不存在")
        if not self.permission_path_exists(permissions_path):
            if create_path_if_not_exists:
                self.add_permissions(permissions_path)
            else:
                raise IndexError(f"权限路径 {permissions_path} 不存在")
        self.manager.assign_permissions_to_role(role_name, permissions_path, mode)
        self.manager.unassign_permissions_to_role(role_name, permissions_path, 'black' if mode == 'white' else 'white')
        
    def assign_permissions_to_user(self, user_name: str, permissions_path: str, mode: Literal["white", "black"] = "white", create_path_if_not_exists: bool = True):
        if not self.user_exists(user_name):
            raise IndexError(f"用户 {user_name} 不存在")
        if not self.permission_path_exists(permissions_path):
            if create_path_if_not_exists:
                self.add_permissions(permissions_path)
            else:
                raise IndexError(f"权限路径 {permissions_path} 不存在")
        self.manager.assign_permissions_to_user(user_name, permissions_path, mode)
        self.manager.unassign_permissions_to_user(user_name, permissions_path, 'black' if mode == 'white' else 'white')
        
    def unassign_permissions_to_role(self, role_name: str, permissions_path: str):
        self.manager.unassign_permissions_to_role(role_name, permissions_path, 'black')
        
    def unassign_permissions_to_user(self, user_name: str, permissions_path: str):
        self.manager.unassign_permissions_to_user(user_name, permissions_path, 'black')
    
    def add_role_inheritance(self, role: str, inherited_role: str):
        if not self.role_exists(role) or not self.role_exists(inherited_role):
            raise IndexError(f"角色 {role} 或 {inherited_role} 不存在")
        self.manager.set_role_inheritance(role, inherited_role)
    
    def add_permissions(self, permissions_path: str, ignore_if_exists: bool = True):
        if self.permission_path_exists(permissions_path):
            if ignore_if_exists:
                return
            else:
                raise IndexError(f"权限路径 {permissions_path} 已存在")
        else:
            self.manager.add_permissions(permissions_path)
        
    