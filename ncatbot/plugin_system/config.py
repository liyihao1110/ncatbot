# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-06-12 18:58:49
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-08-04 14:55:45
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议 
# -------------------------
from dataclasses import dataclass, field

@dataclass
class PluginSystemConfig:
    """
    插件系统配置类，用于管理插件系统的全局配置。
    """
    auto_install_pip_pack: bool = field(default=True)
    '''是否自动安装依赖的 pip 包'''
    plugins_dir: str = field(default='./plugins')
    '''插件目录路径'''
    plugins_data_dir: str = field(default='./data')
    plugins_config_dir: str = field(default='./config')
    rbac_path: str = field(default='./data/rbac.json')
    '''RBAC 配置文件路径'''

config = PluginSystemConfig()