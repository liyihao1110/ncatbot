from .commnad_mixin import CommandMixin
from typing import Any, List, Dict, Union
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils import PermissionGroup

class Config:
    def __init__(self, data: dict):
        self.name = data['name']
        self.default_value = data['default_value']
        self.description = data['description']
        self.value_type = data['value_type']
        self.metadata = data['metadata']
    
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Config):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False

class ConfigMixin(CommandMixin):
    _registered_configs: Dict[str, Config] = {}
    def _configurator(self, event: BaseMessageEvent, args: List[str]):
        # [config].[plugin_name] [config_name] [value]
        # TODO 错误提示
        try:
            if len(args) < 3:
                raise ValueError("参数不足")
            config_name = args[2]
            if config_name not in self._registered_configs:
                raise ValueError(f"配置 {config_name} 不存在")
            config = self._registered_configs[config_name]
            real_value = config.value_type(args[2])
            self.config["config.name"] = real_value
        except Exception as e:
            pass
            # event.reply_sync()
    
    def get_registered_configs(self) -> Dict[str, Config]:
        if not hasattr(self, '_registered_configs'):
            self._registered_configs: Dict[str, Config] = {}
        return self._registered_configs
    
    def register_config(self, name: str, default_value: Any, description: str = "", value_type: type = Union[str, int, bool], metadata: Dict[str, Any] = None):
        # TODO: 自动生成描述
        if not hasattr(self, "_registered_configs"):
            self._registered_configs: Dict[str, Config] = {}
            self.register_command(f"config.{self.name}", self._configurator, permission=PermissionGroup.ADMIN.value)
            
        if name not in self._registered_configs:
            if isinstance(value_type, str):
                value_type = eval(value_type)
            self.config[name] = value_type(default_value)
            self._registered_configs[name] = Config({
                'name': name,
                'default_value': default_value,
                'description': description,
                'value_type': value_type,
                'metadata': metadata
            })
        else:
            raise ValueError(f"配置 {name} 已存在")