import asyncio
import platform
import time

from ncatbot.adapter.nc.install import install_or_update_napcat
from ncatbot.adapter.nc.login import BotUINError, login, online_qq_is_bot
from ncatbot.adapter.nc.start import start_napcat, stop_napcat
from ncatbot.adapter.net import check_websocket
from ncatbot.utils import config, get_log

LOG = get_log("adapter.nc.launcher")


def napcat_service_ok():
    return asyncio.run(check_websocket(config.ws_uri))


def connect_napcat():
    """启动并尝试连接 napcat 直到成功"""

    def info_windows():
        LOG.info("===请允许终端修改计算机, 并在弹出的另一个终端扫码登录===")
        LOG.info(f"===确认 bot QQ 号 {config.bt_uin} 是否正确===")

    def info(quit=False):
        LOG.info("连接 napcat websocket 服务器超时, 请检查以下内容:")
        if platform.system() == "Windows":
            info_windows()
        elif platform.system() == "Linux":
            pass
        else:
            pass
        LOG.info(f"===websocket url 是否正确: {config.ws_uri}===")
        if quit:
            raise Exception("连接超时")

    MAX_TIME_EXPIRE = time.time() + 60
    # INFO_TIME_EXPIRE = time.time() + 20
    LOG.info("正在连接 napcat websocket 服务器...")
    while not napcat_service_ok():
        time.sleep(0.05)
        if time.time() > MAX_TIME_EXPIRE:
            info(True)

    LOG.info("连接 napcat websocket 服务器成功!")


def ncatbot_service_remote_start():
    """尝试以远程模式连接到 NapCat 服务"""
    if napcat_service_ok():
        LOG.info(f"napcat 服务器 {config.ws_uri} 在线, 连接中...")
        if not config.enable_webui_interaction:  # 跳过基于 WebUI 交互的检查
            LOG.warning(
                f"跳过基于 WebUI 交互的检查, 请自行确保 NapCat 已经登录了正确的 QQ {config.bt_uin}"
            )
            return True
        if not online_qq_is_bot():
            if not config.remote_mode:
                # 如果账号不对并且是本地模式, 则停止 NapCat 服务后重新启动
                stop_napcat()
                return False
            else:
                LOG.error(
                    "远端的 NapCat 服务 QQ 账号信息与本地 bot_uin 不匹配, 请检查远端 NapCat 配置"
                )
                raise Exception("账号错误")
        return True
    elif config.remote_mode:
        LOG.error("远程模式已经启用, 无法到连接远程 NapCat 服务器, 将自动退出")
        LOG.error(f'服务器参数: uri="{config.ws_uri}", token="{config.ws_token}"')
        LOG.info(
            """可能的错误原因:
                    1. napcat webui 中服务器类型错误, 应该为 "WebSocket 服务器", 而非 "WebSocket 客户端"
                    2. napcat webui 中服务器配置了但没有启用, 请确保勾选了启用服务器"
                    3. napcat webui 中服务器 host 没有设置为监听全部地址, 应该将 host 改为 0.0.0.0
                    4. 检查以上配置后, 在本机尝试连接远程的 webui ,使用 error 信息中的的服务器参数, \"接口调试\"选择\"WebSocket\"尝试连接.
                    5. webui 中连接成功后再尝试启动 ncatbot
                    """
        )
        raise Exception("服务器离线")

    LOG.info("NapCat 服务器离线, 启动本地 NapCat 服务中...")
    return False


def launch_napcat_service(*args, **kwargs):
    """
    启动配置中 QQ 对应的 NapCat 服务, 保证 WebSocket 接口可用, 包括以下任务:

    1. 安装或者更新 NapCat
    2. 配置 NapCat
    3. 启动 NapCat 服务
    4. NapCat 登录 QQ
    5. 连接 NapCat 服务
    """
    if ncatbot_service_remote_start():
        return True

    install_or_update_napcat()
    start_napcat()  # 配置、启动 NapCat 服务
    try:
        if config.enable_webui_interaction:  # 如果允许 webui 交互, 则做登录引导
            login(reset=True)  # NapCat 登录 QQ
    except BotUINError:  # 我也不知道, 后面可能会把这玩意删了
        LOG.error("我觉得这个错误不该有, 如果遇到了请联系开发者")
        return False
        # stop_napcat()
        # launch_napcat_service(*args, **kwargs)
    connect_napcat()  # 连接 NapCat 服务
    return True
