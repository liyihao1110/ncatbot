import os
import site
import subprocess
import sys

import requests

from ncatbot.utils.logger import get_log

_log = get_log()


def get_local_package_version(package_name):
    """
    获取当前虚拟环境中已安装包的版本。
    :param package_name: 包名
    :return: 本地版本（字符串）或 None（如果包未安装）
    """
    try:
        # 指定 encoding 参数为 'utf-8'
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        for line in result.stdout.splitlines():
            if line.startswith("ncatbot"):
                parts = line.split()  # 使用 split() 方法分割字符串，去除多余空格
                formatted_line = f"{parts[0]}: {parts[1]}"
                return formatted_line.split(": ")[1]
        return None  # 如果没有找到版本信息或命令执行失败
    except subprocess.CalledProcessError:
        return None  # pip 命令执行失败，包可能未安装


def get_pypi_latest_version(package_name):
    """
    获取 PyPI 上的最新版本。
    :param package_name: 包名
    :return: 最新版本（字符串）或 None（如果无法获取）
    """
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=3)
        response.raise_for_status()  # 如果请求失败会抛出异常
        data = response.json()
        return data["info"]["version"]
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        return None  # 请求失败、超时或包不存在


def is_package_installed(package_name):
    """
    检查包是否已安装。
    :param package_name: 包名
    :return: True 如果包已安装，False 否则
    """
    # 获取当前环境的site-packages路径
    site_packages = site.getsitepackages()  # 对于全局安装包
    user_site_packages = site.getusersitepackages()  # 对于用户安装包

    # 针对不同平台，检查site-packages路径下是否存在该包
    for path in site_packages + [user_site_packages]:
        # 检查指定包是否存在于site-packages目录
        package_path = os.path.join(path, package_name)
        if os.path.exists(package_path):
            return True

        # 对于某些包，可能会有egg-info文件夹，我们也可以检查这个
        egg_info_path = os.path.join(path, f"{package_name}.egg-info")
        if os.path.exists(egg_info_path):
            return True

    return False


def compare_versions(package_name):
    """
    比较本地版本和 PyPI 上的版本，返回比较结果。
    :param package_name: 包名
    :return: 字典，包含安装状态、版本信息及比较结果
    """
    # 初始化返回值
    result = {
        "installed": False,
        "local_version": None,
        "latest_version": None,
        "update_available": False,
        "error": None,
    }

    # 检查包是否已安装
    if not is_package_installed(package_name):
        result["error"] = f"{package_name} 未安装"
        return result

    # 获取本地包版本
    local_version = get_local_package_version(package_name)
    if not local_version:
        result["error"] = f"{package_name} 未安装"
        return result

    # 获取 PyPI 最新版本
    latest_version = get_pypi_latest_version(package_name)
    if not latest_version:
        result["error"] = f"无法获取 {package_name} 在 PyPI 上的最新版本"
        return result

    # 更新结果
    result["installed"] = True
    result["local_version"] = local_version
    result["latest_version"] = latest_version
    result["update_available"] = local_version != latest_version

    return result


def check_version():
    """
    检查包的版本，并输出比较结果。
    """
    package_name = "ncatbot"
    result = compare_versions(package_name)
    if result["installed"]:
        if result["update_available"]:
            _log.warning(
                "NcatBot 有可用更新！推荐您使用以下命令更新：pip install --upgrade ncatbot"
            )
        return True
    else:
        if result["error"].startswith("无法获取"):
            _log.warning("获取 NcatBot 最新版本失败。")
            return True
        _log.error(f"包 {package_name} 未使用 pip 安装，请使用 pip 安装。")
        return False


if __name__ == "__main__":
    check_version()
