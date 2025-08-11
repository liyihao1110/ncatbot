import os
import json
import shutil
from urllib.parse import urlparse
from ncatbot.core.adapter.nc.utils import get_napcat_dir, check_linux_permissions
from ncatbot.utils import get_log, ncatbot_config
from ncatbot.utils.assets.default_webui_config import config as default_webui_config

LOG = get_log("ncatbot.core.adapter.nc.config")

def config_napcat():
    """配置 napcat 服务器, 保证 napcat_dir 存在且被正确配置"""
    napcat_dir = get_napcat_dir()

    def config_onebot11():
        if os.path.exists(
            os.path.join(
                napcat_dir, "config", "onebot11_" + str(ncatbot_config.bt_uin) + ".json"
            )
        ):
            original_data = json.load(
                open(
                    os.path.join(
                        napcat_dir, "config", "onebot11_" + str(ncatbot_config.bt_uin) + ".json"
                    ),
                    "r",
                    encoding="utf-8",
                )
            )
            if original_data["parseMultMsg"] != ncatbot_config.napcat.report_forward_message_detail:
                LOG.warning("解析合并转发消息配置不匹配, 将修改为 NcatBot 配置的配置: " + str(ncatbot_config.napcat.report_forward_message_detail))
                original_data["parseMultMsg"] = ncatbot_config.napcat.report_forward_message_detail
        else:
            original_data = {
                "network": {
                    "websocketServers": [],
                },
                "musicSignUrl": "",
                "enableLocalFile2Url": False,
                "parseMultMsg": ncatbot_config.napcat.report_forward_message_detail,
            }

        expected_server_config = {
            "name": "WsServer",
            "enable": True,
            "host": ncatbot_config.napcat.ws_listen_ip,
            "port": int(urlparse(ncatbot_config.napcat.ws_uri).port),
            "messagePostFormat": "array",
            "reportSelfMessage": ncatbot_config.napcat.report_self_message,
            "token": (str(ncatbot_config.napcat.ws_token) if ncatbot_config.napcat.ws_token is not None else ""),
            "enableForcePushEvent": True,
            "debug": False,
            "heartInterval": 30000,
        }
        if expected_server_config in original_data["network"]["websocketServers"]:
            pass
        else:
            for server_config in original_data["network"]["websocketServers"]:
                if server_config["port"] == int(urlparse(ncatbot_config.napcat.ws_uri).port):
                    LOG.error(
                        f"原配置对应的端口 {server_config['port']} 已经存在, 请更改端口"
                    )
                    raise ValueError(
                        f"原配置对应的端口 {server_config['port']} 已经存在, 请更改端口"
                    )
            original_data["network"]["websocketServers"].append(expected_server_config)

        try:
            with open(
                os.path.join(
                    napcat_dir,
                    "config",
                    "onebot11_" + str(ncatbot_config.bt_uin) + ".json",
                ),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(original_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            LOG.error("配置 onebot 失败: " + str(e))
            if not check_linux_permissions():
                LOG.info("请使用 root 权限运行 ncatbot")
                raise Exception("请使用 root 权限运行 ncatbot")

    def config_quick_login():
        ori = os.path.join(napcat_dir, "quickLoginExample.bat")
        dst = os.path.join(napcat_dir, f"{ncatbot_config.bt_uin}_quickLogin.bat")
        shutil.copy(ori, dst)

    def config_webui():
        # 确定 webui 路径
        webui_config_path = os.path.join(napcat_dir, "config", "webui.json")
        try:
            with open(webui_config_path, "r") as f:
                webui_config = json.load(f)
                port = webui_config.get("port", 6099)
                token = webui_config.get("token", "")
                ws_listen_ip = webui_config.get("wsListenIp", "0.0.0.0")
            if token != ncatbot_config.napcat.webui_token:
                LOG.warning("WebUI 令牌不匹配, 将修改为 NcatBot 配置的令牌: " + ncatbot_config.napcat.webui_token)
            if port != ncatbot_config.napcat.webui_port:
                LOG.warning("WebUI 端口不匹配, 将修改为 NcatBot 配置的端口: " + str(ncatbot_config.napcat.webui_port))
                ncatbot_config.napcat.webui_port = port
            if ws_listen_ip != ncatbot_config.napcat.ws_listen_ip:
                LOG.warning("WebUI 监听 IP 不匹配, 将修改为 NcatBot 配置的监听 IP: " + ncatbot_config.napcat.ws_listen_ip)
        except FileNotFoundError:
            LOG.warning("第一次运行 WebUI, 将创建 WebUI 配置文件")
            default_webui_config["port"] = ncatbot_config.napcat.webui_port
            default_webui_config["token"] = ncatbot_config.napcat.webui_token
            default_webui_config["wsListenIp"] = ncatbot_config.napcat.ws_listen_ip
        with open(webui_config_path, "w") as f:
            json.dump(default_webui_config, f, indent=4, ensure_ascii=False)

    config_onebot11()
    config_quick_login()
    config_webui()
