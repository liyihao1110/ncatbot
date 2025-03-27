import atexit
import os
import platform
import subprocess
import time

from ncatbot.utils.config import config
from ncatbot.utils.literals import LINUX_NAPCAT_DIR, WINDOWS_NAPCAT_DIR
from ncatbot.utils.logger import get_log

_log = get_log()


def get_launcher_name():
    """获取对应系统的launcher名称"""
    is_server = "Server" in platform.release()
    if is_server:
        version = platform.release()
        if "2016" in version:
            _log.info("当前操作系统为: Windows Server 2016")
            return "launcher-win10.bat"
        elif "2019" in version:
            _log.info("当前操作系统为: Windows Server 2019")
            return "launcher-win10.bat"
        elif "2022" in version:
            _log.info("当前操作系统为: Windows Server 2022")
            return "launcher-win10.bat"
        elif "2025" in version:
            _log.info("当前操作系统为：Windows Server 2025")
            return "launcher.bat"
        else:
            _log.error(
                f"不支持的的 Windows Server 版本: {version}，将按照 Windows 10 内核启动"
            )
            return "launcher-win10.bat"

    if platform.release() == "10":
        _log.info("当前操作系统为: Windows 10")
        return "launcher-win10.bat"

    if platform.release() == "11":
        _log.info("当前操作系统为: Windows 11")
        return "launcher.bat"

    return "launcher-win10.bat"


def check_napcat_statu_linux(qq):
    process = subprocess.Popen(
        ["bash", "napcat", "status", str(qq)], stdout=subprocess.PIPE
    )
    process.wait()
    output = process.stdout.read().decode(encoding="utf-8")
    return output.find(str(qq)) != -1


def start_napcat_linux(qq):
    process = subprocess.Popen(
        ["sudo", "bash", "napcat", "start", str(qq)], stdout=subprocess.PIPE
    )
    process.wait()
    if process.returncode != 0:
        _log.error("启动 napcat 失败，请检查日志，ncatbot cli 可能没有被正确安装")


def stop_napcat_linux(qq):
    process = subprocess.Popen(
        ["bash", "napcat", "stop", str(qq)], stdout=subprocess.PIPE
    )
    process.wait()


def start_napcat(config_data, system_type: str = "Windows"):
    """
    启动 napcat 客户端, 启动不了就退出

    Args:
        config_data: 配置数据, 包含QQ号码
        system_type: 操作系统类型, 可选值为 "Windows" 或 "Linux"

    """
    _log.info("正在启动 napcat 服务器")
    if system_type == "Windows":
        # Windows启动逻辑
        launcher = get_launcher_name()
        napcat_dir = os.path.abspath(WINDOWS_NAPCAT_DIR)
        launcher_path = os.path.join(napcat_dir, launcher)

        if not os.path.exists(launcher_path):
            _log.error(f"找不到启动文件: {launcher_path}")
            exit(1)

        _log.info(f"正在启动QQ，启动器路径: {launcher_path}")
        subprocess.Popen(
            f'"{launcher_path}" {config_data.bt_uin}',
            shell=True,
            cwd=napcat_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        # Linux启动逻辑
        napcat_path = LINUX_NAPCAT_DIR
        if not os.path.exists(napcat_path):
            _log.error("未找到 napcat")
            exit(1)

        try:
            # 启动并注册清理函数
            start_napcat_linux(config_data.bt_uin)
            if config.stop_napcat:
                atexit.register(lambda: stop_napcat_linux(config_data.bt_uin))
        except Exception as e:
            _log.error(f"pgrep 命令执行失败, 无法判断 QQ 是否启动, 请检查错误: {e}")
            exit(1)

        if not check_napcat_statu_linux(config_data.bt_uin):
            _log.error("napcat 启动失败，请检查日志")
            exit(1)
        else:
            time.sleep(0.5)
            _log.info("napcat 启动成功")
    return
