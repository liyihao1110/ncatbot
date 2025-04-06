# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-03-08 12:47:07
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-09 18:33:20
# @Description  : 应该只有插件加载会用，有空可以塞进去，而不是这个文件
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
import importlib
import json
import subprocess
import sys
from typing import Any, Dict, List, Optional, Union

from packaging import version
from packaging.markers import UndefinedComparison
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet

from ncatbot.utils import PYPI_URL


class PipManagerException(Exception):
    """包管理器操作异常基类

    当包管理操作失败时抛出, 包含详细的错误信息

    Attributes:
        message: 异常描述信息
        original_exception: 原始异常对象(如果有)
    """

    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.original_exception = original_exception
        self.message = f"包管理错误: {message}"


class PipTool:
    """Python包管理核心类

    提供完整的包管理功能, 包括：
    - 包安装/卸载
    - 包信息查询
    - 依赖管理
    - 环境验证
    - 批量操作

    Attributes:
        python_path (str): Python解释器路径, 默认为当前环境
        base_cmd (List[str]): 基础命令前缀
    """

    def __init__(self, python_path: str = sys.executable):
        """初始化包管理器

        Args:
            python_path: Python解释器路径, 默认使用当前环境解释器
                        示例: "/usr/bin/python3"

        Raises:
            PipManagerException: 当基础依赖安装失败时抛出
        """
        self.python_path = python_path
        self.base_cmd = [self.python_path, "-m"]

        # 初始化时自动安装必要依赖
        try:
            self._run_command(
                ["pip", "install", "--upgrade", "setuptools", "wheel", "-i", PYPI_URL],
                pip=False,
            )
        except subprocess.CalledProcessError as exc:
            raise PipManagerException("基础依赖安装失败") from exc

    def _run_command(
        self, args: List[str], capture_output: bool = True, pip: bool = True
    ) -> subprocess.CompletedProcess:
        """执行系统命令的基础方法

        Args:
            args: 命令参数列表
            capture_output: 是否捕获输出, 默认True
            pip: 是否在基础命令中添加pip, 默认True

        Returns:
            subprocess.CompletedProcess: 命令执行结果对象

        Raises:
            PipManagerException: 当命令执行失败时抛出
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
                f"命令执行失败: {' '.join(exc.cmd)}\n错误信息: {error_msg}",
                original_exception=exc,
            )

    def install(
        self,
        package: str,
        version: Optional[str] = None,
        upgrade: bool = False,
        no_deps: bool = False,
        index_url: Optional[str] = PYPI_URL,
        extra_args: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """安装Python包

        Args:
            package: 包名称
            version: 指定版本号, 可选
            upgrade: 是否升级到最新版本, 默认False
            no_deps: 是否跳过依赖安装, 默认False
            index_url: 自定义PyPI镜像源URL, 可选
            extra_args: 额外pip参数列表, 可选

        Returns:
            包含操作结果的字典:
            {
                "status": "success"|"failed",
                "package": 包名称,
                "version": 安装版本(可选),
                "error": 错误信息(失败时存在)
            }

        Example:
            >>> pm = PackageManager()
            >>> pm.install("requests", version="2.25.1", upgrade=True)
            {'status': 'success', 'package': 'requests==2.25.1'}
        """
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
            result = self._run_command(args, capture_output=False)
            return {"status": "success", "package": package}
        except PipManagerException as exc:
            return {
                "status": "failed",
                "package": package,
                "error": str(exc),
                "version": version or "latest",
            }

    def uninstall(self, package: str, confirm: bool = True) -> Dict[str, Any]:
        """卸载已安装的包

        Args:
            package: 要卸载的包名称
            confirm: 是否自动确认卸载, 默认True

        Returns:
            包含操作结果的字典:
            {
                "status": "success"|"failed",
                "package": 包名称,
                "error": 错误信息(失败时存在)
            }

        Example:
            >>> pm.uninstall("requests")
            {'status': 'success', 'package': 'requests'}
        """
        args = ["uninstall", "-y"] if confirm else ["uninstall"]
        args.append(package)

        try:
            self._run_command(args)
            return {"status": "success", "package": package}
        except PipManagerException as exc:
            return {"status": "failed", "package": package, "error": str(exc)}

    def list_installed(self, format: str = "dict") -> Union[List[Dict], str, None]:
        """获取已安装包列表

        Args:
            format: 输出格式, 支持 dict/json, 默认dict

        Returns:
            包列表的格式化结果:
            - dict格式: [{"name": str, "version": str}, ...]
            - json格式: JSON字符串
            失败时返回None

        Example:
            >>> pm.list_installed()
            [{'name': 'requests', 'version': '2.26.0'}, ...]
        """
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

            return self._format_output(packages, format)
        except PipManagerException:
            return None

    def show_info(self, package: str, format: str = "dict") -> Union[Dict, str, None]:
        """获取包的详细信息

        Args:
            package: 包名称
            format: 输出格式, 支持 dict/json, 默认dict

        Returns:
            包信息的格式化结果:
            - dict格式: 包含所有元数据的字典
            - json格式: JSON字符串
            包不存在时返回None

        Example:
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
        """内部方法：格式化输出数据

        Args:
            data: 要格式化的原始数据
            format: 目标格式 (dict/json)

        Returns:
            格式化后的数据, 格式不支持时返回原数据
        """
        if format == "json":
            return json.dumps(data, indent=2, ensure_ascii=False)
        return data

    def generate_dependency_tree(self, root: Optional[str] = None) -> Dict:
        """生成包依赖树

        Args:
            root: 指定根包名称, 默认显示所有包的依赖

        Returns:
            依赖树的字典结构

        Raises:
            PipManagerException: 当依赖分析失败时抛出

        Example:
            >>> await pm.generate_dependency_tree("requests")
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
        """验证当前环境依赖兼容性（优化版）"""
        conflicts = []
        installed = {}

        # 获取所有已安装包的名称和版本（小写规范化）
        for dist in importlib.metadata.distributions():
            name = dist.metadata.get("Name", "").lower()
            if name:  # 跳过无法获取名称的包
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
                except:
                    continue  # 跳过解析失败的依赖

                # 处理环境标记
                if req.marker:
                    try:
                        if not req.marker.evaluate():
                            continue
                    except UndefinedComparison:
                        continue  # 跳过包含未定义变量的条件
                    except:
                        continue  # 其他异常跳过

                dep_name = req.name.lower()
                installed_version = installed.get(dep_name)
                required_version = req.specifier

                # 跳过没有版本要求
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
        """解析包的依赖要求(内部方法)"""
        info = self.show_info(package)
        if not info or "requires" not in info:
            return []
        return [Requirement(r) for r in info["requires"].split(", ") if r]

    def _check_requirement(self, requirement: Requirement) -> bool:
        """检查依赖是否满足(内部方法)"""
        installed_info = self.show_info(requirement.name)
        if not installed_info:
            return False
        return requirement.specifier.contains(installed_info["version"])

    def compare_versions(self, installed_version: str, required_version: str) -> bool:
        """比较版本号是否满足"""
        try:
            # 如果是精确版本号比较（没有操作符）
            if required_version.isdigit() or all(
                part.isdigit() for part in required_version.split(".")
            ):
                return installed_version == required_version

            if any(op in required_version for op in ["==", ">=", "<=", ">", "<", "~="]):
                # 创建版本说明符
                spec = SpecifierSet(required_version)
                # 检查已安装版本是否满足版本说明符
                return version.parse(installed_version) in spec

            # 默认情况下，假设需要完全匹配
            return installed_version == required_version
        except Exception:
            return False


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
