"""Plugin main file."""

from ncatbot.core import GroupMessageEvent, PrivateMessageEvent, BaseMessageEvent
from ncatbot.plugin_system import NcatBotPlugin



class Plugin(NcatBotPlugin):
    """Plugin class."""

    name = "Plugin Name"  # 插件名称
    version = "0.1.0"  # 插件版本
    author = "Your Name"  # 插件作者
    info = "这是一个示例插件，用于演示插件系统的基本功能"  # 插件描述
    dependencies = {}  # 插件依赖，格式: {"插件名": "版本要求"}

    async def on_load(self):
        """插件加载时执行的操作."""
        print(f"{self.name} 插件已加载")
        print(f"插件版本: {self.version}")

        # 注册功能示例
        self.register_user_func(
            name="test",
            handler=self.test_handler,
            prefix="/test",
            description="测试功能",
            usage="/test",
            examples=["/test"],
            tags=["test", "example"],
            metadata={"category": "utility"},
        )

        # 注册配置项示例
        self.register_config(
            key="greeting",
            default="你好",
            on_change=self.on_greeting_change,
            description="问候语",
            value_type="string",
            allowed_values=["你好", "Hello", "Hi"],
            metadata={"category": "greeting", "max_length": 20},
        )

    async def test_handler(self, msg: BaseMessageEvent):
        """测试功能处理函数."""
        await msg.reply_text(f"测试功能调用成功！当前问候语: {self.config['greeting']}")

    async def on_greeting_change(self, value, msg: BaseMessageEvent):
        """配置变更回调函数."""
        await msg.reply_text(f"问候语已修改为: {value}")
