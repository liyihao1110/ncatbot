# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-05-15 19:12:16
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-06-12 18:53:15
# @Description  : IPluginApi用于显示声明动态添加的属性
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议 
# -------------------------
BotApi =object # 需要导入 BotApi

class IPluginApi:
    '''用于显示声明动态添加的属性
    >>> PluginLoader.load_plugins
    注释此行为传入的额外关键词参数'''
    api: BotApi

class AbstractPluginApi:
    def init_api(self):
        pass

class CompatibleHandler:
    '''兼容性处理器基类'''
    _subclasses = []
    
    def __init__(self, attr_name: str):
        self.attr_name = attr_name
        
    def check(self, obj: object) -> bool:
        """检查对象是否满足该处理器的处理条件"""
        raise NotImplementedError
        
    def handle(self, obj: object) -> None:
        """处理对象的兼容性行为"""
        raise NotImplementedError
    
    class __metaclass__(type):
        def __init__(cls, name, bases, attrs):
            super().__init__(name, bases, attrs)
            if cls is not CompatibleHandler:
                CompatibleHandler._subclasses.append(cls)