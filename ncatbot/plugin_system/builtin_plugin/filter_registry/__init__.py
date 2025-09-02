# 过滤器注册模块

# 导入子模块
from .filters import BaseFilter
from .command import filter, register
from .analyzer import FuncAnalyser
from .testing import test_sentence_feature
from .plugin import FilterRegistryPlugin

# 保持向后兼容的导入
from .filters import (
    SimpleFilterProtocol,
    AdvancedFilterProtocol, 
    CustomFilterFunc,
    CustomFilter,
    GroupFilter,
    PrivateFilter,
    AdminFilter,
    RootFilter
)
from .command import CommandGroup, FilterRegistry
from .analyzer.func_analyzer import get_subclass_recursive


# 向后兼容导出
__all__ = [
    # 主要插件类
    "FilterRegistryPlugin",
    
    # 过滤器相关
    "BaseFilter",
    "SimpleFilterProtocol",
    "AdvancedFilterProtocol", 
    "CustomFilterFunc",
    "CustomFilter",
    "GroupFilter",
    "PrivateFilter",
    "AdminFilter",
    "RootFilter",
    
    # 命令相关
    "CommandGroup",
    "FilterRegistry",
    "filter",
    "register",
    
    # 分析器
    "FuncAnalyser",
    "get_subclass_recursive",
    
    # 测试函数
    "test_sentence_feature"
]


if __name__ == "__main__":
    # 可以直接运行此模块来测试
    test_sentence_feature()
