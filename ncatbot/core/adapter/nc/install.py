# 安装 napcat
import json
import os
import platform
import subprocess
import sys


from ....utils import (
    INSTALL_SCRIPT_URL,
    WINDOWS_NAPCAT_DIR,
    ncatbot_config,
    get_log,
    gen_url_with_proxy,
    get_json,
)

from .utils import (
    check_linux_permissions,
    check_self_package_version,
    unzip_file,
    download_file,
    get_napcat_dir,
)

LOG = get_log("ncatbot.core.adapter.nc.install")


def get_napcat_version():
    """从GitHub获取 napcat 版本号"""
    version_url = "https://raw.githubusercontent.com/NapNeko/NapCatQQ/main/package.json"
    version_url = gen_url_with_proxy(version_url)
    LOG.info(f"正在获取版号信息... {version_url}")
    data = get_json(version_url)
    version = data.get("version", None)
    if version:
        LOG.debug(f"获取最新版本信息成功, 版本号: {version}")
        return version
    else:
        LOG.info("获取最新版本信息失败: package.json 中缺少 version 字段")
    return None


def check_windows_qq_version():
    # TODO: 登陆后检查 QQ 版本
    pass


def install_napcat_windows(type: str):
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
            return False
    elif type == "update":
        if input("输入 Y 继续安装或 N 跳过更新: ").strip().lower() not in ["y", "yes"]:
            return False

    try:
        version = get_napcat_version()
        download_url = gen_url_with_proxy(
            f"https://github.com/NapNeko/NapCatQQ/releases/download/v{version}/NapCat.Shell.zip"
        )
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
        LOG.error("安装失败: " + str(e))
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
            f"sudo bash -c 'curl -sS {INSTALL_SCRIPT_URL} -o install && printf \"n\ny\n\" | sudo bash install'",
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
            raise Exception("执行一键安装脚本失败")
    except Exception as e:
        LOG.error("执行一键安装脚本失败，错误信息: " + str(e))
        raise e


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
        raise Exception("请使用 root 权限运行 ncatbot")


def check_ncatbot_installation():
    """检查 ncatbot 版本, 以及是否正确安装"""
    if not ncatbot_config.skip_ncatbot_install_check:
        # 检查版本和安装方式
        version_ok = check_self_package_version()
        if not version_ok:
            raise Exception("请使用 pip 安装 ncatbot")
    else:
        LOG.info("调试模式, 跳过 ncatbot 安装检查")


def is_napcat_installed():
    napcat_dir = get_napcat_dir()
    return os.path.exists(napcat_dir)


def install_or_update_napcat():
    """安装 napcat 或者检查 napcat 更新并重新安装"""
    if not is_napcat_installed():
        if not install_napcat("install"):
            return False
        return True
    elif ncatbot_config.napcat.check_napcat_update:
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
    else:
        return True


def main():
    install_napcat("install")


if __name__ == "__main__":
    main()
