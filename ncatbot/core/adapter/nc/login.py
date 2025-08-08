import hashlib
import platform
import time
import traceback

import qrcode
import requests
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError

# from PIL import Image
# import qreader
from ncatbot.utils import NAPCAT_WEBUI_SALT, ncatbot_config, get_log


class QQLoginedError(Exception):
    def __init__(self):
        super().__init__("QQ 已登录")


LOG = get_log("ncatbot.core.adapter.nc.login")
main_handler = None


def show_qrcode(qrcode_url):
    LOG.info(f"二维码对应的 QQ 号: {ncatbot_config.bt_uin}")
    qr = qrcode.QRCode()
    qr.add_data(qrcode_url)
    qr.print_ascii(invert=True)


# def decode_qrcode(qrcode_path):
#     img = Image.open(qrcode_path)
#     return qreader.read(img)[0].data.decode("utf-8")


def get_handler(reset=False):
    global main_handler
    if main_handler is None or reset:
        main_handler = LoginHandler()
    return main_handler


class BotUINError(Exception):
    def __init__(self, uin):
        super().__init__(
            f"BotUINError: 已经在线的 QQ {uin} 不是设置的 bot 账号 {ncatbot_config.bt_uin}"
        )


class LoginError(Exception):
    def __init__(self):
        super().__init__("登录失败")


