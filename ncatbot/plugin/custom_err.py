# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-21 18:23:06
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-02-21 19:44:37
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @message: 喵喵喵?
# @Copyright (c) 2025 by Fish-LP, MIT License
# -------------------------
class PluginSystemError(Exception):
    pass


class PluginCircularDependencyError(PluginSystemError):
    def __init__(self, dependency_chain):
        super().__init__(f"检测到插件循环依赖: {' -> '.join(dependency_chain)}->...")


class PluginNotFoundError(PluginSystemError):
    def __init__(self, plugin_name):
        super().__init__(f"插件 '{plugin_name}' 未找到")


class PluginLoadError(PluginSystemError):
    def __init__(self, plugin_name, reason):
        super().__init__(f"无法加载插件 '{plugin_name}' : {reason}")


class PluginDependencyError(PluginSystemError):
    def __init__(self, plugin_name, missing_dependency, version_constraints):
        super().__init__(
            f"插件 '{plugin_name}' 缺少依赖: '{missing_dependency}' {version_constraints}"
        )


class PluginVersionError(PluginSystemError):
    def __init__(self, plugin_name, required_plugin, required_version, actual_version):
        super().__init__(
            f"插件 '{plugin_name}' 的依赖 '{required_plugin}' 版本不满足要求: 要求 '{required_version}', 实际版本 '{actual_version}'"
        )


class PluginUnloadError(PluginSystemError):
    def __init__(self, plugin_name, reason):
        super().__init__(f"无法卸载插件 '{plugin_name}': {reason}")


class PluginSecurityError(PluginSystemError):
    def __init__(self, plugin_name, reason):
        super().__init__(f"插件 '{plugin_name}' 存在安全问题: {reason}")


class InvalidPluginStateError(PluginSystemError):
    def __init__(self, plugin_name, state):
        super().__init__(f"插件 '{plugin_name}' 处于无效状态: {state}")
