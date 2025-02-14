import subprocess

from ncatbot.utils.logger import get_log

_log = get_log()

def check_qq_version(package_installer: str):
    """检查 linuxqq 客户端版本
    Args:
        package_installer (str): 包管理器
    Returns:
        str: 版本号
    """
    if package_installer == "dpkg":
        try:
            linuxqq_installed_version = subprocess.check_output(
                "dpkg -l | grep '^ii' | grep 'linuxqq' | awk '{print $3}'",
                shell=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            _log.info(f"请检查 dpkg 错误: {e}")
        if linuxqq_installed_version:
            _log.info("Linux QQ 已安装")
            return linuxqq_installed_version
        else:
            _log.info("Linux QQ 未安装")
    elif package_installer == "rpm":
        try:
            linuxqq_installed_version = subprocess.check_output(
                "rpm -q --queryformat '%{VERSION}' linuxqq",
                shell=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            _log.info(f"请检查 rpm 错误: {e}")
        if linuxqq_installed_version:
            _log.info("Linux QQ 已安装")
            return linuxqq_installed_version
        else:
            _log.info("Linux QQ 未安装")
