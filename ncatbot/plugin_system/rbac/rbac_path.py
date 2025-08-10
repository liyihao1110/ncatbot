from typing import Iterator, Tuple, Union


class PermissionPath:
    path_split = "."  # 分隔符
    row_path: str
    path: tuple

    def __init__(self, path: Union[str, "PermissionPath", list, tuple]):
        if isinstance(path, PermissionPath):
            self.row_path = path.row_path
            self.path = path.path
        elif isinstance(path, (list, tuple)):
            self.row_path = self.path_split.join(path)
            self.path = tuple(path)
        elif isinstance(path, str):
            self.row_path = path
            self.path = tuple(path.split(self.path_split))
        else:
            raise ValueError(f"未知类型: {type(path)}")

    def __repr__(self):
        """
        返回对象的字符串表示,用于调试。
        """
        return f"PermissionPath(path={self.row_path}, path_split={self.path_split})"

    def __str__(self):
        """
        返回路径的字符串形式。
        """
        return self.row_path

    def __eq__(self, other):
        """
        比较两个PermissionPath对象是否相等。
        """
        if isinstance(other, PermissionPath):
            return self.path == other.path
        elif isinstance(other, (list, tuple)):
            return self.path == tuple(other)
        elif isinstance(other, str):
            return self.row_path == other
        return False

    def __len__(self):
        """
        返回路径的层级数。
        """
        return len(self.path)

    def __getitem__(self, index: int):
        """
        获取路径的某个层级。
        """
        return self.path[index]

    def __iter__(self) -> Iterator:
        """
        返回路径的迭代器。
        """
        return iter(self.path)

    def __contains__(self, path_node: str) -> bool:
        """
        检查路径中是否包含某个节点。
        """
        return path_node in self.path

    def __call__(self, path: str):
        """
        允许对象作为函数调用,返回一个新的PermissionPath对象。
        """
        return PermissionPath(path)

    def matching_path(self, path: str, complete=False) -> bool:
        if "*" in self.row_path and "*" in path:
            raise ValueError(f"{self.row_path} 与 {path} 不能同时使用通配符")
        if path == self.row_path:
            return True
        if len(self.path) < len(path.split(self.path_split)):
            if not (("**" in path) or ("**" in self.row_path)):
                return False
        template = self if "*" in self.row_path else PermissionPath(path)
        target = PermissionPath(path) if "*" in self.row_path else self
        for i, template_node in enumerate(template):
            target_node = target.get(i)
            if target_node:
                if template_node == "**":
                    return True
                elif template_node == "*":
                    if template.get(i + 1):
                        pass
                    elif not target.get(i + 1):
                        return True
                else:
                    if target_node == template_node:
                        pass
                    else:
                        return False
            else:
                return not complete
        return True

    def join(self, *paths: str) -> "PermissionPath":
        """
        将路径段连接成一个新的PermissionPath。
        """
        # return split.join(self.path)
        new_path = self.row_path
        for p in paths:
            if p:
                new_path = f"{new_path}{self.path_split}{p}"
        return PermissionPath(new_path)

    def split(self) -> Tuple[str, ...]:
        """
        返回路径的分割后的元组形式。
        """
        return self.path

    def get(self, index: int, default=None):
        """
        获取路径的某个层级。
        """
        try:
            respond = self.path[index]
            return respond
        except IndexError:
            return default