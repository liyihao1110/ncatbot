## RBACManager 使用文档（user_exists 及以下）

本文档介绍 `ncatbot.plugin_system.rbac.rbac_manager.RBACManager` 中从 `user_exists` 起及其后续公开方法的使用方式、参数与注意事项。示例基于 Windows/PowerShell 环境，Python 代码与平台无关。

> 说明
> - RBACManager 封装了底层 `_RBACManager` 与权限 Trie 逻辑，负责用户/角色/权限路径的日常管理。
> - 默认大小写敏感（case_sensitive=True），路径匹配支持通配符（例如 `a.*.c`）。
> - 在实例化时，会确保基础角色存在（User/Admin/Root），调整继承关系，并将配置中的 root 用户加入 Root 角色。


## API 参考

以下 API 按照在源码中自 `user_exists` 开始的顺序罗列。

### user_exists

#### 函数原型

```python
class RBACManager:
    ...
    def user_exists(self, user_name: str) -> bool:
        """"
        判断用户是否存在。
        Args:
            user_name: 用户名
        Returns:
            bool，存在为 True。
        """
        ...
```

#### 示例用法

```python
class MyPlugin(NcatBotPlugin):
    ...
    async def some_method(self):
        if self.rbac_manager.user_exists("alice"):
            print("User 'alice' exists.")
```

### role_exists

#### 函数原型

```python
class RBACManager:
    ...
    def role_exists(self, role_name: str) -> bool:
        """
        判断角色是否存在。
        Args:
            role_name: 角色名
        Returns:
            bool，存在为 True。
        """
        ...
```

#### 示例用法

```python
if self.rbac_manager.role_exists("auditor"):
    print("Role 'auditor' exists.")
```

### permission_path_exists

#### 函数原型

```python
class RBACManager:
    ...
    def permission_path_exists(self, permissions_path: str) -> bool:
        """
        判断权限路径是否已在权限 Trie 中注册。
        Args:
            permissions_path: 权限路径（大小写敏感，支持通配符）
        Returns:
            bool，存在为 True。
        """
        ...
```

#### 示例用法

```python
if not self.rbac_manager.permission_path_exists("plugin.demo.read"):
    print("permission path not registered")
```

### check_permission

#### 函数原型

```python
from typing import Literal

class RBACManager:
    ...
    def check_permission(self, user_name: str, path: str, create_user_if_not_exists: bool = True) -> bool:
        """
        检查用户是否拥有某权限路径。
        Args:
            user_name: 用户名
            path: 权限路径（支持通配符）
            create_user_if_not_exists: 用户不存在时是否自动创建（默认 True）
        Returns:
            bool，允许为 True。
        """
        ...
```

#### 示例用法

```python
allowed = self.rbac_manager.check_permission("alice", "plugin.demo.read")
if not allowed:
    print("no permission")

# 严格控制用户生命周期时：
try:
    allowed = self.rbac_manager.check_permission("bob", "plugin.demo.read", create_user_if_not_exists=False)
except IndexError:
    print("user not exists")
```

### user_has_role

#### 函数原型

```python
class RBACManager:
    ...
    def user_has_role(self, user_name: str, role_name: str) -> bool:
        """
        判断用户是否拥有指定角色。
        Args:
            user_name: 用户名
            role_name: 角色名
        Returns:
            bool，拥有为 True。
        """
        ...
```

#### 示例用法

```python
if not self.rbac_manager.user_has_role("alice", "auditor"):
    print("alice has no 'auditor' role")
```

### add_role

#### 函数原型

```python
class RBACManager:
    ...
    def add_role(self, role_name: str, ignore_if_exists: bool = True):
        """
        创建新角色。
        Args:
            role_name: 角色名
            ignore_if_exists: 若已存在是否忽略（默认 True）
        """
        ...
```

#### 示例用法

```python
self.rbac_manager.add_role("auditor")
```

### add_user

#### 函数原型

```python
class RBACManager:
    ...
    def add_user(self, user_name: str, role_list: list[str] | None = None, ignore_if_exists: bool = True):
        """
        创建新用户，可选地赋予一组角色。
        Args:
            user_name: 用户名
            role_list: 角色列表（可选）
            ignore_if_exists: 已存在时是否忽略（默认 True）
        """
        ...
```

#### 示例用法

```python
self.rbac_manager.add_user("alice")
```

### assign_role_to_user

#### 函数原型

```python
class RBACManager:
    ...
    def assign_role_to_user(self, user_name: str, role_name: str, create_user_if_not_exists: bool = True):
        """
        为用户赋予角色。
        Args:
            user_name: 用户名
            role_name: 角色名
            create_user_if_not_exists: 用户不存在是否自动创建（默认 True）
        """
        ...
```

#### 示例用法

```python
self.rbac_manager.assign_role_to_user("alice", "auditor")
```

### assign_permissions_to_role

#### 函数原型

```python
from typing import Literal

class RBACManager:
    ...
    def assign_permissions_to_role(self, role_name: str, permissions_path: str, mode: Literal["white", "black"] = "white", create_path_if_not_exists: bool = True):
        """
        为角色分配权限（白名单或黑名单）。
        Args:
            role_name: 角色名
            permissions_path: 权限路径
            mode: "white" 或 "black"（默认 "white"）
            create_path_if_not_exists: 权限不存在时是否自动创建（默认 True）
        """
        ...
```

#### 示例用法

```python
self.rbac_manager.add_permissions("plugin.demo.read")
self.rbac_manager.assign_permissions_to_role("auditor", "plugin.demo.read", mode="white")
```

### assign_permissions_to_user

#### 函数原型

