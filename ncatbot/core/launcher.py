import atexit
import os
import platform
import subprocess

from ncatbot.utils.env_checker import check_linux_permissions
from ncatbot.utils.literals import NAPCAT_DIR
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


def start_napcat(config_data, system_type: str = "Windows"):
    """
    启动 napcat 客户端, 启动不了就退出

    Args:
        config_data: 配置数据, 包含QQ号码
        system_type: 操作系统类型, 可选值为 "Windows" 或 "Linux"

    """
    if system_type == "Windows":
        # Windows启动逻辑
        launcher = get_launcher_name()
        napcat_dir = os.path.abspath(NAPCAT_DIR)
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
        napcat_path = "/opt/QQ/resources/app/app_launcher/napcat"
        if not os.path.exists(napcat_path):
            _log.error("未找到 napcat")
            exit(1)

        if check_linux_permissions("root") != "root":
            _log.error("请使用 root 权限运行 ncatbot")
            exit(1)

        try:
            result = subprocess.run(
                ["pgrep", "xvfb"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            if result.stdout.decode().strip() != "":
                _log.info("QQ 已启动")
                atexit.register(lambda: subprocess.run(["pkill", "qq"], check=False))
                return
            else:
                subprocess.Popen(
                    [
                        "xvfb-run",
                        "-a",
                        "qq",
                        "--no-sandbox",
                        "-q",
                        str(config_data.bt_uin),
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                # 添加一个简单的清理函数
                atexit.register(lambda: subprocess.run(["pkill", "xvfb"], check=False))
                atexit.register(lambda: subprocess.run(["pkill", "qq"], check=False))
        except Exception as e:
            # 如果发生异常，则可能pgrep命令没有正确执行
            _log.error(f"pgrep 命令执行失败, 无法判断 QQ 是否启动, 请检查错误: {e}")
            exit(1)

    return
