# 配置和启动本地 NapCat 服务

import atexit
import json
import os
import platform
import shutil
import subprocess
import time
from urllib.parse import urlparse

from ncatbot.adapter.nc.install import check_permission, get_napcat_dir
from ncatbot.utils import WINDOWS_NAPCAT_DIR, config, get_log

LOG = get_log("adapter.nc.start")


def is_napcat_running_linux():
    process = subprocess.Popen(
        ["bash", "napcat", "status", str(config.bt_uin)], stdout=subprocess.PIPE
    )
    process.wait()
    output = process.stdout.read().decode(encoding="utf-8")
    return output.find(str(config.bt_uin)) != -1


def start_napcat_linux():
    """保证 NapCat 已经安装的前提下, 启动 NapCat 服务"""
    # Linux启动逻辑
    try:
        # 启动并注册清理函数
        process = subprocess.Popen(
            ["sudo", "bash", "napcat", "start", str(config.bt_uin)],
            stdout=subprocess.PIPE,
        )
        process.wait()
        if process.returncode != 0:
            LOG.error("启动 napcat 失败，请检查日志，ncatbot cli 可能没有被正确安装")
        if config.stop_napcat:
            atexit.register(lambda: stop_napcat_linux(config.bt_uin))
    except Exception as e:
        LOG.error(f"pgrep 命令执行失败, 无法判断 QQ 是否启动, 请检查错误: {e}")
        exit(1)

    if not is_napcat_running_linux():
        LOG.error("napcat 启动失败，请检查日志")
        exit(1)
    else:
        time.sleep(0.5)
        LOG.info("napcat 启动成功")


def stop_napcat_linux():
    process = subprocess.Popen(["bash", "napcat", "stop"], stdout=subprocess.PIPE)
    process.wait()


def is_napcat_running_windows():
    """暂未实现逻辑"""
    return True


def start_napcat_windows():
    # Windows启动逻辑
    def get_launcher_name():
        """获取对应系统的launcher名称"""
        is_server = "Server" in platform.release()
        if is_server:
            version = platform.release()
            if "2016" in version:
                LOG.info("当前操作系统为: Windows Server 2016")
                return "launcher-win10.bat"
            elif "2019" in version:
                LOG.info("当前操作系统为: Windows Server 2019")
                return "launcher-win10.bat"
            elif "2022" in version:
                LOG.info("当前操作系统为: Windows Server 2022")
                return "launcher-win10.bat"
            elif "2025" in version:
                LOG.info("当前操作系统为：Windows Server 2025")
                return "launcher.bat"
            else:
                LOG.error(
                    f"不支持的的 Windows Server 版本: {version}，将按照 Windows 10 内核启动"
                )
                return "launcher-win10.bat"

        if platform.release() == "10":
            LOG.info("当前操作系统为: Windows 10")
            return "launcher-win10.bat"

        if platform.release() == "11":
            LOG.info("当前操作系统为: Windows 11")
            return "launcher.bat"

        return "launcher-win10.bat"

    launcher = get_launcher_name()
    napcat_dir = os.path.abspath(WINDOWS_NAPCAT_DIR)
    launcher_path = os.path.join(napcat_dir, launcher)

    if not os.path.exists(launcher_path):
        LOG.error(f"找不到启动文件: {launcher_path}")
        exit(1)

    LOG.info(f"正在启动QQ, 启动器路径: {launcher_path}")
    subprocess.Popen(
        f'"{launcher_path}" {config.bt_uin}',
        shell=True,
        cwd=napcat_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def stop_napcat_windows():
    """暂未实现"""
    pass


def is_napcat_running():
    if platform.system() == "Linux":
        return is_napcat_running_linux()
    elif platform.system() == "Windows":
        return is_napcat_running_windows()
    else:
        LOG.warning("不提供官方支持的系统, 默认 NapCat 正在运行")
        return True


def stop_napcat():
    """本地停止 NapCat 服务"""
    LOG.info("正在停止 NapCat 服务")
    if platform.system() == "Linux":
        stop_napcat_linux()
    elif platform.system() == "Windows":
        stop_napcat_windows()
    else:
        LOG.warning("不提供官方支持的系统, 默认 NapCat 未启动")


def start_napcat():
    """本地配置并启动 NapCat 服务"""
    config_napcat()
    if platform.system() == "Linux":
        start_napcat_linux()
    elif platform.system() == "Windows":
        start_napcat_windows()
    else:
        LOG.warning("不提供官方支持的系统, 默认 NapCat 已启动")


def config_napcat():
    """配置 napcat 服务器, 保证 napcat_dir 存在且被正确配置"""
    napcat_dir = get_napcat_dir()

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
                            str(config.ws_token) if config.ws_token is not None else ""
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
            LOG.error("配置 onebot 失败: " + str(e))
            if not check_permission():
                LOG.info("请使用 root 权限运行 ncatbot")
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
            LOG.info("Token: " + token + ", Webui port: " + str(port))

        except FileNotFoundError:
            LOG.error("无法读取 WebUI 配置, 将使用默认配置")

    config_onebot11()
    config_quick_login()
    read_webui_config()