```python
from typing import Literal

class RBACManager:
    ...
    def assign_permissions_to_user(self, user_name: str, permissions_path: str, mode: Literal["white", "black"] = "white", create_path_if_not_exists: bool = True):
        """
        为用户直接分配权限（白/黑名单）。
        Args:
            user_name: 用户名
            permissions_path: 权限路径
            mode: "white" 或 "black"（默认 "white"）
            create_path_if_not_exists: 权限不存在时是否自动创建（默认 True）
        """
        ...
```

#### 示例用法

```python
self.rbac_manager.add_permissions("plugin.demo.write")
self.rbac_manager.assign_permissions_to_user("alice", "plugin.demo.write", mode="white")
```

### unassign_role_to_user

#### 函数原型

```python
class RBACManager:
    ...
    def unassign_role_to_user(self, user_name: str, role_name: str):
        """
        撤销用户的某个角色。
        Args:
            user_name: 用户名
            role_name: 角色名
        """
        ...
```

#### 示例用法

```python
self.rbac_manager.unassign_role_to_user("alice", "auditor")
```

### unassign_permissions_to_role

#### 函数原型

```python
class RBACManager:
    ...
    def unassign_permissions_to_role(self, role_name: str, permissions_path: str):
        """
        从角色撤销某权限。
        Args:
            role_name: 角色名
            permissions_path: 权限路径
        """
        ...
```

#### 示例用法

```python
self.rbac_manager.unassign_permissions_to_role("auditor", "plugin.demo.read")
```

### unassign_permissions_to_user

#### 函数原型

```python
class RBACManager:
    ...
    def unassign_permissions_to_user(self, user_name: str, permissions_path: str):
        """
        从用户撤销某权限。
        Args:
            user_name: 用户名
            permissions_path: 权限路径
        """
        ...
```

#### 示例用法

```python
self.rbac_manager.unassign_permissions_to_user("alice", "plugin.demo.write")
```

### add_role_inheritance

#### 函数原型

```python
class RBACManager:
    ...
    def add_role_inheritance(self, role: str, inherited_role: str):
        """
        设置角色继承关系（role 继承 inherited_role 的权限）。
        Args:
            role: 子角色
            inherited_role: 被继承的父角色
        """
        ...
```

#### 示例用法

```python
self.rbac_manager.add_role("user")
self.rbac_manager.add_role("auditor")
self.rbac_manager.add_role_inheritance("auditor", "user")
```

### add_permissions

#### 函数原型

```python
class RBACManager:
    ...
    def add_permissions(self, permissions_path: str, ignore_if_exists: bool = True):
        """
        向权限 Trie 注册一个权限路径。
        Args:
            permissions_path: 权限路径
            ignore_if_exists: 已存在时是否忽略（默认 True）
        """
        ...
```

#### 示例用法

```python
self.rbac_manager.add_permissions("plugin.demo.read")
```

---

## 行为与边界说明

- 大小写敏感：默认启用。若你的系统希望大小写不敏感，需要在更底层的 `_RBACManager` 初始化里调整（当前 RBACManager 未暴露该开关）。
- 匹配规则：
  - 黑名单优先于白名单；精确匹配优先于通配符匹配；未命中则拒绝。
  - 通配符覆盖示例：`a.*.c` 可匹配 `a.x.c`。
- 自动创建用户：
  - `check_permission` 和 `user_has_role` 在用户不存在时会“隐式创建用户”，这会改变系统状态。若不希望副作用，请自行判定 `user_exists` 后再调用。
- 白/黑名单互斥：
  - 通过 `assign_permissions_to_*` 分配时会自动从相反名单移除同一路径，避免冲突。
- 已知实现限制/问题：
  1) `add_role(ignore_if_exists=False)` 在角色原本不存在的情况下也可能抛出异常；
  2) `add_user(..., role_list=[...])` 的赋权参数传递有误，可能不会按预期将角色赋给用户；
  3) `unassign_permissions_to_role` / `unassign_permissions_to_user` 仅从黑名单移除，无法直接移除白名单条目——可调用底层 `manager` 同名方法并显式传入 `mode` 作为临时替代。

---

## 进阶示例：白/黑名单与继承

```python
# 角色继承：auditor 继承 user
manager.add_role("user")
manager.add_role("auditor")
manager.add_role_inheritance("auditor", "user")

# 为 user 赋白名单
manager.add_permissions("plugin.report.view")
manager.assign_permissions_to_role("user", "plugin.report.view", mode="white")

# 为 auditor 加黑名单，显式屏蔽某细分路径
manager.add_permissions("plugin.report.view.sensitive")
manager.assign_permissions_to_role("auditor", "plugin.report.view.sensitive", mode="black")

manager.add_user("bob")
manager.assign_role_to_user("bob", "auditor")

assert manager.check_permission("bob", "plugin.report.view") is True
assert manager.check_permission("bob", "plugin.report.view.sensitive") is False
```

---

## 常见问答

- Q：如何彻底撤销用户/角色的某个“白名单”权限？
  - A：目前封装层的 `unassign_permissions_to_*` 会从“黑名单”移除。如果需要从白名单移除，请调用底层 `manager.unassign_permissions_to_*` 并传入 `mode="white"`。

- Q：`check_permission` 的通配符是如何工作的？
  - A：底层使用 Trie 进行分段匹配，支持 `*` 作为通配符段进行覆盖匹配，黑名单优先、精确优先。

- Q：如何避免 `check_permission` 隐式创建用户？
  - A：先用 `user_exists` 判定用户存在，再以 `create_user_if_not_exists=False` 调用 `check_permission`，或自行保障用户生命周期。
