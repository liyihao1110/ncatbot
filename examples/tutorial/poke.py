# 处理群内戳一戳事件
from ncatbot.core import BotClient, NoticeEvent

bot = BotClient()


@bot.on_notice()
async def handle_group_msg(msg: NoticeEvent):
    if msg.sub_type == "poke" and msg.target_id == msg.self_id:
        await bot.api.send_group_text(
            msg.group_id, f"[CQ:at,qq={msg.user_id}] 不要戳我！"
        )


bot.run_frontend()
