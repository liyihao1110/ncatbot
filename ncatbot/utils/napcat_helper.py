import os
import sys
import subprocess
import platform
import zipfile
import requests
from tqdm import tqdm

from ncatbot.utils.logger import get_log
from ncatbot.utils.literals import NAPCAT_DIR
from ncatbot.utils.github_helper import get_proxy_url, get_version
from ncatbot.scripts.check_linux_permissions import check_linux_permissions

_log = get_log()

def download_napcat(type: str, base_path: str):
    """下载和安装 napcat 客户端"""
    if platform.system() == "Windows":
        return download_napcat_windows(type, base_path)
    elif platform.system() == "Linux":
        return download_napcat_linux()
    return False

def download_napcat_windows(type: str, base_path: str):
    """Windows系统下载安装napcat"""
    _log.info("未找到 napcat ，是否要自动安装？")
    if input("输入 Y 继续安装或 N 退出: ").strip().lower() not in ['y', 'yes']:
        return False
    
    try:
        github_proxy_url = get_proxy_url()
        version = get_version(github_proxy_url)
        if not version:
            return False
            
        download_url = f"{github_proxy_url}https://github.com/NapNeko/NapCatQQ/releases/download/v{version}/NapCat.Shell.zip"
        _log.info(f"下载链接为 {download_url}...")
        _log.info("正在下载 napcat 客户端, 请稍等...")
        
        # 下载和解压逻辑...
        # ...existing download and extract code...
        
        return True
    except Exception as e:
        _log.error("安装失败:", e)
        return False

def download_napcat_linux():
    """Linux系统下载安装napcat"""
    _log.warning("未找到 napcat ，是否要使用一键安装脚本安装？")
    if input("输入 Y 继续安装或 N 退出: ").strip().lower() not in ['y', 'yes']:
        return False
    
    if check_linux_permissions("root") != "root":
        _log.error("请使用 root 权限运行 ncatbot")
        return False
        
    try:
        _log.info("正在下载一键安装脚本...")
        install_script_url = "https://nclatest.znin.net/NapNeko/NapCat-Installer/main/script/install.sh"
        process = subprocess.Popen(
            f"sudo bash -c 'curl -sSL {install_script_url} | sudo bash'",
            shell=True,
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        process.wait()
        _log.info("napcat 客户端安装完成。")
        return True
    except Exception as e:
        _log.error("执行一键安装脚本失败，错误信息:", e)
        return False
