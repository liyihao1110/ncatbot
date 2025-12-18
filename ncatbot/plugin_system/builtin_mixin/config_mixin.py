from typing import Any, Dict, Union, Callable
from ncatbot.utils import get_log

LOG = get_log("ConfigMixin")


class Config:
    def __init__(self, data: dict):
        self.name = data["name"]
        self.default_value = data["default_value"]
        self.description = data["description"]
        self.value_type = data["value_type"]
        self.metadata = data["metadata"]
        self.plugin = data["plugin"]
        self.on_change = data["on_change"]

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Config):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False

    def update(self, value: str) -> None:
        oldvalue = self.plugin.config.get(self.name, None)
        newvalue = None
        if self.value_type is bool:
            if value.lower() in ["true", "1", "yes", "on"]:
                newvalue = True
            elif value.lower() in ["false", "0", "no", "off"]:
                newvalue = False
            else:
                raise ValueError(f"Invalid boolean value: {value}")
        else:
            newvalue = self.value_type(value)
        self.plugin.config[self.name] = newvalue
        return oldvalue, newvalue


class ConfigMixin:
    def get_registered_configs(self) -> Dict[str, Config]:
        if not hasattr(self, "_registered_configs"):
            self._registered_configs: Dict[str, Config] = {}
        return self._registered_configs

    def register_config(
        self,
        name: str,
        default_value: Any = None,
        description: str = "",
        value_type: Union[type] = str,
        metadata: Dict[str, Any] = None,
        on_change: Callable = None,
        *args,
        **kwargs,
    ):
        # TODO: 自动生成描述
        # 兼容旧版
        if "default" in kwargs:
            default_value = kwargs["default"]

        if default_value is None:
            raise TypeError(
                "ConfigMixin.register_config() missing 1 required positional argument: 'default_value'"
            )

        if not hasattr(self, "_registered_configs"):
            self._registered_configs: Dict[str, Config] = dict()

        LOG.debug(f"插件 {self.name} 注册配置 {name}")
        if name not in self._registered_configs:
            if isinstance(value_type, str):
                value_type = eval(value_type)
            if self.config.get(name, None) is None:
                self.config[name] = value_type(default_value)
            self._registered_configs[name] = Config(
                {
                    "name": name,
                    "default_value": default_value,
                    "description": description,
                    "value_type": value_type,
                    "metadata": metadata,
                    "plugin": self,
                    "on_change": on_change,
                }
            )

        else:
            raise ValueError(f"配置 {name} 已存在")
