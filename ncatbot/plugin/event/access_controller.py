# 对插件系统封装的权限管理器

import json
import os
from typing import Literal

from ncatbot.plugin.event.event import EventSource
from ncatbot.plugin.RBACManager import RBACManager
from ncatbot.utils import PermissionGroup, config, get_log

LOG = get_log("AccessController")
global_access_controller = None


class BaseRBACManager(RBACManager):
    # 做好 USER 和 GROUP 的分组包装
    def __init__(self, case_sensitive=False, is_group: bool = False):
        super().__init__(case_sensitive)
        self.user_prefix = "user-" if not is_group else "group-"
        self.is_group = is_group

    def role_exist(self, role_name):
        return self.check_availability(role_name=role_name)

    def user_exist(self, user_name: str):
        return self.check_availability(user_name=self.user_prefix + user_name)

    def permission_path_exist(self, path: str):
        return self.check_availability(permissions_path=path)

    def create_user(self, user_name, base_role=PermissionGroup.USER.value):
        """带前缀的创建用户"""
        self.add_user(self.user_prefix + user_name)
        self.assign_role_to_user(base_role, user_name)

    def check_permission(self, user_name, path):
        return super().check_permission(self.user_prefix + user_name, path)

    def assign_role_to_user(self, role_name, user_name):
        if not self.user_has_role(user_name, role_name):
            return super().assign_role_to_user(role_name, self.user_prefix + user_name)

    def unassign_role_to_user(self, role_name, user_name):
        return super().unassign_role_to_user(role_name, self.user_prefix + user_name)

    def assign_permissions_to_user(self, user_name, permissions_path, mode):
        return super().assign_permissions_to_user(
            self.user_prefix + user_name, permissions_path, mode
        )

    def unassign_permissions_to_user(self, user_name, permissions_path, mode):
        try:
            return super().unassign_permissions_to_user(
                self.user_prefix + user_name, permissions_path, mode
            )
        except ValueError:
            pass  # 允许删除不存在的权限

    def user_has_role(self, user_name, role_name):
        return role_name in self.users[self.user_prefix + user_name]["role_list"]


class RoleManagerMixin:
    def __init__(self):
        # 反正要重写, 给点东西做补全提示
        self.ur = BaseRBACManager()
        self.gr = BaseRBACManager(is_group=True)

    def assign_permissions_to_role(
        self,
        role_name: str,
        path: str,
        mode: Literal["black", "white"],
        create_permission_path: bool = False,
    ):
        self._create_permission_path_if_not_exist(path, create_permission_path)
        self.gr.assign_permissions_to_role(role_name, path, mode)
        self.ur.assign_permissions_to_role(role_name, path, mode)

    def unassign_permissions_to_role(
        self,
        role_name: str,
        path: str,
        mode: Literal["black", "white"],
        create_permission_path: bool = False,
    ):
        self._create_permission_path_if_not_exist(path, create_permission_path)
        self.gr.unassign_permissions_to_role(role_name, path, mode)
        self.ur.unassign_permissions_to_role(role_name, path, mode)

    def add_white_list_to_role(
        self, role_name: str, path: str, create_permission_path: bool = False
    ):
        self.unassign_permissions_to_role(
            role_name, path, "black", create_permission_path
        )
        self.assign_permissions_to_role(
            role_name, path, "white", create_permission_path
        )

    def add_black_list_to_role(
        self, role_name: str, path: str, create_permission_path: bool = False
    ):
        self.unassign_permissions_to_role(
            role_name, path, "white", create_permission_path
        )
        self.assign_permissions_to_role(
            role_name, path, "black", create_permission_path
        )

    def user_has_role(self, user_id, role_name):
        self._create_user_if_not_exist(user_id, True)
        return self.ur.user_has_role(user_id, role_name)

    def group_has_role(self, group_id, role_name):
        self._create_group_if_not_exist(group_id, True)
        return self.gr.user_has_role(group_id, role_name)

    def role_exist(self, role_name):
        ure = self.ur.role_exist(role_name)
        gre = self.gr.role_exist(role_name)
        if ure != gre:
            raise ValueError(f"角色 {role_name} 不同步")
        return ure

    def create_role(self, role_name, ignore_exist=False):
        if not self.role_exist(role_name):
            self.ur.add_role(role_name)
            self.gr.add_role(role_name)
        else:
            if not ignore_exist:
                raise ValueError(f"角色 {role_name} 已存在")

    def set_role_inheritance(self, son, father, create: bool = False):
        self._create_role_if_not_exist(son, create)
        self._create_role_if_not_exist(father, create)
        self.ur.set_role_inheritance(son, father)
        self.gr.set_role_inheritance(son, father)

    def _create_role_if_not_exist(self, role_name, create: bool = False):
        if not self.role_exist(role_name):
            if create:
                self.create_role(role_name)
            else:
                raise ValueError(f"角色 {role_name} 不存在")

    def _create_basic_roles(self):
        """创建基本角色, 并给 root 添加权限"""
        self.create_role(PermissionGroup.ROOT.value, ignore_exist=True)
        self.create_role(PermissionGroup.ADMIN.value, ignore_exist=True)
        self.create_role(PermissionGroup.USER.value, ignore_exist=True)
        self.set_role_inheritance(
            PermissionGroup.ROOT.value, PermissionGroup.ADMIN.value
        )
        self.set_role_inheritance(
            PermissionGroup.ADMIN.value, PermissionGroup.USER.value
        )
        self.assign_permissions_to_role(PermissionGroup.ROOT.value, "**", "white")


