import hashlib
import platform
import time
import traceback

import qrcode
import requests
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError

from ncatbot.utils import NAPCAT_WEBUI_SALT, config, get_log

LOG = get_log("adapter.nc.login")
main_handler = None


def show_qrcode(qrcode_url):
    LOG.info(f"二维码指代的 url 地址: {qrcode_url}")
    qr = qrcode.QRCode()
    qr.add_data(qrcode_url)
    qr.print_ascii(invert=True)


def get_handler(reset=False):
    global main_handler
    if main_handler is None or reset:
        main_handler = LoginHandler()
    return main_handler


class BotUINError(Exception):
    def __init__(self, uin):
        super().__init__(
            f"BotUINError: 已经在线的 QQ {uin} 不是设置的 bot 账号 {config.bt_uin}"
        )


class LoginError(Exception):
    def __init__(self):
        super().__init__("登录失败")


class LoginHandler:
    # 登录处理器
    def __init__(self):
        MAX_TIME_EXPIER = time.time() + 15
        self.base_uri = config.webui_uri
        while True:
            try:
                time.sleep(0.02)
                hashed_token = hashlib.sha256(
                    f"{config.webui_token}.{NAPCAT_WEBUI_SALT}".encode()
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
                            json={"token": config.webui_token},
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
                        raise Exception("连接 WebUI 失败")
            except (ConnectionError, NewConnectionError):
                if platform.system() == "Windows":
                    if time.time() > MAX_TIME_EXPIER:
                        LOG.error("授权操作超时")
                        LOG.info(
                            "请检查 Windows 安全中心, 查看是否有拦截了 NapCat 启动程序的日志"
                        )
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
        # 获取快速登录列表
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

    def check_login_status(self):
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

    def get_online_qq(self):
        """获取当前在线的 QQ 号, 如果无 QQ 在线, 则返回 None"""
        for _ in range(5):
            try:
                data = requests.post(
                    self.base_uri + "/api/QQLogin/GetQQLoginInfo",
                    headers=self.header,
                    timeout=5,
                ).json()["data"]
                offline = not data.get("online", False)
                uin = data.get("uin", None)
                if not offline:
                    return str(uin)
            except TimeoutError:
                LOG.warning("检查在线状态超时, 默认不在线")
                return False
            time.sleep(0.05)
        return None

    def check_online_status(self):
        # 检查 QQ 是否在线
        online_qq = self.get_online_qq()
        if online_qq is None:
            return False
        elif is_qq_equal(online_qq, config.bt_uin):
            return True
        else:
            raise BotUINError(online_qq)

    def send_quick_login_request(self):
        # 发送快速登录请求
        LOG.info("正在发送快速登录请求...")
        try:
            status = requests.post(
                self.base_uri + "/api/QQLogin/SetQuickLogin",
                headers=self.header,
                json={"uin": str(config.bt_uin)},
                timeout=5,
            ).json().get("message", "failed") in ["success", "QQ Is Logined"]
            return status
        except TimeoutError:
            LOG.warning("快速登录失败, 进行其它登录尝试")
            pass

    def reqeust_qrcode_url(self):
        EXPIRE = time.time() + 15
        while time.time() < EXPIRE:
            time.sleep(0.2)
            try:
                data = requests.post(
                    self.base_uri + "/api/QQLogin/CheckLoginStatus",
                    headers=self.header,
                    timeout=5,
                ).json()["data"]
                val = data["qrcodeurl"]
                if val is not None and val != "":
                    return val
            except TimeoutError:
                pass

        LOG.error(
            f"获取二维码失败, 请执行 `napcat stop; napcat start {config.bt_uin}` 后重启引导程序."
        )
        raise Exception("获取二维码失败")

    def login(self):
        def _login():
            uin = str(config.bt_uin)
            if uin in self.get_quick_login() and self.send_quick_login_request():
                return True
            else:
                LOG.warning("终端二维码登录为试验性功能, 如果失败请在 webui 登录")
                if True:
                    try:
                        show_qrcode(self.reqeust_qrcode_url())
                        TIMEOUT_EXPIRE = time.time() + 60
                        WARN_EXPIRE = time.time() + 30
                        while not self.check_online_status():
                            if time.time() > TIMEOUT_EXPIRE:
                                LOG.error(
                                    "登录超时, 请重新操作, 如果无法扫码, 请在 webui 登录"
                                )
                                raise TimeoutError("登录超时")
                            if time.time() > WARN_EXPIRE:
                                LOG.warning("二维码即将失效, 请尽快扫码登录")
                                WARN_EXPIRE += 60
                        LOG.info("登录成功")
                    except Exception as e:
                        LOG.error(f"生成 ASCII 二维码时出错: {e}")
                        raise Exception("登录失败")
                else:
                    LOG.error("未找到二维码图片, 请在 webui 尝试扫码登录")
                    raise Exception("登录失败")

        if not self.check_online_status():
            LOG.info("未登录 QQ, 尝试登录")
            return _login()
        LOG.info("napcat 已登录成功")
        return True


def login(reset=False):
    if main_handler is None and platform.system() == "Windows":
        LOG.info("即将弹出权限请求, 请允许")

    get_handler(reset=reset).login()


def is_qq_equal(uin, other):
    """判断 QQ 号是否相等"""
    return str(uin) == str(other)


def online_qq_is_bot():
    handler = get_handler(reset=True)
    online_qq = handler.get_online_qq()

    if online_qq is not None and not is_qq_equal(online_qq, config.bt_uin):
        LOG.warning(
            f"当前在线的 QQ 号为: {online_qq}, 而配置的 bot QQ 号为: {config.bt_uin}"
        )
    return online_qq is None or is_qq_equal(online_qq, config.bt_uin)


if __name__ == "__main__":
    pass
