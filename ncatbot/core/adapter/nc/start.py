import atexit
import os
import platform
import subprocess
import time
import traceback

from ncatbot.utils import WINDOWS_NAPCAT_DIR, ncatbot_config, get_log

LOG = get_log("adapter.nc.start")


def is_napcat_running_linux(target=None):
    process = subprocess.Popen(["bash", "napcat", "status"], stdout=subprocess.PIPE)
    process.wait()
    output = process.stdout.read().decode(encoding="utf-8")
    if target is None:
        return output.find("PID") != -1
    else:
        return output.find(str(target)) != -1


def start_napcat_linux():
    """保证 NapCat 已经安装的前提下, 启动 NapCat 服务"""
    # Linux启动逻辑
    if not is_napcat_running_linux(ncatbot_config.bt_uin):
        if is_napcat_running_linux():
            LOG.warning("NapCat 正在运行, 但运行的不是该 QQ 号")
            rs = input("按 y 强制结束当前 NapCat 进程并继续, 按其他键退出")
            if rs == "y":
                stop_napcat_linux()
            else:
                raise Exception("NapCat 正在运行, 但运行的不是该 QQ 号")
    else:
        LOG.info("NapCat 已启动")
        return
    try:
        # 启动并注册清理函数
        LOG.info("正在启动 NapCat 服务")
        if os.path.exists("napcat"):
            LOG.error(
                "工作目录下存在 napcat 目录, Linux 启动时不应该在工作目录下存在 napcat 目录"
            )
            raise FileExistsError("工作目录下存在 napcat 目录")
        process = subprocess.Popen(
            ["sudo", "bash", "napcat", "start", str(ncatbot_config.bt_uin)],
            stdout=subprocess.PIPE,
        )
        process.wait()
        if process.returncode != 0:
            LOG.error("启动 napcat 失败，请检查日志，napcat cli 可能没有被正确安装")
            raise FileNotFoundError("napcat cli 可能没有被正确安装")
        if ncatbot_config.napcat.stop_napcat:
            atexit.register(lambda: stop_napcat_linux(ncatbot_config.bt_uin))
    except Exception as e:
        import traceback

        LOG.error(f"pgrep 命令执行失败, 无法判断 QQ 是否启动, 请检查错误: {e}")
        LOG.info(traceback.format_exc())
        raise e

    if not is_napcat_running_linux(ncatbot_config.bt_uin):
        LOG.error("napcat 启动失败，请检查日志")
        raise Exception("napcat 启动失败")
    else:
        time.sleep(0.5)
        LOG.info("napcat 启动成功")


def stop_napcat_linux():
    try:
        process = subprocess.Popen(["bash", "napcat", "stop"], stdout=subprocess.PIPE)
        process.wait()
        if process.returncode != 0:
            LOG.error("停止 napcat 失败，请检查日志")
            raise Exception("停止 napcat 失败")
        else:
            LOG.info("已成功停止 napcat")
    except Exception as e:
        LOG.error(f"停止 napcat 失败，请检查日志: {e}")
        LOG.info(traceback.format_exc())
        raise e


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
        raise FileNotFoundError(f"找不到启动文件: {launcher_path}")

    LOG.info(f"正在启动QQ, 启动器路径: {launcher_path}")
    subprocess.Popen(
        f'"{launcher_path}" {ncatbot_config.bt_uin}',
        shell=True,
        cwd=napcat_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def stop_napcat_windows():
    """停止 NapCat 服务: 在 Windows 上强制结束 QQ.exe 进程"""
    try:
        # 使用 taskkill 强制结束 QQ.exe 进程
        subprocess.run(
            ["taskkill", "/F", "/IM", "QQ.exe"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        LOG.info("已成功停止 QQ.exe 进程（NapCat 服务）")
    except subprocess.CalledProcessError as e:
        # 如果 taskkill 命令执行失败，记录错误并抛出异常
        stdout = e.stdout.decode(errors="ignore") if e.stdout else ""
        stderr = e.stderr.decode(errors="ignore") if e.stderr else ""
        LOG.error(f"停止 NapCat 服务失败: {stderr or stdout}")
        raise RuntimeError(f"无法停止 QQ.exe 进程: {stderr or stdout}")


def is_napcat_running():
    if platform.system() == "Linux":
        return is_napcat_running_linux()
    elif platform.system() == "Windows":
        return is_napcat_running_windows()
    else:
        raise RuntimeError("不支持的操作系统")


def stop_napcat():
    """本地停止 NapCat 服务"""
    LOG.info("正在停止 NapCat 服务")
    if platform.system() == "Linux":
        stop_napcat_linux()
    elif platform.system() == "Windows":
        stop_napcat_windows()
    else:
        raise RuntimeError("不支持的操作系统")

def start_napcat():
    """本地启动 NapCat 服务"""
    if platform.system() == "Linux":
        start_napcat_linux()
    elif platform.system() == "Windows":
        start_napcat_windows()
    else:
        raise RuntimeError("不支持的操作系统")