class PluginAccessController(RoleManagerMixin):
    # 最终开放的权限管理接口
    def __init__(self):
        self.ur = BaseRBACManager()
        self.gr = BaseRBACManager(is_group=True)
        self._load_access()
        self._create_basic_roles()
        self._create_root_user()
        pass

    def _load_access(self):
        LOG.debug("加载权限")
        try:
            if os.path.exists("data/U_access.json"):
                with open("data/U_access.json", "r", encoding="utf-8") as f:
                    self.ur.from_dict(json.JSONDecoder().decode(f.read()))
            else:
                LOG.warning("权限文件不存在, 将创建新的权限文件")
            if os.path.exists("data/G_access.json"):
                with open("data/G_access.json", "r", encoding="utf-8") as f:
                    self.gr.from_dict(json.JSONDecoder().decode(f.read()))
            else:
                LOG.warning("权限文件不存在, 将创建新的权限文件")
        except Exception as e:
            LOG.error(f"加载权限时出错: {e}")

    def _save_access(self):
        LOG.debug("保存权限")
        try:
            with open("data/U_access.json", "w", encoding="utf-8") as f:
                f.write(json.JSONEncoder().encode(self.ur.to_dict()))
            with open("data/G_access.json", "w", encoding="utf-8") as f:
                f.write(json.JSONEncoder().encode(self.gr.to_dict()))
        except Exception as e:
            LOG.error(f"保存权限时出错: {e}")

    def _create_root_user(self):
        """创建 root 级别的用户和群组"""
        self.create_group(PermissionGroup.ROOT.value)
        self.create_user(config.root)
        self.assign_role_to_user(config.root, PermissionGroup.ROOT.value)
        self.assign_role_to_group(
            PermissionGroup.ROOT.value, PermissionGroup.ROOT.value
        )

    def _create_id_if_not_exist(self, id, is_group, create: bool = True):
        manager = self.gr if is_group else self.ur
        if not manager.user_exist(id):
            if create:
                manager.create_user(id)
            else:
                raise ValueError(f"{'群组' if is_group else '用户'} {id} 不存在")

    def _create_user_if_not_exist(self, user_id, create: bool = True):
        """如果用户不存在, 根据配置创建或者报错"""
        self._create_id_if_not_exist(user_id, False, create)

    def _create_group_if_not_exist(self, group_id, create: bool = True):
        """如果群聊不存在, 根据配置创建或者报错"""
        self._create_id_if_not_exist(group_id, True, create)

    def _create_permission_path_if_not_exist(self, path, create: bool = False):
        """如果权限路径不存在, 根据配置创建或者报错"""
        if not self.permission_path_exist(path):
            if create:
                self.create_permission_path(path)
            else:
                raise ValueError(f"权限路径 {path} 不存在")

    def permission_path_exist(self, path):
        ure = self.ur.permission_path_exist(path)
        gre = self.gr.permission_path_exist(path)
        if ure != gre:
            raise ValueError(f"权限路径 {path} 不同步")
        return ure

    def create_permission_path(self, path, ignore_exist: bool = False):
        if not self.permission_path_exist(path):
            self.ur.add_permissions(path)
            self.gr.add_permissions(path)
        elif not ignore_exist:
            raise ValueError(f"权限路径 {path} 已存在")

    def create_user(self, user_id):
        """创建用户"""
        self._create_user_if_not_exist(user_id)

    def create_group(self, group_id):
        """创建群组"""
        self._create_group_if_not_exist(group_id)

    def assign_role_to_user(
        self, user_id, role_name, create_user: bool = True, create_role: bool = True
    ):
        """为用户分配角色"""
        self._create_user_if_not_exist(user_id, create_user)
        self._create_role_if_not_exist(role_name, create_role)
        self.ur.assign_role_to_user(role_name, user_id)

    def unassign_role_to_user(
        self, user_id, role_name, create_user: bool = True, create_role: bool = True
    ):
        """为用户取消角色"""
        self._create_user_if_not_exist(user_id, create_user)
        self._create_role_if_not_exist(role_name, create_role)
        self.ur.unassign_role_to_user(role_name, user_id)

    def assign_role_to_group(
        self, role_name, group_id, create_role: bool = True, create_group: bool = True
    ):
        """为群组分配角色"""
        self._create_group_if_not_exist(group_id, create_group)
        self._create_role_if_not_exist(role_name, create_role)
        self.gr.assign_role_to_user(role_name, group_id)

    def unassign_role_to_group(
        self, role_name, group_id, create_role: bool = True, create_group: bool = True
    ):
        """为群组取消角色"""
        self._create_group_if_not_exist(group_id, create_group)
        self._create_role_if_not_exist(role_name, create_role)
        self.gr.unassign_role_to_user(role_name, group_id)

    def assign_permissions_to_user(
        self,
        user_id,
        path,
        mode: Literal["black", "white"] = "white",
        create_permission_path: bool = False,
        create_user: bool = True,
    ):
        """为用户分配权限"""
        self._create_user_if_not_exist(user_id, create_user)
        self._create_permission_path_if_not_exist(path, create_permission_path)
        self.ur.assign_permissions_to_user(user_id, path, mode)

    def assign_permissions_to_group(
        self,
        group_id,
        path,
        mode: Literal["black", "white"] = "white",
        create_permission_path: bool = False,
        create_user: bool = True,
    ):
        """为群组分配权限"""
        self._create_group_if_not_exist(group_id, create_user)
        self._create_permission_path_if_not_exist(path, create_permission_path)
        self.gr.assign_permissions_to_user(group_id, path, mode)

    def unassign_permissions_to_user(
        self,
        user_id,
        path,
        mode: Literal["black", "white"] = "white",
        create_permission_path: bool = False,
        create_user: bool = True,
    ):
        """为用户取消权限"""
        self._create_user_if_not_exist(user_id, create_user)
        self._create_permission_path_if_not_exist(path, create_permission_path)
        self.ur.unassign_permissions_to_user(user_id, path, mode)

    def unassign_permissions_to_group(
        self,
        group_id,
        path,
        mode: Literal["black", "white"] = "white",
        create_permission_path: bool = False,
        create_user: bool = True,
    ):
        """为群组取消权限"""
        self._create_group_if_not_exist(group_id, create_user)
        self._create_permission_path_if_not_exist(path, create_permission_path)
        self.gr.unassign_permissions_to_user(group_id, path, mode)

    def add_white_list_to_user(
        self,
        user_id,
        path,
        create_permission_path: bool = False,
        create_user: bool = True,
    ):
        self.unassign_permissions_to_user(
            user_id, path, "black", create_permission_path, create_user
        )
        self.assign_permissions_to_user(
            user_id, path, "white", create_permission_path, create_user
        )

    def add_black_list_to_user(
        self,
        user_id,
        path,
        create_permission_path: bool = False,
        create_user: bool = True,
    ):
        self.unassign_permissions_to_user(
            user_id, path, "white", create_permission_path, create_user
        )
        self.assign_permissions_to_user(
            user_id, path, "black", create_permission_path, create_user
        )

    def add_white_list_to_group(
        self,
        group_id,
        path,
        create_permission_path: bool = False,
        create_user: bool = True,
    ):
        self.unassign_permissions_to_group(
            group_id, path, "black", create_permission_path, create_user
        )
        self.assign_permissions_to_group(
            group_id, path, "white", create_permission_path, create_user
        )

    def add_black_list_to_group(
        self,
        group_id,
        path,
        create_permission_path: bool = False,
        create_user: bool = True,
    ):
        self.unassign_permissions_to_group(
            group_id, path, "white", create_permission_path, create_user
        )
        self.assign_permissions_to_group(
            group_id, path, "black", create_permission_path, create_user
        )

    def with_user_permission(self, path, user_id, create_user: bool = True):
        self._create_user_if_not_exist(user_id, create_user)
        return self.ur.check_permission(user_id, path)

    def with_group_permission(self, path, group_id, create_user: bool = True):
        self._create_group_if_not_exist(group_id, create_user)
        return self.gr.check_permission(group_id, path)

    def with_permission(
        self,
        path: str,
        source: EventSource,
        permission_raise: bool = False,
        create_user: bool = True,
    ):
        """检查消息来源是否拥有对应权限"""
        group_id = source.group_id if not permission_raise else "root"
        return self.with_user_permission(
            path, source.user_id, create_user=create_user
        ) and self.with_group_permission(path, group_id, create_user=create_user)

    def user_exist(self, user_id):
        return self.ur.user_exist(user_id)

    def group_exist(self, group_id):
        return self.gr.user_exist(group_id)


def get_global_access_controller() -> PluginAccessController:
    global global_access_controller
    if global_access_controller is None:
        global_access_controller = PluginAccessController()
    return global_access_controller
