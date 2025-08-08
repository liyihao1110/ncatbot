# 检查本地 NcatBot 环境
import platform
import os
import site
import subprocess
import sys
import urllib
import urllib.parse
import zipfile
import requests
from tqdm import tqdm
from ncatbot.utils.assets.literals import PYPI_URL, WINDOWS_NAPCAT_DIR, LINUX_NAPCAT_DIR
from ncatbot.utils import get_log

LOG = get_log("ncatbot.core.adapter.nc.utils")


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

def download_file(url, file_name):
    """下载文件, 带进度条"""
    try:
        r = requests.get(url, stream=True)
        total_size = int(r.headers.get("content-length", 0))
        progress_bar = tqdm(
            total=total_size,
            unit="iB",
            unit_scale=True,
            desc=f"Downloading {file_name}",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            colour="green",
            dynamic_ncols=True,
            smoothing=0.3,
            mininterval=0.1,
            maxinterval=1.0,
        )
        with open(file_name, "wb") as f:
            for data in r.iter_content(chunk_size=1024):
                progress_bar.update(len(data))
                f.write(data)
        progress_bar.close()
    except Exception as e:
        LOG.error(f"从 {url} 下载 {file_name} 失败")
        LOG.error("错误信息:", e)
        return

def unzip_file(file_name, exact_path, remove=False):
    try:
        with zipfile.ZipFile(file_name, "r") as zip_ref:
            zip_ref.extractall(exact_path)
            LOG.info(f"解压 {file_name} 成功")
        if remove:
            os.remove(file_name)
    except Exception:
        LOG.error(f"解压 {file_name} 失败")
        return
    

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
            text=True,
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
        url = urllib.parse.urljoin(PYPI_URL, package_name + "/json")
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


def check_self_package_version():
    """
    检查文件所在包的版本.
    """
    package_name = __package__
    result = compare_versions(package_name)
    if result["installed"]:
        if result["update_available"]:
            LOG.warning("NcatBot 有可用更新！")
            LOG.info("若使用 main.exe 或者 NcatBot CLI 启动, CLI 输入 update 即可更新")
            LOG.info(
                "若手动安装, 推荐您使用以下命令更新: pip install --upgrade ncatbot"
            )
        return True
    else:
        if result["error"].startswith("无法获取"):
            LOG.warning("获取 NcatBot 最新版本失败。")
            return True
        LOG.error(f"包 {package_name} 未使用 pip 安装，请使用 pip 安装。")
        return False


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
            LOG.error("当前用户不是root用户, 请使用sudo运行")
            raise Exception("当前用户不是root用户, 请使用sudo运行")
    except subprocess.CalledProcessError as e:
        LOG.error(f"sudo 命令执行失败, 请检查错误: {e}")
        raise e
    except FileNotFoundError as e:
        LOG.error("sudo 命令不存在, 请检查错误")
        raise e
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
        LOG.error(f"apt-get 命令执行失败, 请检查错误: {e}")
        raise e
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
            LOG.error(f"dnf 命令执行失败, 请检查错误: {e}")
            raise e
        except FileNotFoundError as e:
            LOG.error("高级包管理器检查失败, 目前仅支持apt-get/dnf")
            raise e
    LOG.info(f"当前高级包管理器: {package_manager}")
    try:
        subprocess.run(
            ["dpkg", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        package_installer = "dpkg"
    except subprocess.CalledProcessError as e:
        LOG.error(f"dpkg 命令执行失败, 请检查错误: {e}")
        raise e
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
            LOG.error(f"rpm 命令执行失败, 请检查错误: {e}")
            raise e
        except FileNotFoundError as e:
            LOG.error("基础包管理器检查失败, 目前仅支持 dpkg/rpm")
            raise e
    LOG.info(f"当前基础包管理器: {package_installer}")
    return package_manager, package_installer
