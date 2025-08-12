"""NcatBot 配置管理模块。"""

import copy
import os
import logging
import time
import urllib.parse
import warnings
from dataclasses import KW_ONLY, asdict, dataclass, field, fields
from typing import Any, List, Optional, Self, TextIO

import rich  # 这东西真需要吗
import yaml
from ncatbot.utils.logger import get_log
from ncatbot.utils.status import status

logger = get_log("Config")
CONFIG_PATH = os.getenv("NCATBOT_CONFIG_PATH", os.path.join(os.getcwd(), "config.yaml"))


@dataclass(frozen=False)
class BaseConfig:
    """基础配置类，提供通用功能。"""

    _: KW_ONLY

    @classmethod
    def from_dict(cls, data: dict[str, Any], /, **kwargs: Any) -> Self:
        """从字典创建新实例。

        Args:
            data: 配置数据字典
            **kwargs: 其他参数

        Returns:
            配置实例
        """
        data, kwargs = {**data, **kwargs}, {}
        for f in fields(cls):
            if f.name in data and f.init:
                if f.name in ATTRIBUTE_RECURSIVE:
                    if isinstance(data[f.name], list):
                        kwargs[f.name] = [
                            ATTRIBUTE_RECURSIVE[f.name].from_dict(d)
                            for d in data.pop(f.name)
                        ]
                    else:
                        kwargs[f.name] = ATTRIBUTE_RECURSIVE[f.name].from_dict(
                            data.pop(f.name)
                        )
                else:
                    kwargs[f.name] = data.pop(f.name)

        self = cls(**kwargs)
        sentinel = object()
        for key, value in data.items():
            if key in ATTRIBUTE_IGNORE:
                continue
            self_value = getattr(self, key, sentinel)
            if self_value is sentinel:
                warnings.warn(f"Unexpected key: {key!r}", stacklevel=2)
                setattr(self, key, value)
            elif self_value != value:
                raise ValueError(
                    f"Conflicting values for key: {key!r}, got {value!r} and already had {self_value!r}.",
                )

        return self

    def asdict(self) -> dict[str, Any]:
        """将实例转换为字典。"""
        return asdict(self)

    def __replace__(self, **kwargs: Any) -> Self:
        """替换属性值。

        Args:
            **kwargs: 要替换的属性值

        Returns:
            替换后的新实例
        """
        replaced = copy.copy(self)
        for key, value in kwargs.items():
            setattr(replaced, key, value)
        return replaced

    def pprint(self, file: TextIO | None = None) -> None:
        """美化打印实例。"""
        rich.print(self, file=file)

    def update_value(self, key, value) -> None:
        """更新配置。"""

        if hasattr(self, key):
            setattr(self, key, value)
            return True
        else:
            # TODO: 更复杂的层次结构的更新
            for attr in ATTRIBUTE_RECURSIVE:
                if hasattr(getattr(self, attr), key):
                    setattr(getattr(self, attr), key, value)
                    return True
        return False


@dataclass(frozen=False)
class NapCatConfig(BaseConfig):
    """NapCat 客户端配置。"""

    ws_uri: str = "ws://localhost:3001"
    """WebSocket URI 地址"""
    ws_token: str = ""
    """WebSocket 令牌"""
    ws_listen_ip: str = "localhost"
    """WebSocket 监听 IP"""
    webui_uri: str = "http://localhost:6099"
    """WebUI URI 地址"""
    webui_token: str = "napcat"
    """WebUI 监听"""
    webui_listen_ip: str = "0.0.0.0"
    """WebUI 令牌"""
    check_napcat_update: bool = False
    """是否检查 NapCat 更新"""
    stop_napcat: bool = False
    """退出时是否停止 NapCat"""
    suppress_client_initial_error: bool = False
    """是否抑制客户端初始错误"""
    remote_mode: bool = False
    """是否启用远程模式"""
    report_self_message: bool = False
    """是否报告自身消息"""
    report_forward_message_detail: bool = True
    """是否上报解析合并转发消息"""

    # 自动检测的值（不由构造函数初始化）
    ws_host: Optional[str] = field(default=None, init=False)
    """WebSocket 主机，从 ws_uri 自动检测"""
    webui_host: Optional[str] = field(default=None, init=False)
    """WebUI 主机，从 webui_uri 自动检测"""
    ws_port: Optional[int] = field(default=None, init=False)
    """WebSocket 端口，从 ws_uri 自动检测"""
    webui_port: Optional[int] = field(default=None, init=False)
    """WebUI 端口，从 webui_uri 自动检测"""

    def _standardize_ws_uri(self) -> None:
        """标准化 WebSocket URI 格式。"""
        if not (self.ws_uri.startswith("ws://") or self.ws_uri.startswith("wss://")):
            self.ws_uri = f"ws://{self.ws_uri}"
        parsed = urllib.parse.urlparse(self.ws_uri)
        self.ws_host = parsed.hostname
        self.ws_port = parsed.port

    def _standardize_webui_uri(self) -> None:
        """标准化 WebUI URI 格式。"""
        if not (
            self.webui_uri.startswith("http://")
            or self.webui_uri.startswith("https://")
        ):
            self.webui_uri = f"http://{self.webui_uri}"
        parsed = urllib.parse.urlparse(self.webui_uri)
        self.webui_host = parsed.hostname
        self.webui_port = parsed.port

    def validate(self) -> None:
        """验证配置，生成自动获取配置，并更新状态"""
        self._standardize_ws_uri()
        self._standardize_webui_uri()
        
        if self.ws_host not in ["localhost", "127.0.0.1"]:
            logger.info("NapCat 服务不是本地的，请确保远程服务配置正确")
            time.sleep(1)

        if self.ws_listen_ip not in {"0.0.0.0", self.ws_host}:
            logger.warning("WS 监听地址与 WS 地址不匹配，连接可能失败")
        status.update_logger_level()


