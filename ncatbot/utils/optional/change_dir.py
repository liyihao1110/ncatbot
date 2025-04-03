# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-18 21:06:40
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-16 14:08:58
# @Description  : 上下文管理器, 用于暂时切换工作路径, 使用插件的私有数据目录时需要
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------


import os
import tempfile
from contextlib import ContextDecorator
from pathlib import Path
from typing import Optional, Union
from uuid import UUID, uuid4

from ..logger import get_log

LOG = get_log("ChangeDir")


class ChangeDir(ContextDecorator):
    """
    上下文管理器,用于暂时切换工作路径。
    支持自动恢复原始路径和目录创建/清理。
    """

    _DIRS_REGISTRY: dict[UUID, str] = {}  # 保存所有可用目录的 UUID 和路径

    def __init__(
        self,
        path: Optional[Union[str, UUID, Path]] = None,
        create_missing: bool = False,
        keep_temp: bool = False,
        init_path: bool = False,
    ) -> None:
        """
        初始化工作路径切换器。

        Args
            path (Optional[str | UUID | Path]): 新的工作路径。若为 None,则创建临时目录。
            create_missing (bool): 如果目标路径不存在,是否自动创建。
            keep_temp (bool): 是否在退出后暂存临时目录。
            init_path (bool): 立刻初始化路径。否则在使用时初始化
        """
        self.create_missing = create_missing
        self.keep_temp = keep_temp
        self.temp_dir = None  # 临时目录管理器
        self.origin_path = os.getcwd()
        self.path = path
        self.init = False
        self.new_path = ""
        self.dir_id = None  # 目录对应的 UUID
        if init_path:
            self.init_path()

    def init_path(self):
        """初始化目标路径"""
        if self.init:
            return
        if isinstance(self.path, str):
            self.new_path = os.path.abspath(self.path)
            self._handle_str_path()
        elif isinstance(self.path, UUID):
            # 从路径注册表中加载路径
            self._load_path(self.path)
        elif isinstance(self.path, Path):
            self.new_path = str(self.path.absolute())
            self._handle_str_path()
        else:
            # 未指定路径,创建临时目录
            self._create_temp_directory()
        self.init = True

    def _handle_str_path(self) -> None:
        """
        处理以字符串形式传入的路径。
        """
        if not os.path.exists(self.new_path):
            if self.create_missing:
                os.makedirs(self.new_path, exist_ok=True)
                LOG.debug(f"创建文件夹: {self.new_path}")
            else:
                raise FileNotFoundError(f"路径不存在: {self.new_path}")
        if not os.path.isdir(self.new_path):
            raise NotADirectoryError(f"路径不是文件夹: {self.new_path}")
        # 生成 UUID 并保存到注册表
        self.dir_id = uuid4()
        self._DIRS_REGISTRY[self.dir_id] = self.new_path
        LOG.debug(f"为目录 [{self.dir_id}] 注册路径: {self.new_path}")

    def _load_path(self, path_id: UUID) -> None:
        """
        从路径注册表中加载路径。
        """
        self.new_path = self._DIRS_REGISTRY.get(path_id, "")
        if not self.new_path or not os.path.exists(self.new_path):
            raise FileNotFoundError(f"路径未找到: {path_id}")
        LOG.debug(f"加载目录: {path_id} → {self.new_path}")

    def _create_temp_directory(self) -> None:
        """
        创建临时目录并记录相关信息。
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dir_id = uuid4()
        self.new_path = self.temp_dir.name
        self._DIRS_REGISTRY[self.dir_id] = self.new_path
        LOG.debug(f"创建临时目录 [{self.dir_id}]: {self.new_path}")

    def __enter__(self) -> "UUID":
        """
        进入上下文时,初始化并切换到新的工作路径。
        """
        self.init_path()
        os.chdir(self.new_path)
        return self.dir_id if self.dir_id else UUID(int=0)

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        退出上下文时,恢复原始路径并清理临时目录。
        """
        try:
            os.chdir(self.origin_path)
            LOG.debug(f"恢复目录: {self.origin_path}")
        except Exception as e:
            LOG.error(f"恢复原始目录失败: {e}")
            return False  # 允许异常传播

        # 清理临时目录 如果需要
        if self.temp_dir and not self.keep_temp:
            try:
                self.temp_dir.cleanup()
                LOG.debug(f"删除临时目录: {self.new_path}")
                # 移除临时目录的注册记录
                if self.dir_id in self._DIRS_REGISTRY:
                    del self._DIRS_REGISTRY[self.dir_id]
            except Exception as e:
                LOG.error(f"删除临时目录失败: {e}")

        return True  # 阻止异常传播

    def __del__(self) -> None:
        """
        清理临时目录（即使上下文管理器未正常退出）。
        """
        # 清理临时目录 如果需要
        if self.temp_dir and not self.keep_temp:
            try:
                self.temp_dir.cleanup()
                LOG.debug(f"对象销毁时清理临时目录: {self.new_path}")
                # 移除临时目录的注册记录
                if self.dir_id in self._DIRS_REGISTRY:
                    del self._DIRS_REGISTRY[self.dir_id]
            except Exception as e:
                LOG.warning(f"清理临时目录失败: {e}")