class LoginHandler:
    # 登录处理器
    def __init__(self):
        MAX_TIME_EXPIER = time.time() + 90
        self.base_uri = f"http://{ncatbot_config.napcat.webui_host}:{ncatbot_config.napcat.webui_port}"
        while True:
            try:
                time.sleep(0.02)
                hashed_token = hashlib.sha256(
                    f"{ncatbot_config.napcat.webui_token}.{NAPCAT_WEBUI_SALT}".encode()
                ).hexdigest()
                content = requests.post(
                    self.base_uri + "/api/auth/login",
                    json={"hash": hashed_token},
                    timeout=5,
                ).json()
                time.sleep(0.02)
                self.header = {
                    "Authorization": "Bearer " + content["data"]["Credential"],
                }
                LOG.debug("成功连接到 WEBUI")
                return
            except TimeoutError:
                LOG.error("连接 WebUI 失败, 以下给出几种可能的解决方案:")
                if platform.system() == "Windows":
                    LOG.info(
                        "检查 Windows 安全中心, 查看是否有拦截了 NapCat 启动程序的日志。"
                        "如果你修改了natcat的网页端开放端口（不是websocket），请修改启动参数：webui_uri='ws://xxxxx:xxxx'"
                    )
                LOG.info("开放防火墙的 WebUI 端口 (默认 6099)")
                raise Exception("连接 WebUI 失败")
            except KeyError:
                if time.time() > MAX_TIME_EXPIER:
                    # 尝试老版本 NapCat 登录
                    try:
                        content = requests.post(
                            self.base_uri + "/api/auth/login",
                            json={"token": ncatbot_config.napcat.webui_token},
                            timeout=5,
                        ).json()
                        time.sleep(0.2)
                        self.header = {
                            "Authorization": "Bearer " + content["data"]["Credential"],
                        }
                        LOG.debug("成功连接到 WEBUI")
                        return
                    except Exception:
                        LOG.error(
                            "授权操作超时, 连接 WebUI 成功但无法获取授权信息, 可以使用 bot.run(enable_webui_interaction=False) 跳过鉴权"
                        )
                        LOG.info("建议更新到最新版本 NapCat")
                        LOG.info(traceback.format_exc())
                        raise Exception("无法获取授权信息")
            except (ConnectionError, NewConnectionError):
                if platform.system() == "Windows":
                    if time.time() > MAX_TIME_EXPIER:
                        LOG.error("授权操作超时")
                        LOG.info(
                            "考虑在启动参数中加入 enable_webui_interaction=False 跳过"
                        )
                        LOG.info("bot.run(enable_webui_interaction=False)")
                        raise Exception("连接 WebUI 失败")
                elif platform.system() == "Linux":
                    if time.time() > MAX_TIME_EXPIER:
                        LOG.error(
                            "错误 LoginHandler.__init__ ConnectionError, 请保留日志并联系开发团队"
                        )
                        raise Exception("连接 WebUI 失败")
                else:
                    LOG.error("不支持的操作系统, 请自行检查并适配")
            except Exception as e:
                if time.time() > MAX_TIME_EXPIER:
                    LOG.error(
                        f"未知错误 LoginHandler.__init__ {e}, 请保留日志并联系开发团队"
                    )
                    LOG.info(traceback.format_exc())
                    raise Exception("连接 WebUI 失败")

    def get_quick_login(self):
        try:
            data = requests.post(
                self.base_uri + "/api/QQLogin/GetQuickLoginListNew",
                headers=self.header,
                timeout=5,
            ).json()["data"]
            list = [rec["uin"] for rec in data if rec["isQuickLogin"]]
            LOG.info("快速登录列表: " + str(list))
            return list
        except TimeoutError:
            LOG.warning("获取快速登录列表失败, 禁用快速登录")
            return []

    def check_login_status(self) -> bool:
        # 检查 NapCat 是否登录
        try:
            return requests.post(
                self.base_uri + "/api/QQLogin/CheckLoginStatus",
                headers=self.header,
                timeout=5,
            ).json()["data"]["isLogin"]
        except TimeoutError:
            LOG.warning("检查登录状态超时, 默认未登录")
            return False

    def send_quick_login_request(self):
        LOG.info("正在发送快速登录请求...")
        try:
            status = requests.post(
                self.base_uri + "/api/QQLogin/SetQuickLogin",
                headers=self.header,
                json={"uin": str(ncatbot_config.bt_uin)},
                timeout=8,
            ).json()
            success = status.get("message", "failed") in ["success", "QQ Is Logined"]
            if not success:
                LOG.warning(f"快速登录请求失败: {status}")
            return success
        except TimeoutError:
            LOG.warning("快速登录失败, 进行其它登录尝试")
        except Exception:
            print(traceback.format_exc())

    def get_qrcode_url(self):
        EXPIRE = time.time() + 15
        while time.time() < EXPIRE:
            time.sleep(0.2)
            try:
                data = requests.post(
                    self.base_uri + "/api/QQLogin/GetQQLoginQrcode",
                    headers=self.header,
                    timeout=5,
                ).json()
                val = data.get("data", {}).get("qrcode", None)
                if data.get("message", None) == "QQ Is Logined":
                    raise QQLoginedError()
                if val is not None and val != "":
                    return val
                else:
                    if time.time() > EXPIRE:
                        LOG.error(f"获取二维码失败: {data}")
                        raise TimeoutError("获取二维码失败")
                    else:
                        continue
            except TimeoutError as e:
                raise e

    def get_qq_login_info(self):
        try:
            return (
                requests.post(
                    self.base_uri + "/api/QQLogin/GetQQLoginInfo",
                    headers=self.header,
                    timeout=5,
                )
                .json()
                .get("data", {})
            )
        except TimeoutError:
            LOG.warning("获取登录信息超时, 默认未登录")
            return None

    def is_target_qq_online(self) -> bool:
        info = self.get_qq_login_info()
        if info is None or "online" not in info or "uin" not in info:
            return False
        return info["online"] and str(info["uin"]) == str(ncatbot_config.bt_uin)

    def _qrcode_login(self):
        try:
            try:
                show_qrcode(self.get_qrcode_url())
            except QQLoginedError:
                if self.report_login_status() == 0:
                    LOG.info("QQ 已登录")
                    return
                else:
                    LOG.info("登录状态异常, 请物理重启本机")
                    raise Exception("登录状态异常")
            TIMEOUT_EXPIRE = time.time() + 60
            WARN_EXPIRE = time.time() + 30
            while not self.check_login_status():
                if time.time() > TIMEOUT_EXPIRE:
                    LOG.error("登录超时, 请重新操作, 如果无法扫码, 请在 webui 登录")
                    raise TimeoutError("登录超时")
                if time.time() > WARN_EXPIRE:
                    LOG.warning("二维码即将失效, 请尽快扫码登录")
                    WARN_EXPIRE += 60
            LOG.info("登录成功")
        except Exception as e:
            LOG.error(f"生成 ASCII 二维码时出错: {e}")
            LOG.info(traceback.format_exc())
            raise Exception("登录失败")

    def _quick_login(self):
        uin = str(ncatbot_config.bt_uin)
        if uin in self.get_quick_login() and self.send_quick_login_request():
            return True
        else:
            return False

    def _login(self):
        if self._quick_login():
            LOG.info("快速登录成功")
        else:
            self._qrcode_login()

    def report_login_status(self):
        """检查登录状态
        Returns:
            0: 已经正确登录
            1: 未登录
            2: 登录的 QQ 号与配置的 QQ 号不匹配
            3: 登录状态异常, 需要重启 NapCat 服务
        """
        if not self.check_login_status():
            return 1
        target_qq = str(ncatbot_config.bt_uin)
        info = self.get_qq_login_info()
        if info["uin"] != target_qq or not info["online"]:
            if info["uin"] != target_qq:
                return 2
            else:
                return 3
        else:
            return 0

    def login(self):
        if self.report_login_status() > 1:
            LOG.error("登录状态异常, 请物理重启本机")
            raise Exception("登录状态异常")
        self._login()
        if self.report_login_status() != 0:
            LOG.error("登录状态异常, 请检查是否使用了正确的 bot 账号扫码登录")
            raise Exception("登录状态异常, 请检查登录状态")


def login(reset=False):
    get_handler(reset=reset).login()


def report_login_status(reset=False):
    return get_handler(reset=reset).report_login_status()


if __name__ == "__main__":
    pass
