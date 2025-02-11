from typing import Sequence

from packaging.version import Version


class PluginSystemError(Exception):
    """插件系统的基础异常类,所有插件相关的异常都应继承自此类"""

    pass


class PluginCircularDependencyError(PluginSystemError):
    """当插件之间存在循环依赖时抛出此异常"""

    def __init__(self, dependency_chain: Sequence[str]):
        self.dependency_chain = dependency_chain
        super().__init__(
            f"检测到插件循环依赖: {' -> '.join(dependency_chain)}->... 请检查插件之间的依赖关系"
        )


class PluginNotFoundError(PluginSystemError):
    """当尝试加载或使用一个不存在的插件时抛出此异常"""

    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name
        super().__init__(
            f"插件 '{plugin_name}' 未找到 请检查插件名称是否正确,以及插件是否已正确安装"
        )


class PluginLoadError(PluginSystemError):
    """当插件加载过程中出现错误时抛出此异常"""

    def __init__(self, plugin_name: str, reason):
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(f"无法加载插件 '{plugin_name}' : {reason}")


class PluginInitializationError(PluginSystemError):
    """当插件初始化失败时抛出此异常"""

    def __init__(self, plugin_name: str, reason):
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(f"插件 '{plugin_name}' 初始化失败: {reason}")


class PluginDependencyError(PluginSystemError):
    """当插件依赖未满足时抛出此异常"""

    def __init__(self, plugin_name: str, missing_dependency):
        self.plugin_name = plugin_name
        self.missing_dependency = missing_dependency
        super().__init__(
            f"插件 '{plugin_name}' 缺少必要的依赖项: {'|'.join(missing_dependency)}"
        )


class PluginConfigurationError(PluginSystemError):
    """当插件配置不正确时抛出此异常"""

    def __init__(self, plugin_name: str, reason):
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(f"插件 '{plugin_name}' 配置错误: {reason}")


class PluginExecutionError(PluginSystemError):
    """当插件执行过程中出现错误时抛出此异常"""

    def __init__(self, plugin_name: str, reason):
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(f"插件 '{plugin_name}' 执行失败: {reason}")


class PluginCompatibilityError(PluginSystemError):
    """当插件与当前系统或环境不兼容时抛出此异常"""

    def __init__(self, plugin_name: str, reason):
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(f"插件 '{plugin_name}' 与当前环境不兼容: {reason}")


class PluginAlreadyLoadedError(PluginSystemError):
    """当尝试重复加载同一个插件时抛出此异常"""

    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name
        super().__init__(f"插件 '{plugin_name}' 已经被加载,无法重复加载")


class PluginUnloadError(PluginSystemError):
    """当插件卸载过程中出现错误时抛出此异常"""

    def __init__(self, plugin_name: str, reason):
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(f"无法卸载插件 '{plugin_name}': {reason}")


class PluginSecurityError(PluginSystemError):
    """当插件存在安全问题时抛出此异常"""

    def __init__(self, plugin_name: str, reason):
        self.plugin_name = plugin_name
        self.reason = reason
        super().__init__(f"插件 '{plugin_name}' 存在安全问题: {reason}")


class PluginVersionError(PluginSystemError):
    """当插件版本不满足要求时抛出此异常"""

    def __init__(
        self,
        plugin_name: str,
        required_plugin_name: str,
        required_version: str,
        actual_version: Version,
    ):
        self.plugin_name = plugin_name
        self.required_plugin_name = required_plugin_name
        self.required_version = required_version
        self.actual_version = actual_version
        super().__init__(
            f"插件 '{required_plugin_name}' 版本不满足要求'{plugin_name}'需要 '{required_plugin_name}' 的版本: {required_version},实际版本: {actual_version.public}"
        )
