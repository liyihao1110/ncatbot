from ncatbot.core import BotClient
from ncatbot.utils import config

# 基础配置（示例）
config.set_bot_uin("1550507358")

bot = BotClient()
api = bot.run_backend(debug=True)  # 后台线程启动，返回全局 API（同步友好）

# 同步接口主动发消息（示例群号/QQ 号请替换）
api.send_group_text_sync(701784439, "后端已启动：Hello from backend")
api.send_private_text_sync(3051561876, "后端问候：Hi")

print("后台已运行，继续做其他同步任务……")