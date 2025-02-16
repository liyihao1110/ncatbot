import subprocess

from ncatbot.utils.logger import get_log

_log = get_log()


def check_linux_permissions(range: str = "all"):
    """检查Linux的root权限和包管理器

    Args:
        range (str): root, all

    Returns:
        str: root, package_manager, package_installer
    """
    try:
        result = subprocess.run(
            ["sudo", "whoami"],
            check=True,
            text=True,
            capture_output=True,
        )
        if result.stdout.strip() != "root":
            _log.error("当前用户不是root用户, 请使用sudo运行")
            exit(0)
    except subprocess.CalledProcessError as e:
        _log.error(f"sudo 命令执行失败, 请检查错误: {e}")
        exit(0)
    except FileNotFoundError:
        _log.error("sudo 命令不存在, 请检查错误")
        exit(0)
    if range == "root":
        return "root"
    try:
        subprocess.run(
            ["apt-get", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        package_manager = "apt-get"
    except subprocess.CalledProcessError as e:
        _log.error(f"apt-get 命令执行失败, 请检查错误: {e}")
        exit(0)
    except FileNotFoundError:
        try:
            subprocess.run(
                ["dnf", "--version"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            package_manager = "dnf"
        except subprocess.CalledProcessError as e:
            _log.error(f"dnf 命令执行失败, 请检查错误: {e}")
            exit(0)
        except FileNotFoundError:
            _log.error("高级包管理器检查失败, 目前仅支持apt-get/dnf")
            exit(0)
    _log.info(f"当前高级包管理器: {package_manager}")
    try:
        subprocess.run(
            ["dpkg", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        package_installer = "dpkg"
    except subprocess.CalledProcessError as e:
        _log.error(f"dpkg 命令执行失败, 请检查错误: {e}")
        exit(0)
    except FileNotFoundError:
        try:
            subprocess.run(
                ["rpm", "--version"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            package_installer = "rpm"
        except subprocess.CalledProcessError as e:
            _log.error(f"rpm 命令执行失败, 请检查错误: {e}")
            exit(0)
        except FileNotFoundError:
            _log.error("基础包管理器检查失败, 目前仅支持dpkg/rpm")
            exit(0)
    _log.info(f"当前基础包管理器: {package_installer}")
    return package_manager, package_installer
