# 安装 napcat

import time

from ncatbot.utils.logger import get_log

_log = get_log()


import platform
import subprocess
import sys

import requests

from ncatbot.utils.assets.literals import (
    INSTALL_SCRIPT_URL,
    WINDOWS_NAPCAT_DIR,
)
from ncatbot.utils.env_checker import check_linux_permissions
from ncatbot.utils.file_io import download_file, unzip_file
from ncatbot.utils.logger import get_log

_log = get_log()


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


def check_permission():
    if check_linux_permissions("root") != "root":
        _log.error("请使用 root 权限运行 ncatbot")
        exit(1)


def check_ncatbot_install():
    """检查 ncatbot 版本, 以及是否正确安装"""
    if not debug:
        # 检查版本和安装方式
        version_ok = check_version()
        if not version_ok:
            exit(0)
    else:
        _log.info("调试模式, 跳过 ncatbot 安装检查")


def ncatbot_quick_start():
    """在能够链接上 napcat 服务器时跳过检查直接启动"""
    if self.napcat_server_ok():
        _log.info(f"napcat 服务器 {config.ws_uri} 在线, 连接中...")
        LoginHandler().login()
        self._run()
    elif not config._is_localhost():
        _log.error("napcat 服务器没有配置在本地, 无法连接服务器, 自动退出")
        _log.error(f'服务器参数: uri="{config.ws_uri}", token="{config.token}"')
        _log.info(
            """可能的错误原因:
                    1. napcat webui 中服务器类型错误, 应该为 "WebSocket 服务器", 而非 "WebSocket 客户端"
                    2. napcat webui 中服务器配置了但没有启用, 请确保勾选了启用服务器"
                    3. napcat webui 中服务器 host 没有设置为监听全部地址, 应该将 host 改为 0.0.0.0
                    4. 检查以上配置后, 在 webui 中使用 error 信息中的的服务器参数, \"接口调试\"选择\"WebSocket\"尝试连接.
                    5. webui 中连接成功后再尝试启动 ncatbot
                    """
        )
        exit(1)
    elif kwargs.get("reload", False):
        _log.info("napcat 服务器未启动, 且开启了重加载模式, 运行失败")
        exit(1)
    _log.info("napcat 服务器离线")


def check_install_napcat():
    """检查是否已经安装 napcat 客户端, 如果没有, 安装 napcat"""
    if not os.path.exists(napcat_dir):
        if not download_napcat("install"):
            exit(1)
    else:
        # 检查 napcat 版本更新
        with open(os.path.join(napcat_dir, "package.json"), "r", encoding="utf-8") as f:
            version = json.load(f)["version"]
            _log.info(f"当前 napcat 版本: {version}, 正在检查更新...")

        github_version = get_version()
        if version != github_version:
            _log.info(f"发现新版本: {github_version}, 是否要更新 napcat 客户端？")
            if not download_napcat("update"):
                _log.info(f"跳过 napcat {version} 更新")
        else:
            _log.info("当前 napcat 已是最新版本")


def config_napcat():
    """配置 napcat 服务器"""

    def config_onebot11():
        expected_data = {
            "network": {
                "websocketServers": [
                    {
                        "name": "WsServer",
                        "enable": True,
                        "host": str(urlparse(config.ws_uri).hostname),
                        "port": int(urlparse(config.ws_uri).port),
                        "messagePostFormat": "array",
                        "reportSelfMessage": False,
                        "token": (
                            str(config.token) if config.token is not None else ""
                        ),
                        "enableForcePushEvent": True,
                        "debug": False,
                        "heartInterval": 30000,
                    }
                ],
            },
            "musicSignUrl": "",
            "enableLocalFile2Url": False,
            "parseMultMsg": False,
        }
        try:
            with open(
                os.path.join(
                    napcat_dir,
                    "config",
                    "onebot11_" + str(config.bt_uin) + ".json",
                ),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(expected_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            _log.error("配置 onebot 失败: " + str(e))
            if not check_permission():
                _log.info("请使用 root 权限运行 ncatbot")
                exit(1)

    def config_quick_login():
        ori = os.path.join(napcat_dir, "quickLoginExample.bat")
        dst = os.path.join(napcat_dir, f"{config.bt_uin}_quickLogin.bat")
        shutil.copy(ori, dst)

    def read_webui_config():
        # 确定 webui 路径
        webui_config_path = os.path.join(napcat_dir, "config", "webui.json")
        try:
            with open(webui_config_path, "r") as f:
                webui_config = json.load(f)
                port = webui_config.get("port", 6099)
                token = webui_config.get("token", "")
                config.webui_token = token
                config.webui_port = port
            _log.info("Token: " + token + ", Webui port: " + str(port))

        except FileNotFoundError:
            _log.error("无法读取 WebUI 配置, 将使用默认配置")

    config_onebot11()
    config_quick_login()
    read_webui_config()


def connect_napcat():
    """启动并尝试连接 napcat 直到成功"""

    def info_windows():
        _log.info("1. 请允许终端修改计算机, 并在弹出的另一个终端扫码登录")
        _log.info(f"2. 确认 QQ 号 {config.bt_uin} 是否正确")
        _log.info(f"3. websocket url 是否正确: {config.ws_uri}")

    def info_linux():
        _log.info(f"1. websocket url 是否正确: {config.ws_uri}")

    def info(quit=False):
        _log.info("连接 napcat websocket 服务器超时, 请检查以下内容:")
        if platform.system() == "Windows":
            info_windows()
        else:
            info_linux()
        if quit:
            exit(1)

    start_napcat(config, platform.system())  # 启动 napcat
    if platform.system() == "Linux":
        LoginHandler().login()

    MAX_TIME_EXPIRE = time.time() + 60
    INFO_TIME_EXPIRE = time.time() + 20
    _log.info("正在连接 napcat websocket 服务器...")
    while not self.napcat_server_ok():
        time.sleep(0.5)
        if time.time() > MAX_TIME_EXPIRE:
            info(True)
        if time.time() > INFO_TIME_EXPIRE:
            info()
            INFO_TIME_EXPIRE += 100

    _log.info("连接 napcat websocket 服务器成功!")
