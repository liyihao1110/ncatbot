import platform
import subprocess
import sys

import requests

from ncatbot.utils.env_checker import check_linux_permissions
from ncatbot.utils.io import download_file, unzip_file
from ncatbot.utils.literals import (
    INSTALL_SCRIPT_URL,
    WINDOWS_NAPCAT_DIR,
)
from ncatbot.utils.logger import get_log

_log = get_log()


def get_proxy_url():
    """获取 github 代理 URL"""
    github_proxy_urls = [
        "https://ghfast.top/",
        "https://github.7boe.top/",
        "https://cdn.moran233.xyz/",
        "https://gh-proxy.ygxz.in/",
        "https://gh-proxy.lyln.us.kg/",
        "https://github.whrstudio.top/",
        "https://proxy.yaoyaoling.net/",
        "https://ghproxy.net/",
        "https://fastgit.cc/",
        "https://git.886.be/",
        "https://gh-proxy.com/",
    ]
    _log.debug("正在尝试连接 GitHub 代理...")
    for url in github_proxy_urls:
        try:
            _log.debug(f"正在尝试连接 {url}")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return url
        except requests.RequestException as e:
            _log.warning(f"无法连接到 {url}: {e}, 继续尝试下一个代理...")
            continue
    _log.warning("无法连接到任何 GitHub 代理, 将直接连接 GitHub")
    return ""


def get_version():
    """从GitHub获取 napcat 版本号"""
    github_proxy_url = get_proxy_url()
    version_url = f"{github_proxy_url}https://raw.githubusercontent.com/NapNeko/NapCatQQ/main/package.json"
    version_response = requests.get(version_url)
    if version_response.status_code == 200:
        version = version_response.json()["version"]
        _log.debug(f"获取最新版本信息成功, 版本号: {version}")
        return version
    _log.info(f"获取最新版本信息失败, http 状态码: {version_response.status_code}")
    return None


def download_napcat_windows(type: str):
    """
    Windows系统下载安装napcat

    Args:
        type: 安装类型, 可选值为 "install" 或 "update"
    Returns:
        bool: 安装成功返回True, 否则返回False
    """
    if type == "install":
        _log.info("未找到 napcat ，是否要自动安装？")
        if input("输入 Y 继续安装或 N 退出: ").strip().lower() not in ["y", "yes"]:
            exit(0)  # 未安装不安装的直接退出程序
    elif type == "update":
        if input("输入 Y 继续安装或 N 跳过更新: ").strip().lower() not in ["y", "yes"]:
            return False

    try:
        version = get_version()
        github_proxy_url = get_proxy_url()
        download_url = f"{github_proxy_url}https://github.com/NapNeko/NapCatQQ/releases/download/v{version}/NapCat.Shell.zip"
        if not version:
            return False

        # 下载并解压 napcat 客户端
        _log.info(f"下载链接为 {download_url}...")
        _log.info("正在下载 napcat 客户端, 请稍等...")
        download_file(download_url, f"{WINDOWS_NAPCAT_DIR}.zip")
        unzip_file(f"{WINDOWS_NAPCAT_DIR}.zip", WINDOWS_NAPCAT_DIR, True)
        return True
    except Exception as e:
        _log.error("安装失败:", e)
        return False


def download_napcat_cli():
    # 已经弃用
    pass


def download_napcat_linux(type: str):
    """Linux 系统下载安装 napcat 和 cli

    Args:
        type: 安装类型, 可选值为 "install" 或 "update"

    Returns:
        bool: 安装成功返回True, 否则返回False
    """
    if type == "install":
        _log.warning("未找到 napcat ，是否要使用一键安装脚本安装？")
        if input("输入 Y 继续安装或 N 退出: ").strip().lower() not in ["y", "yes"]:
            return False
    elif type == "update":
        _log.info("是否要更新 napcat 客户端？")
        if input("输入 Y 继续安装或 N 跳过更新: ").strip().lower() not in ["y", "yes"]:
            return False

    if check_linux_permissions("root") != "root":
        _log.error("请使用 root 权限运行 ncatbot")
        return False

    try:
        _log.info("正在下载一键安装脚本...")
        process = subprocess.Popen(
            f"sudo bash -c 'curl {INSTALL_SCRIPT_URL} -o install && yes | bash install'",
            shell=True,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        process.wait()
        if process.returncode == 0:
            _log.info("napcat 客户端安装完成。")
            return True
        else:
            _log.error("执行一键安装脚本失败, 请检查命令行输出")
            exit(1)
    except Exception as e:
        _log.error("执行一键安装脚本失败，错误信息:", e)
        exit(1)


def download_napcat(type: str):
    """
    下载和安装 napcat 客户端

    Args:
        type: 安装类型, 可选值为 "install" 或 "update"

    Returns:
        bool: 安装成功返回True, 否则返回False
    """
    if platform.system() == "Windows":
        return download_napcat_windows(type)
    elif platform.system() == "Linux":
        return download_napcat_linux(type)
    return False
