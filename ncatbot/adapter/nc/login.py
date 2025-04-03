import os
import time

import qrcode
import requests

from ncatbot.utils.config import config
from ncatbot.utils.logger import get_log

_log = get_log()


def show_qrcode(barcode_url):
    _log.info(f"二维码指代的 url 地址: {barcode_url}")
    qr = qrcode.QRCode()
    qr.add_data(barcode_url)
    qr.print_ascii(invert=True)


class LoginHandler:
    # 登录处理器
    def __init__(self):
        self.base_uri = config.webui_uri
        try:
            content = requests.post(
                self.base_uri + "/api/auth/login",
                json={"token": config.webui_token},
                timeout=5,
            ).json()
        except TimeoutError:
            _log.error("连接 WebUI 失败")
            _log.info("请开放 webui 端口 (默认 6099)")

        self.header = {
            "Authorization": "Bearer " + content["data"]["Credential"],
        }

    def get_quick_login(self):
        # 获取快速登录列表
        try:
            data = requests.post(
                self.base_uri + "/api/QQLogin/GetQuickLoginListNew",
                headers=self.header,
                timeout=5,
            ).json()["data"]
            list = [rec["uin"] for rec in data if rec["isQuickLogin"]]
            _log.info("快速登录列表: " + str(list))
            return list
        except TimeoutError:
            _log.warning("获取快速登录列表失败, 禁用快速登录")
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
            _log.warning("检查登录状态超时, 默认未登录")
            return False

    def check_online_statu(self):
        # 检查 QQ 是否在线
        try:
            data = requests.post(
                self.base_uri + "/api/QQLogin/GetQQLoginInfo",
                headers=self.header,
                timeout=5,
            ).json()["data"]
            if data["online"] == False:
                return False
            if data["uin"] != config.bt_uin:
                if data["uin"] == config.root:
                    _log.warning("root 和 bot 账号互换, 已经自动纠正")
                    config.bt_uin, config.root = config.root, config.bt_uin
                    return True
                else:
                    _log.warning("有账号在线, 但不是 bot 账号, 进入登录流程")
                    return False
        except TimeoutError:
            _log.warning("检查在线状态超时, 默认不在线")
            return False

    def send_quick_login(self):
        # 发送快速登录请求
        _log.info("正在发送快速登录请求...")
        try:
            status = (
                requests.post(
                    self.base_uri + "/api/QQLogin/SetQuickLogin",
                    headers=self.header,
                    json={"uin": config.bt_uin},
                    timeout=5,
                )
                .json()
                .get("message", "failed")
                == "success"
            )
            return status
        except TimeoutError:
            _log.warning("快速登录失败, 进行其它登录尝试")
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

        _log.error("获取二维码失败, 请执行 `napcat stop` 后重启引导程序.")
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
            _log.info("未登录 QQ, 尝试登录")
            return _login()
        _log.info("napcat 已登录成功")
        return True


if __name__ == "__main__":
    # config.set_bot_uin(os.getenv("BOT_UIN"))
    config.set_bot_uin("3051561876")
    config.set_root(os.getenv("ROOT_UIN"))
    login = LoginHandler()
    login.check_login_statu()
    login.check_online_statu()
    login.login()
