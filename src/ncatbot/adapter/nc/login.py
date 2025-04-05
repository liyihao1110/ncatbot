import platform
import time

import qrcode
import requests
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError

from ncatbot.utils import config, get_log

LOG = get_log("adapter.nc.login")
main_handler = None


def show_qrcode(barcode_url):
    LOG.info(f"二维码指代的 url 地址: {barcode_url}")
    qr = qrcode.QRCode()
    qr.add_data(barcode_url)
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
        MAX_TIME_EXPIER = time.time() + 30
        self.base_uri = config.webui_uri
        while True:
            try:
                time.sleep(0.2)
                content = requests.post(
                    self.base_uri + "/api/auth/login",
                    json={"token": config.webui_token},
                    timeout=10,
                ).json()
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
                exit(1)
            except (ConnectionError, NewConnectionError):
                if platform.system() == "Windows":
                    if time.time() > MAX_TIME_EXPIER:
                        LOG.error("授权操作超时")
                        LOG.info(
                            "请检查 Windows 安全中心, 查看是否有拦截了 NapCat 启动程序的日志"
                        )
                        exit(1)
                elif platform.system() == "Linux":
                    if time.time() > MAX_TIME_EXPIER:
                        LOG.error(
                            "未知错误 LoginHandler.__init__ ConnectionError, 请保留日志并联系开发团队"
                        )
                        exit(1)
                else:
                    LOG.error("不支持的操作系统, 请自行检查并适配")
            except Exception as e:
                if time.time() > MAX_TIME_EXPIER:
                    LOG.error(
                        f"未知错误 LoginHandler.__init__ {e}, 请保留日志并联系开发团队"
                    )
                    exit(1)

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

    def check_login_statu(self):
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
        try:
            data = requests.post(
                self.base_uri + "/api/QQLogin/GetQQLoginInfo",
                headers=self.header,
                timeout=5,
            ).json()["data"]
            offline = not data.get("online", False)
            uin = data.get("uin", None)
            return None if offline else str(uin)
        except TimeoutError:
            LOG.warning("检查在线状态超时, 默认不在线")
            return False

    def check_online_statu(self):
        # 检查 QQ 是否在线
        online_qq = self.get_online_qq()
        if online_qq is None:
            return False
        elif online_qq == config.bt_uin:
            return True
        else:
            raise BotUINError(online_qq)

    def send_quick_login(self):
        # 发送快速登录请求
        LOG.info("正在发送快速登录请求...")
        try:
            status = requests.post(
                self.base_uri + "/api/QQLogin/SetQuickLogin",
                headers=self.header,
                json={"uin": config.bt_uin},
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

        LOG.error("获取二维码失败, 请执行 `napcat stop` 后重启引导程序.")
        exit(1)

    def login(self):
        def _login():
            uin = config.bt_uin
            if uin in self.get_quick_login() and self.send_quick_login():
                return True
            else:
                LOG.warning("终端二维码登录为试验性功能, 如果失败请在 webui 登录")
                if True:
                    try:
                        show_qrcode(self.reqeust_qrcode_url())
                        TIMEOUT_EXPIRE = time.time() + 60
                        WARN_EXPIRE = time.time() + 30
                        while not self.check_online_statu():
                            if time.time() > TIMEOUT_EXPIRE:
                                LOG.error(
                                    "登录超时, 请重新操作, 如果无法扫码, 请在 webui 登录"
                                )
                                exit(0)
                            if time.time() > WARN_EXPIRE:
                                LOG.warning("二维码即将失效, 请尽快扫码登录")
                                WARN_EXPIRE += 60
                        LOG.info("登录成功")
                    except Exception as e:
                        LOG.error(f"生成 ASCII 二维码时出错: {e}")
                        exit(1)
                else:
                    LOG.error("未找到二维码图片, 请在 webui 尝试扫码登录")
                    exit(1)

        if not self.check_online_statu():
            LOG.info("未登录 QQ, 尝试登录")
            return _login()
        LOG.info("napcat 已登录成功")
        return True


def login(reset=False):
    if main_handler is None and platform.system() == "Windows":
        LOG.info("即将弹出权限请求, 请允许")

    get_handler(reset=reset).login()


def online_qq_is_bot():
    online_qq = get_handler().get_online_qq()
    if online_qq is not None and online_qq != config.bt_uin:
        LOG.warning(
            f"当前在线的 QQ 号为: {online_qq}, 而配置的 bot QQ 号为: {config.bt_uin}"
        )
    return online_qq is None or online_qq == config.bt_uin


if __name__ == "__main__":
    pass
