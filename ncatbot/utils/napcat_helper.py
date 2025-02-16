import os
import platform
import subprocess
import sys
import zipfile

import requests
from tqdm import tqdm

from ncatbot.scripts.check_linux_permissions import check_linux_permissions
from ncatbot.utils.github_helper import get_proxy_url, get_version
from ncatbot.utils.literals import NAPCAT_DIR
from ncatbot.utils.logger import get_log

_log = get_log()


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
