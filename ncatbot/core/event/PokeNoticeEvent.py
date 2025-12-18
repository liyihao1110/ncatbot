from ncatbot.utils import status
from ncatbot.utils.thread_pool import run_coroutine
from .notice import NoticeEvent
from typing import Optional


class PokeNoticeEvent(NoticeEvent):
    """戳一戳通知事件的封装类"""

    def __init__(self, data):
        super().__init__(data)

    async def get_sender_name(self) -> Optional[str]:
        """获取发送者名称"""
        if self.group_id:
            info = await status.global_api.get_group_member_info(
                self.group_id, self.user_id
            )
            name = info.nickname
        else:
            info = await status.global_api.get_stranger_info(self.user_id)
            name = info.get("data", {}).get("nickname", self.user_id)
        return str(name)

    async def get_target_name(self) -> Optional[str]:
        if self.group_id:
            info = await status.global_api.get_group_member_info(
                self.group_id, self.target_id
            )
            name = info.nickname
        else:
            info = await status.global_api.get_stranger_info(self.target_id)
            name = info.get("data", {}).get("nickname", self.target_id)
        return str(name)

    async def get_poke_message(self) -> Optional[str]:
        """获取戳一戳的消息内容"""
        if self.sub_type != "poke":
            return None
        if not isinstance(self.raw_info, list) or len(self.raw_info) < 3:
            return None
        result = await self.get_sender_name()
        for seg in self.raw_info[2:]:
            if "txt" in seg and "type" in seg and seg["type"] == "nor":
                result += seg["txt"]
            elif "type" in seg and seg["type"] == "qq":
                name = await self.get_target_name()
                result += name
        return result

    def get_poke_message_sync(self) -> Optional[str]:
        """同步获取戳一戳的消息内容"""
        return run_coroutine(self.get_poke_message)