@dataclass(frozen=False)
class PluginConfig(BaseConfig):
    """插件配置类。"""

    plugins_dir: str = "plugins"
    """插件目录"""
    plugin_whitelist: List[str] = field(default_factory=list)
    # """插件白名单"""
    plugin_blacklist: List[str] = field(default_factory=list)
    # """插件黑名单"""
    skip_plugin_load: bool = False
    # """是否跳过插件加载"""

    def validate(self) -> None:
        """验证配置。"""
        if not os.path.exists(self.plugins_dir):
            logger.warning(f"插件目录 {self.plugins_dir} 不存在，将自动创建")
            os.makedirs(self.plugins_dir)


@dataclass(frozen=False)
class Config(BaseConfig):
    """NcatBot 配置类。"""

    # NapCat 客户端配置
    napcat: NapCatConfig = field(default_factory=NapCatConfig)
    """NapCat 客户端配置"""

    # 插件配置
    plugin: PluginConfig = field(default_factory=PluginConfig)
    """插件配置"""

    # 需要保留的默认值
    _default_bt_uin: str = "123456"
    _default_root: str = "123456"

    # 常用配置
    root: str = _default_root
    """根用户 QQ 号"""
    bt_uin: str = _default_bt_uin
    """机器人 QQ 号"""
    enable_webui_interaction: bool = True
    """是否启用 WebUI 交互"""
    debug: bool = False
    """是否启用调试模式, 调试模式会打印部分异常的堆栈信息"""

    # 用的少的
    github_proxy: Optional[str] = field(
        default_factory=lambda: os.getenv("GITHUB_PROXY", None)
    )
    """GitHub 代理 URL"""
    check_ncatbot_update: bool = True
    """是否检查 NcatBot 更新"""
    skip_ncatbot_install_check: bool = False
    """是否跳过 NcatBot 安装检查"""

    # 暂时没用的


    @classmethod
    def create_from_file(cls, path: str) -> "Config":
        """从 YAML 文件加载配置。

        Args:
            path: 配置文件路径

        Returns:
            加载的配置实例

        Raises:
            ValueError: 如果配置文件无效或缺失
            KeyError: 如果缺少必需的配置项
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                conf_dict = yaml.safe_load(f)
                if conf_dict is None:
                    conf_dict = {}
        except FileNotFoundError as e:
            logger.warning("配置文件未找到")
            raise ValueError("[setting] 配置文件不存在！") from e
        except yaml.YAMLError as e:
            raise ValueError("[setting] 配置文件格式无效！") from e
        except Exception as e:
            raise ValueError(f"[setting] 未知错误: {e}") from e

        try:
            # 提取 napcat 配置
            napcat_dict = conf_dict.get("napcat", {})

            # 提取 plugin 配置
            plugin_dict = conf_dict.get("plugin", {})

            # 创建配置对象
            config = cls(
                napcat=NapCatConfig.from_dict(napcat_dict),
                plugin=PluginConfig.from_dict(plugin_dict),
            )

            # 将其它设置直接应用于 Config 对象
            for key, value in conf_dict.items():
                if key not in ATTRIBUTE_RECURSIVE:
                    if hasattr(config, key):
                        setattr(config, key, value)
                    else:
                        logger.warning(f"[setting] 未知配置项: {key}")

            return config
        except KeyError as e:
            raise KeyError(f"[setting] 缺少配置项: {e}") from e

    def __str__(self) -> str:
        """配置的字符串表示。"""
        return (
            f"[BOTQQ]: {self.bt_uin} | [WSURI]: {self.napcat.ws_uri} | "
            f"[WS_TOKEN]: {self.napcat.ws_token} | [ROOT]: {self.root} | "
            f"[WEBUI]: {self.napcat.webui_uri} | [WEBUI_TOKEN]: {self.napcat.webui_token}"
        )

    def update_from_file(self, path: str) -> None:
        new_config = self.create_from_file(path)
        self.__dict__.update(new_config.__dict__)

    def validate_config(self) -> None:
        """验证配置。

        Raises:
            ValueError: 如果配置无效
        """
        # 将 QQ 号转换为字符串
        self.bt_uin = str(self.bt_uin)
        self.root = str(self.root)

        if self.bt_uin == self._default_bt_uin:
            logger.warning("配置中未设置 QQ 号")
            self.bt_uin = str(input("请输入机器人 QQ 号: "))

        if self.root == self._default_root:
            logger.warning("未设置 root QQ 号，某些权限功能可能无法正常工作")

        logger.info(self)

        # 验证插件配置
        self.plugin.validate()
        self.napcat.validate()

    @staticmethod
    def load() -> "Config":
        """从默认路径加载配置。

        Returns:
            加载的配置实例
        """
        try:
            logger.debug(f"从 {CONFIG_PATH} 加载配置")
            cfg = Config.create_from_file(CONFIG_PATH)
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            cfg = Config()
        return cfg        

    def save_permanent_config(self, key: str, value: Any) -> None:
        """有些配置是永久性的，需要保存到文件中。
        Args:
            key: 配置键
            value: 配置值
        """
        try:
            # 读取现有配置文件
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    conf_dict = yaml.safe_load(f) or {}
            except FileNotFoundError:
                logger.warning(f"配置文件 {CONFIG_PATH} 不存在，将创建新文件")
                conf_dict = {}

            # 处理嵌套键 (例如 "napcat.ws_token")
            if "." in key:
                parts = key.split(".")
                section, subkey = parts[0], parts[1]

                # 确保该部分存在
                if section not in conf_dict:
                    conf_dict[section] = {}

                # 更新子键
                conf_dict[section][subkey] = value
                logger.info(f"已更新配置项 {section}.{subkey}")
            else:
                # 直接更新顶级键
                conf_dict[key] = value
                logger.info(f"已更新配置项 {key}")

            # 更新内存中的配置值
            if "." in key:
                parts = key.split(".")
                section, subkey = parts[0], parts[1]
                if hasattr(self, section) and hasattr(getattr(self, section), subkey):
                    setattr(getattr(self, section), subkey, value)
            elif hasattr(self, key):
                setattr(self, key, value)

            # 写回配置文件
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                yaml.dump(conf_dict, f, allow_unicode=True, sort_keys=False)

            logger.info(f"配置已保存到 {CONFIG_PATH}")

        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            raise ValueError(f"保存配置失败: {e}") from e

    def update_config(self, **kwargs: Any) -> None:
        """更新配置。"""
        for key, value in kwargs.items():
            if not self.update_value(key, value):
                logger.warning(f"[setting] 未知配置项: {key}")
        self.validate_config()

    def is_napcat_local(self) -> bool:
        return self.napcat.ws_host in ["localhost", "127.0.0.1"]

    # 3xx 兼容
    def set_bot_uin(self, bot_uin: str) -> None:
        self.bt_uin = str(bot_uin)
    
    def set_root(self, root: str) -> None:
        self.root = str(root)
    
    def set_ws_uri(self, ws_uri: str) -> None:
        self.napcat.ws_uri = str(ws_uri)
    
    def set_webui_uri(self, webui_uri: str) -> None:
        self.napcat.webui_uri = str(webui_uri)
    
    def set_ws_token(self, ws_token: str) -> None:
        self.napcat.ws_token = str(ws_token)
    
    def set_webui_token(self, webui_token: str) -> None:
        self.napcat.webui_token = str(webui_token)
    
    def set_ws_listen_ip(self, ws_listen_ip: str) -> None:
        self.napcat.ws_listen_ip = str(ws_listen_ip)

# 复杂嵌套对象的递归属性映射
ATTRIBUTE_RECURSIVE = {
    "napcat": NapCatConfig,
    "plugin": PluginConfig,
}

# 处理未知字段时要忽略的属性
ATTRIBUTE_IGNORE = {
    "",
}

ncatbot_config = Config.load()
