from ncatbot.core import BotClient, BaseMessageEvent, GroupMessageEvent
from ncatbot.utils import config
from ncatbot.plugin_system import on_message

# 基础配置（示例）
config.set_bot_uin("1550507358")
config.set_root("3051561876")

bot = BotClient()

@on_message
async def on_private_message(event: BaseMessageEvent):
    msg = event.message
    if event.is_group_msg():
        if msg.filter_text()[0].text == "测试":
            await event.reply("群聊：前端模式测试成功")
    else:
        await event.reply("你好呀! 我是 NcatBot!")


bot.run_frontend(debug=True)  # 前台线程启动，返回全局 API（同步友好）

