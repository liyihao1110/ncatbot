import importlib.metadata as _meta
import subprocess
import sys
import logging
from packaging.requirements import Requirement
from packaging.version import Version

LOG = logging.getLogger('PackageHelper')
# TODO 不兼容检测

class PackageHelper:
    """检查并确保某个 PEP-508 需求字符串被满足，否则自动安装/升级"""

    @staticmethod
    def ensure(req_str: str) -> None:
        req = Requirement(req_str)
        dist_name = req.name

        try:
            installed_ver = _meta.version(dist_name)
        except _meta.PackageNotFoundError:
            LOG.info("缺失包 %s，开始安装", dist_name)
            PackageHelper._pip_install(req_str)
            return

        # 已安装 → 检查版本规格
        if not req.specifier.contains(Version(installed_ver)):
            LOG.warning("版本不符(现有 %s, 需求 %s)，尝试升级",
                        installed_ver, req_str)
            PackageHelper._pip_install(req_str)
        else:
            LOG.info("依赖已满足: %s", req_str)

    # ---------- 内部 ----------
    @staticmethod
    def _pip_install(spec: str) -> None:
        cmd = [sys.executable, "-m", "pip", "install", spec]
        LOG.debug("执行: %s", " ".join(cmd))
        subprocess.check_call(cmd)