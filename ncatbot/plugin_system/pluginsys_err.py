# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-11 17:26:43
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-06-14 19:51:13
# @Description  : 插件系统自定义错误
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------

from dataclasses import dataclass

class PluginSystemError(Exception):
    """插件系统的基础错误类"""
    pass

@dataclass
class PluginCircularDependencyError(PluginSystemError):
    """检测到插件循环依赖"""
    dependency_chain: list
    def __str__(self):
        return f"检测到插件循环依赖: {' -> '.join(self.dependency_chain)}->..."

@dataclass
class PluginNotFoundError(PluginSystemError):
    """插件未找到"""
    plugin_name: str
    def __str__(self):
        return f"插件 '{self.plugin_name}' 未找到"

@dataclass
class PluginLoadError(PluginSystemError):
    """插件加载失败"""
    plugin_name: str
    reason: str
    def __str__(self):
        return f"无法加载插件 '{self.plugin_name}' : {self.reason}"

@dataclass
class PluginDependencyError(PluginSystemError):
    """插件缺少依赖"""
    plugin_name: str
    missing_dependency: str
    version_constraints: str
    def __str__(self):
        return f"插件 '{self.plugin_name}' 缺少依赖: '{self.missing_dependency}' {self.version_constraints}"

@dataclass
class PluginVersionError(PluginSystemError):
    """插件版本不满足要求"""
    plugin_name: str
    required_plugin: str
    required_version: str
    actual_version: str
    def __str__(self):
        return f"插件 '{self.plugin_name}' 的依赖 '{self.required_plugin}' 版本不满足要求: 要求 '{self.required_version}', 实际版本 '{self.actual_version}'"

@dataclass
class PluginUnloadError(PluginSystemError):
    """插件卸载失败"""
    plugin_name: str
    reason: str
    def __str__(self):
        return f"无法卸载插件 '{self.plugin_name}': {self.reason}"

@dataclass
class InvalidPluginStateError(PluginSystemError):
    """插件处于无效状态"""
    plugin_name: str
    state: str
    def __str__(self):
        return f"插件 '{self.plugin_name}' 处于无效状态: {self.state}"

@dataclass
class EventHandlerError(PluginSystemError):
    """事件处理器错误"""
    error_info: str
    handler: object
    def __str__(self):
        return f"事件处理器错误[{self.handler.__module__}]: {self.error_info}"

@dataclass
class PluginInitError(PluginSystemError):
    """插件初始化失败"""
    plugin_name: str
    reason: str
    def __str__(self):
        return f"插件 '{self.plugin_name}' 初始化失败: {self.reason}"

@dataclass
class PluginDataError(PluginSystemError):
    """插件数据操作失败"""
    plugin_name: str
    operation: str
    reason: str
    def __str__(self):
        return f"插件 '{self.plugin_name}' {self.operation}数据时出错: {self.reason}"

@dataclass
class PluginValidationError(PluginSystemError):
    """插件验证失败"""
    plugin_name: str
    missing_attrs: list
    def __str__(self):
        return f"插件 '{self.plugin_name}' 验证失败: 缺少必需属性 {', '.join(self.missing_attrs)}"

@dataclass
class PluginWorkspaceError(PluginSystemError):
    """插件工作目录错误"""
    plugin_name: str
    path: str
    reason: str
    def __str__(self):
        return f"插件 '{self.plugin_name}' 工作目录 '{self.path}' 错误: {self.reason}"

@dataclass
class PluginNameConflictError(PluginSystemError):
    """插件名称冲突"""
    plugin_name: str
    def __str__(self):
        return f"插件名称冲突: '{self.plugin_name}' 已被使用"