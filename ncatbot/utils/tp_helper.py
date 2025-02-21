import os
import platform
import subprocess
import sys
import zipfile

import requests
from tqdm import tqdm

from ncatbot.utils.env_checker import check_linux_permissions
from ncatbot.utils.literals import NAPCAT_DIR
from ncatbot.utils.logger import get_log

_log = get_log()


def get_proxy_url():
    """获取 github 代理 URL"""
    github_proxy_urls = [
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
        "https://ghfast.top/",
    ]
    _log.info("正在尝试连接 GitHub 代理...")
    for url in github_proxy_urls:
        try:
            _log.info(f"正在尝试连接 {url}")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return url
        except requests.RequestException as e:
            _log.info(f"无法连接到 {url}: {e}, 继续尝试下一个代理...")
            continue
    _log.info("无法连接到任何 GitHub 代理, 将直接连接 GitHub")
    return ""


def get_version(github_proxy_url: str):
    """从GitHub获取 napcat 版本号"""
    version_url = f"{github_proxy_url}https://raw.githubusercontent.com/NapNeko/NapCatQQ/main/package.json"
    version_response = requests.get(version_url)
    if version_response.status_code == 200:
        version = version_response.json()["version"]
        _log.info(f"获取最新版本信息成功, 版本号: {version}")
        return version
    _log.info(f"获取最新版本信息失败, http 状态码: {version_response.status_code}")
    return None


def download_napcat_windows(type: str, base_path: str):
    """
    Windows系统下载安装napcat

    Args:
        type: 安装类型, 可选值为 "install" 或 "update"
        base_path: 安装路径

    Returns:
        bool: 安装成功返回True, 否则返回False
    """
    if type == "install":
        _log.info("未找到 napcat ，是否要自动安装？")
        if input("输入 Y 继续安装或 N 退出: ").strip().lower() not in ["y", "yes"]:
            return False
    elif type == "update":
        _log.info("是否要更新 napcat 客户端？")
        if input("输入 Y 继续安装或 N 跳过更新: ").strip().lower() not in ["y", "yes"]:
            return False

    try:
        github_proxy_url = get_proxy_url()
        version = get_version(github_proxy_url)
        if not version:
            return False

        download_url = f"{github_proxy_url}https://github.com/NapNeko/NapCatQQ/releases/download/v{version}/NapCat.Shell.zip"
        _log.info(f"下载链接为 {download_url}...")
        _log.info("正在下载 napcat 客户端, 请稍等...")
        # 下载 napcat 客户端
        try:
            r = requests.get(download_url, stream=True)
            total_size = int(r.headers.get("content-length", 0))
            progress_bar = tqdm(
                total=total_size,
                unit="iB",
                unit_scale=True,
                desc=f"Downloading {NAPCAT_DIR}.zip",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
                colour="green",
                dynamic_ncols=True,
                smoothing=0.3,
                mininterval=0.1,
                maxinterval=1.0,
            )
            with open(f"{NAPCAT_DIR}.zip", "wb") as f:
                for data in r.iter_content(chunk_size=1024):
                    progress_bar.update(len(data))
                    f.write(data)
            progress_bar.close()
        except Exception as e:
            _log.error(
                "下载 napcat 客户端失败, 请检查网络连接或手动下载 napcat 客户端。"
            )
            _log.error("错误信息:", e)
            return
        try:
            with zipfile.ZipFile(f"{NAPCAT_DIR}.zip", "r") as zip_ref:
                zip_ref.extractall(NAPCAT_DIR)
                _log.info("解压 napcat 客户端成功, 请运行 napcat 客户端.")
            os.remove(f"{NAPCAT_DIR}.zip")
        except Exception as e:
            _log.error("解压 napcat 客户端失败, 请检查 napcat 客户端是否正确.")
            _log.error("错误信息: ", e)
            return
        return True
    except Exception as e:
        _log.error("安装失败:", e)
        return False


def download_napcat_linux(type: str):
    """Linux系统下载安装napcat

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
        install_script_url = (
            "https://nclatest.znin.net/NapNeko/NapCat-Installer/main/script/install.sh"
        )
        process = subprocess.Popen(
            f"sudo bash -c 'curl -sSL {install_script_url} | sudo bash'",
            shell=True,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        process.wait()
        _log.info("napcat 客户端安装完成。")
        return True
    except Exception as e:
        _log.error("执行一键安装脚本失败，错误信息:", e)
        exit(1)


def download_napcat(type: str, base_path: str):
    """
    下载和安装 napcat 客户端

    Args:
        type: 安装类型, 可选值为 "install" 或 "update"
        base_path: 安装路径

    Returns:
        bool: 安装成功返回True, 否则返回False
    """
    if platform.system() == "Windows":
        return download_napcat_windows(type, base_path)
    elif platform.system() == "Linux":
        return download_napcat_linux(type)
    return False
