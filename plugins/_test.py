from ncatbot.Plugin_system import AsyncPluginInterface
from ncatbot.Logger import get_logger

_LOG = get_logger('HelloPlugin')

class HelloPlugin(AsyncPluginInterface):
    __name__ = "HelloPlugin"
    __version__ = "1.0.0"
    __author__ = "Fish-lp"
    __dependencies__ = []  # 没有依赖

    async def _init_(self):
        # 在初始化时发布一个 "hello" 事件
        self.publish("hello", message="Hello, world!")
        # 订阅 "greet" 事件
        self.on_event("greet", self.on_greet)
        _LOG.info("HelloPlugin 初始化完成")

    async def _close_(self):
        _LOG.info("HelloPlugin 已关闭")

    async def on_load(self):
        _LOG.info("HelloPlugin 已加载")

    async def on_unload(self):
        _LOG.info("HelloPlugin 已卸载")

    async def on_greet(self, message: str):
        # 监听到 "greet" 事件时的处理逻辑
        _LOG.info(f"收到问候: {message}")
        print(f"HelloPlugin 收到问候: {message}")