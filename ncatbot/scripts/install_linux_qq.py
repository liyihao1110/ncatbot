import json
import os
import platform
import subprocess

import requests
from tqdm import tqdm
from ncatbot.utils.literals import NAPCAT_DIR
from ncatbot.utils.logger import get_log
from ncatbot.scripts.check_qq_version import check_qq_version

_log = get_log()


def install(package_installer: str, filename: str):
    """安装Linux QQ
    Args:
        package_installer (str): 包安装器
        filename (str): 文件名
    """
    if package_installer == "dpkg":
        try:
            subprocess.run(
                ["sudo", "apt-get", "install", "-f", "-y", "-qq", f"./{filename}"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError as e:
            _log.error(f"Linux QQ 安装失败, 请检查错误: {e}")
            exit(0)
        try:
            subprocess.run(
                [
                    "sudo",
                    "apt-get",
                    "install",
                    "-y",
                    "-qq",
                    "libnss3",
                    "libgbm1",
                    "libasound2",
                    "libasound2t64",
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError as e:
            _log.error(f"Linux QQ 安装依赖失败, 请检查错误: {e}")
            exit(0)
    elif package_installer == "rpm":
        try:
            subprocess.run(
                ["sudo", "dnf", "localinstall", "-y", f"./{filename}"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError as e:
            _log.error(f"Linux QQ 安装失败, 请检查错误: {e}")
            exit(0)


def arch_to_url(url: str, arch: str, package_installer: str):
    """将架构转换为下载链接
    Args:
        url (str): 下载链接
        arch (str): 架构
        package_installer (str): 包安装器
    Returns:
        str: 下载链接
    """
    if arch == "amd64":
        if package_installer == "dpkg":
            return f"{url}_amd64.deb"
        elif package_installer == "rpm":
            return f"{url}_x86_64.rpm"
    elif arch == "arm64":
        if package_installer == "dpkg":
            return f"{url}_arm64.deb"
        elif package_installer == "rpm":
            return f"{url}_aarch64.rpm"


def download_linuxqq(url: str):
    """下载 linuxqq 客户端
    Args:
        url (str): 下载链接
    """
    try:
        _log.info(f"下载链接为 {url}...")
        _log.info("正在下载 linuxqq 客户端, 请稍等...")
        r = requests.get(url, stream=True)
        filename = url.split("/")[-1]
        total_size = int(r.headers.get("content-length", 0))
        progress_bar = tqdm(
            total=total_size,
            unit="iB",
            unit_scale=True,
            desc=f"Downloading linuxqq",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            colour="green",
            dynamic_ncols=True,
            smoothing=0.3,
            mininterval=0.1,
            maxinterval=1.0,
        )

        # 保存文件
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    size = f.write(chunk)
                    progress_bar.update(size)

        progress_bar.close()
        return filename
    except Exception as e:
        _log.error("下载 linuxqq 客户端失败, 请检查网络连接或手动安装 linuxqq 客户端。")
        _log.error("错误信息:", e)
        exit(0)


def compare_versions(current_version: str, target_version: str) -> bool:
    """比较两个版本号

    Args:
        current_version (str): 当前版本号
        target_version (str): 目标版本号

    Returns:
        bool: 如果当前版本号小于目标版本号, 返回 True, 否则返回 False
    """
    # 将版本号字符串分割成列表
    main_parts1, build_part1 = current_version.split("-")
    version_parts1 = list(map(int, main_parts1.split(".")))
    main_parts2, build_part2 = target_version.split("-")
    version_parts2 = list(map(int, main_parts2.split(".")))

    # 逐个比较版本号的各个部分
    for i in range(max(len(version_parts1), len(version_parts2))):
        if i >= len(version_parts2):
            return False
        if i >= len(version_parts1):
            return True
        if version_parts1[i] < version_parts2[i]:
            return True
        elif version_parts1[i] > version_parts2[i]:
            return False
    return int(build_part1) < int(build_part2)


def install_linux_qq(package_manager: str, package_installer: str, type: str):
    """安装Linux QQ
    Args:
        package_manager (str): 包管理器
        package_installer (str): 包安装器
        type (str): install/update
        
    Returns:
        None
    """
    arch = platform.machine()
    if arch == "x86_64":
        system_arch = "amd64"
    elif arch == "aarch64":
        system_arch = "arm64"
    else:
        _log.error("无法识别的系统架构, 请检查错误")
        exit(0)
    if type == "install":
        if package_manager == "apt-get":
            # 更新包列表
            try:
                subprocess.run(
                    ["sudo", "apt-get", "update", "-y", "-qq"],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except subprocess.CalledProcessError as e:
                _log.error(f"apt-get 更新包列表失败, 请检查错误: {e}")
                exit(0)
            # 安装基础依赖
            try:
                subprocess.run(
                    [
                        "sudo",
                        "apt-get",
                        "install",
                        "-y",
                        "-qq",
                        "xvfb",
                        "screen",
                        "xauth",
                        "procps",
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except subprocess.CalledProcessError as e:
                _log.error(f"apt-get 安装基础依赖失败, 请检查错误: {e}")
                exit(0)
            _log.info("安装依赖成功")
        elif package_manager == "dnf":
            # 安装 epel-release
            try:
                subprocess.run(
                    ["sudo", "dnf", "install", "-y", "epel-release"],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except subprocess.CalledProcessError as e:
                _log.error(f"dnf 安装 epel-release 失败, 请检查错误: {e}")
                exit(0)
            # 安装基础依赖
            try:
                subprocess.run(
                    [
                        "sudo",
                        "dnf",
                        "install",
                        "--allowerasing",
                        "-y",
                        "xorg-x11-server-Xvfb",
                        "screen",
                        "procps-ng",
                    ],
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                _log.error(f"dnf 安装基础依赖失败, 请检查错误: {e}")
                exit(0)
        _log.info("安装依赖成功")
    linuxqq_installed_version = check_qq_version(package_installer)
    with open(os.path.join(NAPCAT_DIR, "qqnt.json"), "r") as f:
        data = json.load(f)
    linux_version = data["linuxVersion"]
    linux_ver_hash = data["linuxVerHash"]
    if linuxqq_installed_version:
        if compare_versions(linuxqq_installed_version, linux_version):
            _log.info(
                f"Linux QQ 版本为 {linuxqq_installed_version}, 需要版本为 {linux_version}, 无需更新"
            )
        else:
            # 更新 linuxqq 客户端
            _log.info(
                f"Linux QQ 版本为 {linuxqq_installed_version}, 需要版本为 {linux_version}, 需要更新"
            )
            base_url = f"https://dldir1.qq.com/qqfile/qq/QQNT/{linux_ver_hash}/linuxqq_{linux_version}"
            download_url = arch_to_url(base_url, system_arch, package_installer)
            # 下载 linuxqq 客户端
            filename = download_linuxqq(download_url)
            install(package_installer, filename)
            try:
                os.remove(filename)
            except Exception as e:
                _log.error(f"删除 Linux QQ 安装包失败, 请检查错误: {e}")
            _log.info(f"Linux QQ {linux_version} 安装成功")
            return None

    else:
        _log.info("开始安装Linux QQ 3.2.15-31363")
        base_url = f"https://dldir1.qq.com/qqfile/qq/QQNT/a5519e17/linuxqq_3.2.15-31363"
        download_url = arch_to_url(base_url, system_arch, package_installer)
        # 下载 linuxqq 客户端
        filename = download_linuxqq(download_url)
        install(package_installer, filename)
        try:
            os.remove(filename)
        except Exception as e:
            _log.error(f"删除 Linux QQ 安装包失败, 请检查错误: {e}")
        _log.info(f"Linux QQ 3.2.15-31363 安装成功")
        return None
