# 安装 napcat

import json
import os
import platform
import subprocess
import sys

import requests

from ncatbot.utils import (
    INSTALL_SCRIPT_URL,
    LINUX_NAPCAT_DIR,
    WINDOWS_NAPCAT_DIR,
    config,
    download_file,
    get_log,
    get_proxy_url,
    unzip_file,
)
from ncatbot.utils.env_checker import (
    check_linux_permissions,
    check_self_package_version,
)

LOG = get_log("adapter.nc.install")


def get_napcat_dir():
    """获取 napcat 安装目录"""
    if platform.system() == "Windows":
        return WINDOWS_NAPCAT_DIR
    elif platform.system() == "Linux":
        return LINUX_NAPCAT_DIR
    else:
        LOG.warning("不支持的系统类型: %s, 可能需要自行适配", platform.system())
        LOG.warning("默认使用工作目录下 napcat/ 目录")
        return os.path.join(os.getcwd(), "napcat")


def get_napcat_version():
    """从GitHub获取 napcat 版本号"""
    github_proxy_url = get_proxy_url()
    version_url = f"{github_proxy_url}https://raw.githubusercontent.com/NapNeko/NapCatQQ/main/package.json"
    version_response = requests.get(version_url)
    if version_response.status_code == 200:
        version = version_response.json()["version"]
        LOG.debug(f"获取最新版本信息成功, 版本号: {version}")
        return version
    LOG.info(f"获取最新版本信息失败, http 状态码: {version_response.status_code}")
    return None


def check_windows_qq_version():
    pass


def install_napcat_windows(type: str):
    # TODO 检查 Windows QQ 的版本是否符合要求
    """
    Windows系统下载安装napcat

    Args:
        type: 安装类型, 可选值为 "install" 或 "update"
    Returns:
        bool: 安装成功返回 True, 否则返回 False
    """
    if type == "install":
        LOG.info("未找到 napcat ，是否要自动安装？")
        if input("输入 Y 继续安装或 N 退出: ").strip().lower() not in ["y", "yes"]:
            exit(0)  # 未安装不安装的直接退出程序
    elif type == "update":
        if input("输入 Y 继续安装或 N 跳过更新: ").strip().lower() not in ["y", "yes"]:
            return False

    try:
        version = get_napcat_version()
        github_proxy_url = get_proxy_url()
        download_url = f"{github_proxy_url}https://github.com/NapNeko/NapCatQQ/releases/download/v{version}/NapCat.Shell.zip"
        if not version:
            return False

        # 下载并解压 napcat 客户端
        LOG.info(f"下载链接为 {download_url}...")
        LOG.info("正在下载 napcat 客户端, 请稍等...")
        download_file(download_url, f"{WINDOWS_NAPCAT_DIR}.zip")
        unzip_file(f"{WINDOWS_NAPCAT_DIR}.zip", WINDOWS_NAPCAT_DIR, True)
        check_windows_qq_version()
        return True
    except Exception as e:
        LOG.error("安装失败:", e)
        return False


def install_napcat_linux(type: str):
    """Linux 系统下载安装 napcat 和 cli

    Args:
        type: 安装类型, 可选值为 "install" 或 "update"

    Returns:
        bool: 安装成功返回True, 否则返回False
    """
    if type == "install":
        LOG.warning("未找到 napcat ，是否要使用一键安装脚本安装？")
        if input("输入 Y 继续安装或 N 退出: ").strip().lower() not in ["y", "yes"]:
            return False
    elif type == "update":
        LOG.info("是否要更新 napcat 客户端？")
        if input("输入 Y 继续安装或 N 跳过更新: ").strip().lower() not in ["y", "yes"]:
            return False

    if check_linux_permissions("root") != "root":
        LOG.error("请使用 root 权限运行 ncatbot")
        return False

    try:
        LOG.info("正在下载一键安装脚本...")
        process = subprocess.Popen(
            f"sudo bash -c 'curl {INSTALL_SCRIPT_URL} -o install && yes | bash install'",
            shell=True,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        process.wait()
        if process.returncode == 0:
            LOG.info("napcat 客户端安装完成。")
            return True
        else:
            LOG.error("执行一键安装脚本失败, 请检查命令行输出")
            exit(1)
    except Exception as e:
        LOG.error("执行一键安装脚本失败，错误信息:", e)
        exit(1)


def install_napcat(type: str):
    """
    下载和安装 napcat 客户端

    Args:
        type: 安装类型, 可选值为 "install" 或 "update"

    Returns:
        bool: 安装成功返回 True, 否则返回 False
    """
    if platform.system() == "Windows":
        return install_napcat_windows(type)
    elif platform.system() == "Linux":
        return install_napcat_linux(type)
    return False


def check_permission():
    if check_linux_permissions("root") != "root":
        LOG.error("请使用 root 权限运行 ncatbot")
        exit(1)


def check_ncatbot_install():
    """检查 ncatbot 版本, 以及是否正确安装"""
    if not config.skip_ncatbot_install_check:
        # 检查版本和安装方式
        version_ok = check_self_package_version()
        if not version_ok:
            exit(0)
    else:
        LOG.info("调试模式, 跳过 ncatbot 安装检查")


def is_napcat_install():
    napcat_dir = get_napcat_dir()
    return os.path.exists(napcat_dir)


def install_update_napcat():
    """安装 napcat 或者检查 napcat 更新并重新安装"""
    if not is_napcat_install():
        if not install_napcat("install"):
            LOG.error("NapCat 安装失败")
            exit(1)
    elif config.check_napcat_update:
        # 检查 napcat 版本更新
        with open(
            os.path.join(get_napcat_dir(), "package.json"), "r", encoding="utf-8"
        ) as f:
            version = json.load(f)["version"]
            LOG.info(f"当前 napcat 版本: {version}, 正在检查更新...")

        github_version = get_napcat_version()
        if version != github_version:
            LOG.info(f"发现新版本: {github_version}, 是否要更新 napcat 客户端？")
            if not install_napcat("update"):
                LOG.info(f"跳过 napcat {version} 更新")
        else:
            LOG.info("当前 napcat 已是最新版本")
