"""NcatBot 的 Python 包管理工具。

本模块提供了管理 Python 包的工具，包括安装、卸载和依赖管理。
"""

import importlib
import importlib.metadata
import json
import subprocess
import sys
from typing import Any, Dict, List, Optional, Union

from packaging import version
from packaging.markers import UndefinedComparison
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet

from ncatbot.cli.utils.constants import PYPI_SOURCE
from ncatbot.utils import get_log

logger = get_log("CLI")


class PipManagerException(Exception):
    """包管理器操作异常基类。

    当包管理操作失败时抛出，包含详细的错误信息。

    属性:
        message: 异常描述
        original_exception: 原始异常对象（如果有）
    """

    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.original_exception = original_exception
        self.message = f"包管理器错误: {message}"


class PipTool:
    """Python 包管理核心类。

    提供全面的包管理功能，包括：
    - 包的安装/卸载
    - 包信息查询
    - 依赖管理
    - 环境验证
    - 批量操作

    属性:
        python_path (str): Python 解释器路径，默认为当前环境
        base_cmd (List[str]): 基础命令前缀
    """

    installed_packages = None

    def __init__(self, python_path: str = sys.executable):
        """初始化包管理器。

        Args:
            python_path: Python 解释器路径，默认为当前解释器
                        示例: "/usr/bin/python3"

        Raises:
            PipManagerException: 当基础依赖安装失败时
        """
        self.python_path = python_path
        self.base_cmd = [self.python_path, "-m"]

        # 通过自动安装必要的依赖来初始化
        try:
            # 我们可以假设这些已经安装好了
            pass
        except subprocess.CalledProcessError as exc:
            raise PipManagerException("安装基础依赖失败") from exc

    def _run_command(
        self, args: List[str], capture_output: bool = True, pip: bool = True
    ) -> subprocess.CompletedProcess:
        """执行系统命令（基础方法）。

        Args:
            args: 命令参数列表
            capture_output: 是否捕获输出，默认为 True
            pip: 是否在基础命令中添加 pip，默认为 True

        Returns:
            subprocess.CompletedProcess: 命令执行结果对象

        Raises:
            PipManagerException: 当命令执行失败时
        """
        full_cmd = self.base_cmd.copy()
        if pip:
            full_cmd.append("pip")
        full_cmd.extend(args)

        try:
            return subprocess.run(
                full_cmd,
                capture_output=capture_output,
                text=True,
                check=True,
                encoding="utf-8",
            )
        except subprocess.CalledProcessError as exc:
            error_msg = exc.stderr.strip() or exc.stdout.strip() or "未知错误"
            raise PipManagerException(
                f"命令执行失败: {' '.join(exc.cmd)}\n错误: {error_msg}",
                original_exception=exc,
            )

    def install(
        self,
        package: str,
        version: Optional[str] = None,
        upgrade: bool = False,
        no_deps: bool = False,
        index_url: Optional[str] = PYPI_SOURCE,
        extra_args: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """安装 Python 包。

        Args:
            package: 包名
            version: 特定版本号，可选
            upgrade: 是否升级到最新版本，默认为 False
            no_deps: 是否跳过依赖安装，默认为 False
            index_url: 自定义 PyPI 镜像 URL，可选
            extra_args: 额外的 pip 参数，可选

        Returns:
            包含操作结果的字典:
            {
                "status": "success"|"failed",
                "package": 包名,
                "version": 安装的版本（可选）,
                "error": 错误信息（失败时存在）
            }

        示例:
            >>> pm = PipTool()
            >>> pm.install("requests", version="2.25.1", upgrade=True)
            {'status': 'success', 'package': 'requests==2.25.1'}
        """
        PipTool.installed_packages = None  # 清除缓存
        args = ["install"]
        if upgrade:
            args.append("--upgrade")
        if no_deps:
            args.append("--no-deps")
        if index_url:
            args.extend(["--index-url", index_url])
        if version:
            package = f"{package}=={version}"
        args.append(package)
        if extra_args:
            args.extend(extra_args)

        try:
            self._run_command(args, capture_output=False)
            return {"status": "success", "package": package}
        except PipManagerException as exc:
            return {
                "status": "failed",
                "package": package,
                "error": str(exc),
                "version": version or "latest",
            }

    def uninstall(self, package: str, confirm: bool = True) -> Dict[str, Any]:
        """卸载已安装的包。

        Args:
            package: 要卸载的包名
            confirm: 是否自动确认卸载，默认为 True

        Returns:
            包含操作结果的字典:
            {
                "status": "success"|"failed",
                "package": 包名,
                "error": 错误信息（失败时存在）
            }

        示例:
            >>> pm = PipTool()
            >>> pm.uninstall("requests")
            {'status': 'success', 'package': 'requests'}
        """
        args = ["uninstall", "-y"] if confirm else ["uninstall"]
        args.append(package)
        PipTool.installed_packages = None  # 清除缓存

        try:
            self._run_command(args)
            return {"status": "success", "package": package}
        except PipManagerException as exc:
            return {"status": "failed", "package": package, "error": str(exc)}

    def list_installed(self, format: str = "dict") -> Union[List[Dict], str, None]:
        """获取已安装包的列表。

        Args:
            format: 输出格式，支持 dict/json，默认为 dict

        Returns:
            包列表的格式化结果:
            - dict 格式: [{"name": str, "version": str}, ...]
            - json 格式: JSON 字符串
            失败时返回 None

        示例:
            >>> pm = PipTool()
            >>> pm.list_installed()
            [{'name': 'requests', 'version': '2.26.0'}, ...]
        """
        if PipTool.installed_packages:
            return PipTool.installed_packages
        try:
            result = self._run_command(["list", "--format=columns"])
            packages = []

            # 解析表格输出
            for line in result.stdout.strip().split("\n")[2:]:  # 跳过表头
                if not line.strip():
                    continue
                parts = line.split()
                packages.append(
                    {
                        "name": parts[0],
                        "version": parts[1],
                        "location": " ".join(parts[2:]) if len(parts) > 2 else "",
                    }
                )
            PipTool.installed_packages = self._format_output(packages, format)
            return PipTool.installed_packages
        except PipManagerException:
            return None

    def show_info(self, package: str, format: str = "dict") -> Union[Dict, str, None]:
        """获取包的详细信息。

        Args:
            package: 包名
            format: 输出格式，支持 dict/json，默认为 dict

        Returns:
            包信息的格式化结果:
            - dict 格式: 包含所有元数据的字典
            - json 格式: JSON 字符串
            如果包不存在则返回 None

        示例:
            >>> pm = PipTool()
            >>> pm.show_info("requests")
            {
                "name": "requests",
                "version": "2.26.0",
                "summary": "Python HTTP for Humans.",
                ...
            }
        """
        try:
            result = self._run_command(["show", package])
            info = {}

            for line in result.stdout.split("\n"):
                if ": " in line:
                    key, value = line.split(": ", 1)
                    info[key.strip().lower()] = value.strip()

            return self._format_output(info, format)
        except PipManagerException:
            return None

    def _format_output(self, data: Any, format: str) -> Any:
        """内部方法：格式化输出数据。

        Args:
            data: 要格式化的原始数据
            format: 目标格式（dict/json）

        Returns:
            格式化后的数据，如果格式不支持则返回原始数据
        """
        if format == "json":
            return json.dumps(data, indent=2, ensure_ascii=False)
        return data

    def generate_dependency_tree(self, root: Optional[str] = None) -> Dict:
        """生成包依赖树。

        Args:
            root: 指定根包名，默认为显示所有包的依赖

        Returns:
            依赖树的字典结构

        Raises:
            PipManagerException: 当依赖分析失败时

        示例:
            >>> pm = PipTool()
            >>> pm.generate_dependency_tree("requests")
            {
                "package": {
                    "key": "requests",
                    "package_name": "requests",
                    "installed_version": "2.32.3"
                    },
                "dependencies": [
                    {"package": "chardet", "version": "3.0.4"},
                    ...
                ]
            }
        """
        try:
            self._run_command(["install", "pipdeptree"])
            args = ["pipdeptree", "--json"]
            if root:
                args.extend(["-p", root])

            output = self._run_command(args, pip=False).stdout
            return json.loads(output)
        except json.JSONDecodeError as exc:
            raise PipManagerException("依赖树解析失败") from exc
        except Exception as exc:
            raise PipManagerException("依赖分析失败") from exc

    def verify_environment(self) -> Dict[str, List]:
        """验证当前环境依赖兼容性（优化版本）。

        Returns:
            包含冲突的字典:
            {
                "conflicts": [
                    {
                        "package": 包名,
                        "dependency": 依赖名,
                        "required": 所需版本,
                        "installed": 已安装版本
                    },
                    ...
                ]
            }

        示例:
            >>> pm = PipTool()
            >>> pm.verify_environment()
            {'conflicts': [
                {
                    'package': 'package1',
                    'dependency': 'dependency1',
                    'required': '>=1.0.0',
                    'installed': '0.9.0'
                }
            ]}
        """
        conflicts = []
        installed = {}

        # 获取所有已安装的包及其名称和版本（小写标准化）
        for dist in importlib.metadata.distributions():
            name = dist.metadata.get("Name", "").lower()
            if name:  # 跳过没有名称的包
                installed[name] = dist.version

        # 检查每个包的依赖关系
        for dist in importlib.metadata.distributions():
            package_name = dist.metadata.get("Name", "").lower()
            if not package_name:
                continue

            try:
                requirements = importlib.metadata.requires(package_name) or []
            except Exception:
                continue

            for req_str in requirements:
                try:
                    req = Requirement(req_str)
                except Exception:
                    continue  # 跳过依赖解析失败的包

                # 处理环境标记
                if req.marker:
                    try:
                        if not req.marker.evaluate():
                            continue
                    except UndefinedComparison:
                        continue  # 跳过包含未定义变量的条件
                    except Exception:
                        continue  # 跳过其他异常

                dep_name = req.name.lower()
                installed_version = installed.get(dep_name)
                required_version = req.specifier

                # 如果没有版本要求则跳过
                if not required_version:
                    continue

                # 依赖未安装
                if installed_version is None:
                    conflicts.append(
                        {
                            "package": package_name,
                            "dependency": dep_name,
                            "required": str(req.specifier),
                            "installed": None,
                        }
                    )
                    continue

                # 版本不满足要求
                if not req.specifier.contains(installed_version, prereleases=True):
                    conflicts.append(
                        {
                            "package": package_name,
                            "dependency": dep_name,
                            "required": str(req.specifier),
                            "installed": installed_version,
                        }
                    )

        return {"conflicts": conflicts}

    def _parse_requirements(self, package: str) -> List[Requirement]:
        """解析包依赖要求（内部方法）。"""
        info = self.show_info(package)
        if not info or "requires" not in info:
            return []
        return [Requirement(r) for r in info["requires"].split(", ") if r]

    def _check_requirement(self, requirement: Requirement) -> bool:
        """检查依赖是否满足（内部方法）。"""
        installed_info = self.show_info(requirement.name)
        if not installed_info:
            return False
        return requirement.specifier.contains(installed_info["version"])

    def compare_versions(self, installed_version: str, required_version: str) -> bool:
        """比较版本以检查是否满足要求。

        Args:
            installed_version: 已安装的版本号
            required_version: 所需的版本规范

        Returns:
            bool: 如果已安装版本满足要求则为 True
        """
        try:
            # 如果是精确版本比较（无运算符）
            if required_version.isdigit() or all(
                part.isdigit() for part in required_version.split(".")
            ):
                return installed_version == required_version

            if any(op in required_version for op in ["==", ">=", "<=", ">", "<", "~="]):
                # 创建版本规范
                spec = SpecifierSet(required_version)
                # 检查已安装版本是否满足规范
                return version.parse(installed_version) in spec

            # 默认情况，假设需要精确匹配
            return installed_version == required_version
        except Exception:
            return False


def install_pip_dependencies(path: str) -> bool:
    """从 requirements.txt 文件安装依赖。"""
    pm = PipTool()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            pm.install(line)


if __name__ == "__main__":

    def main():
        """示例用法"""
        pm = PipTool()

        # # 安装包
        # print(pm.install("requests"))

        # # 列出已安装包
        # print(pm.list_installed(format="json"))

        # # 显示包信息
        # print(pm.show_info("requests"))

        # # 生成依赖树
        # print()
        # print(json.dumps(pm.generate_dependency_tree("requests")))

        # 环境验证
        print(pm.verify_environment())

    main()
