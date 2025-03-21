import time
import urllib.parse

import qrcode
import requests

from ncatbot.utils.config import config
from ncatbot.utils.logger import get_log

_log = get_log()


def show_qrcode(barcode_url):
    qr = qrcode.QRCode()
    qr.add_data(barcode_url)
    qr.print_ascii(invert=True)


class LoginHandler:
    # 登录处理器, 默认 webui host 同 ws_uri 的 host
    def __init__(self):
        self.host = (
            "http://"
            + urllib.parse.urlparse(config.ws_uri).hostname
            + ":"
            + str(config.webui_port)
        )
        while True:
            try:
                content = requests.post(
                    self.host + "/api/auth/login", json={"token": config.webui_token}
                ).json()
                break
            except Exception:
                _log.error(
                    "获取登录列表失败, 请检查 ufw 防火墙、服务商网络防火墙等网络设备, 并开放对应端口"
                )
                _log.info("请开放 webui 端口 (默认 6099)")
                _log.info(f"请开放 websocket 端口 {config.ws_port}")
                exit(1)
                pass

        self.header = {
            "Authorization": "Bearer " + content["data"]["Credential"],
        }

    def get_quick_login(self):
        # 获取快速登录列表
        data = requests.post(
            self.host + "/api/QQLogin/GetQuickLoginListNew", headers=self.header
        ).json()["data"]
        list = [rec["uin"] for rec in data if rec["isQuickLogin"]]
        _log.info("快速登录列表: " + str(list))
        return list

    def check_login_statu(self):
        # 检查 QQ 是否登录
        return requests.post(
            self.host + "/api/QQLogin/CheckLoginStatus", headers=self.header
        ).json()["data"]["isLogin"]

    def check_online_statu(self):
        # 检查 QQ 是否在线
        return (
            requests.post(
                self.host + "/api/QQLogin/GetQQLoginInfo", headers=self.header
            )
            .json()["data"]
            .get("online", False)
        )

    def send_quick_login(self):
        # 发送快速登录请求
        return (
            requests.post(
                self.host + "/api/QQLogin/SetQuickLogin",
                headers=self.header,
                json={"uin": config.bt_uin},
            )
            .json()
            .get("message", "failed")
            == "success"
        )

    def reqeust_qrcode_url(self):
        EXPIRE = time.time() + 10
        while time.time() < EXPIRE:
            time.sleep(0.2)
            val = requests.post(
                self.host + "/api/QQLogin/CheckLoginStatus", headers=self.header
            ).json()["data"]["qrcodeurl"]
            if val is not None:
                return val

        _log.error("获取二维码失败")
        exit(1)

    def login(self):
        def _login():
            uin = config.bt_uin
            if uin in self.get_quick_login() and self.send_quick_login():
                return True
            else:
                _log.warning("终端二维码登录为试验性功能, 如果失败请在 webui 登录")
                # qrcode_path = os.path.join(LINUX_NAPCAT_DIR, "cache", "qrcode.png")
                # os.system(f"feh {qrcode_path}")
                # if os.path.exists(qrcode_path):
                if True:
                    try:
                        show_qrcode(self.reqeust_qrcode_url())
                        TIMEOUT_EXPIRE = time.time() + 60
                        WARN_EXPIRE = time.time() + 30
                        while not self.check_online_statu():
                            if time.time() > TIMEOUT_EXPIRE:
                                _log.error(
                                    "登录超时, 请重新操作, 如果无法扫码, 请在 webui 登录"
                                )
                                exit(0)
                            if time.time() > WARN_EXPIRE:
                                _log.warning("二维码即将失效, 请尽快扫码登录")
                                WARN_EXPIRE += 60
                        _log.info("登录成功")
                    except Exception as e:
                        _log.error(f"生成 ASCII 二维码时出错: {e}")
                        exit(1)
                else:
                    _log.error("未找到二维码图片, 请在 webui 尝试扫码登录")
                    exit(1)

        if not self.check_online_statu():
            _log.info("napcat 未登录, 尝试登录")
            return _login()
        _log.info("napcat 已登录成功")
        return True
