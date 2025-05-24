# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-11 17:26:43
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-03-17 18:56:56
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
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
        super().__init__(f"插件 '{plugin_name}' 缺少依赖: '{missing_dependency}' {version_constraints}")

class PluginVersionError(PluginSystemError):
    def __init__(self, plugin_name, required_plugin, required_version, actual_version):
        super().__init__(f"插件 '{plugin_name}' 的依赖 '{required_plugin}' 版本不满足要求: 要求 '{required_version}', 实际版本 '{actual_version}'")

class PluginUnloadError(PluginSystemError):
    def __init__(self, plugin_name, reason):
        super().__init__(f"无法卸载插件 '{plugin_name}': {reason}")

class InvalidPluginStateError(PluginSystemError):
    def __init__(self, plugin_name, state):
        super().__init__(f"插件 '{plugin_name}' 处于无效状态: {state}")

class EventHandlerError(PluginSystemError):
    def __init__(self, error_info, handler):
        super().__init__(f"事件处理器错误[{handler.__module__}]: {error_info}")

class PluginInitError(PluginSystemError):
    def __init__(self, plugin_name, reason):
        super().__init__(f"插件 '{plugin_name}' 初始化失败: {reason}")

class PluginDataError(PluginSystemError):
    def __init__(self, plugin_name, operation, reason):
        super().__init__(f"插件 '{plugin_name}' {operation}数据时出错: {reason}")
        
class PluginValidationError(PluginSystemError):
    def __init__(self, plugin_name, missing_attrs):
        super().__init__(f"插件 '{plugin_name}' 验证失败: 缺少必需属性 {', '.join(missing_attrs)}")

class PluginWorkspaceError(PluginSystemError):
    def __init__(self, plugin_name, path, reason):
        super().__init__(f"插件 '{plugin_name}' 工作目录 '{path}' 错误: {reason}")