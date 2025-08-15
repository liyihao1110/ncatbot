"""测试内容
Windows:
 - 纯裸机安装启动(扫码登录)
 - NapCat 安装但未运行启动(快速登录, 需要手机确认)
Linux:
 - 纯裸机安装启动(扫码登录)
 - NapCat 安装但未运行启动(快速登录)
跨平台:
 - 远端模式启动(插件无数据)
 - NapCat 安装且运行启动(插件有数据)
"""

import asyncio
import platform
import time
import json
import websockets

from ncatbot.core.adapter.nc.install import install_or_update_napcat
from ncatbot.core.adapter.nc.login import login, report_login_status
from ncatbot.core.adapter.nc.config import config_napcat
from ncatbot.core.adapter.nc.start import start_napcat, stop_napcat
from ncatbot.utils import ncatbot_config, get_log
from ncatbot.utils.error import NcatBotError

LOG = get_log("ncatbot.core.adapter.nc.launch")

class NcatBotLoginError(NcatBotError):
    def __init__(self, info):
        super().__init__(info, False)


async def test_websocket() -> bool:
    uri_with_token = ncatbot_config.napcat.ws_uri + "/?access_token=" + ncatbot_config.napcat.ws_token
    try:
        async with websockets.connect(uri_with_token, open_timeout=3) as ws:
            data = json.loads(await ws.recv())
            if data.get("status", "ok") == "ok":
                return True
            else:
                raise NcatBotError("WebSocket Token 填写错误", False)
    except NcatBotError:
        raise
    except Exception as e:
        return False    


def napcat_service_ok(EXPIRE=0):
    if EXPIRE == 0:
        return asyncio.run(test_websocket())
    else:
        MAX_TIME_EXPIRE = time.time() + EXPIRE
        while not napcat_service_ok():
            if time.time() > MAX_TIME_EXPIRE:
                return False
            time.sleep(0.5)
        return True


def connect_napcat():
    """启动并尝试连接 napcat 直到成功"""
    if not napcat_service_ok(60):
        raise NcatBotError("连接 napcat websocket 服务器超时")
    LOG.info("连接 napcat websocket 服务器成功!")


def check_napcat_service_remote():
    """尝试以远程模式连接到 NapCat 服务"""
    if napcat_service_ok():
        LOG.info(f"napcat 服务器 {ncatbot_config.napcat.ws_uri} 在线, 正在检查账号状态...")
        if not ncatbot_config.enable_webui_interaction:  # 跳过基于 WebUI 交互的检查
            LOG.warning(
                f"跳过基于 WebUI 交互的检查, 请自行确保 NapCat 已经登录了正确的 QQ {ncatbot_config.bt_uin}"
            )
            return True
        status = report_login_status()
        if status == 0:
            return True
        else:
            if status == 3:
                LOG.error("登录状态异常, 请检查远端 NapCat 服务")
                LOG.error("对运行 NapCat 的服务器进行物理重启一般能解决该问题")
                raise NcatBotLoginError("登录状态异常, 请检查远端 NapCat 服务")
            if status == 2:
                LOG.error(
                    f"远端登录的 QQ 与配置的 QQ 号不匹配, 请检查远端 NapCat 服务"
                )
                raise NcatBotLoginError(
                    "登录的 QQ 号与配置的 QQ 号不匹配, 请检查远端 NapCat 服务"
                )

    LOG.info("NapCat 服务器离线或未登录")
    return False


def lanuch_napcat_service(*args, **kwargs):
    if ncatbot_config.napcat.remote_mode:
        LOG.info("正在以远端模式运行, 检查中...")
        if check_napcat_service_remote():
            pass
        else:
            raise NcatBotError("远端 NapCat 服务异常, 请检查远端 NapCat 服务, 或者关闭远端模式")
    else:
        LOG.info("正在以本地模式运行, 检查中...")
        if napcat_service_ok():
            if check_napcat_service_remote():
                LOG.debug("远端 NapCat 服务正常")
        else:
            if platform.system() not in ["Windows", "Linux"]:
                raise NcatBotError("本地模式不支持该操作系统, 请使用远端模式")
            else:
                if not install_or_update_napcat():
                    raise NcatBotError("安装或更新 NapCat 失败")
                config_napcat()
                start_napcat()
                if ncatbot_config.enable_webui_interaction:
                    if not napcat_service_ok(3):
                        LOG.info("登录中...")
                        login(reset=True)
                        connect_napcat()
                        LOG.info("连接成功")
                    else:
                        LOG.info("快速登录成功, 跳过登录引导")
                else:
                    if not napcat_service_ok(15):
                        raise NcatBotError("禁用 WebUI 交互时, 必须手动登录")
                    else:
                        pass

if __name__ == "__main__":
    print(asyncio.run(test_websocket()))