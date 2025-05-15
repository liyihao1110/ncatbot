from ncatbot.core import BotClient
from ncatbot.utils import get_log
from ncatbot.utils import ncatbot_config as config

"""http://172.18.229.250:6099/api/QQLogin/SetQuickLogin
login 请求
quick_login 请求
CheckLogin 请求
"""

_log = get_log()

config.bt_uin = "1550507358"  # 设置 bot qq 号 (必填)
config.root = "3051561876"  # 设置 bot 超级管理员账号 (建议填写)
config.napcat.ws_uri = "ws://localhost:3001"  # 设置 napcat websocket server 地址
config.napcat.ws_token = ""  # 设置 token (napcat 服务器的 token)

# config.plugin.skip_plugin_load = True

bot = BotClient()


# 马尾群: 925586884

if __name__ == "__main__":
    # bot.add_startup_handler(lambda: bot.api.post_private_msg_sync("3051561876", text="你好, 我是小妍"))
    # api = bot.run_blocking(bt_uin="1550507358")
    bot.run(
        bt_uin="1550507358", enable_webui_interaction=False, ws_uri="10.208.96.251:3001"
    )
    # bot.run(enable_webui_interaction=True)
    # api = bot.run_blocking(webui_uri="172.18.224.1:6099", ws_uri="ws://172.18.224.1:3001", ws_listen_ip="0.0.0.0")
    # api.post_group_msg_sync("701784439", "[CQ:reply,id=2022469614]makbak[CQ:face,id=2,raw=&#91;object Object&#93;]yaosshama[CQ:at,qq=2807962909]")
    # api.post_private_msg_sync("3051561876", Text("喵喵喵"))

    try:
        while True:
            import time

            time.sleep(1)
    except KeyboardInterrupt:
        bot.exit()
    # bot.exit()
    # bot.run_non_blocking(skip_ncatbot_install_check=True)
