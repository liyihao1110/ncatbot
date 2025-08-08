from typing import Literal, Union
from ncatbot.core.event import GroupMessageEvent, PrivateMessageEvent, BaseMessageEvent
from ncatbot.core.event import (
    Record,
    Image,
    Forward,
    File,
    Music,
    Reply,
    Text,
    PlainText,
)
from ncatbot.core.event.message_segment.message_array import MessageArray
from ncatbot.utils import NcatBotValueError
from .utils import BaseAPI, APIReturnStatus, MessageAPIReturnStatus, check_exclusive_argument

class MessageAPI(BaseAPI):
    
    # ---------------------
    # region 群聊消息发送
    # ---------------------
    async def send_group_msg(self, group_id: Union[str, int], message: list[dict]) -> str:
        """顶级群聊消息发送接口（一般不开放使用）"""
        if len(message) == 0:
            raise NcatBotValueError("message", "Empty")
        # TODO validate message
        result = await self.async_callback("/send_group_msg", {"group_id": group_id, "message": message})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def post_group_array_msg(self, group_id: Union[str, int], msg: MessageArray) -> str:
        """发送群聊消息（NcatBot 接口）"""
        # TODO: 检查消息合法性
        result = await self.async_callback("/send_group_msg", {"group_id": group_id, "message": msg.to_list()})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def post_group_msg(self, group_id: Union[str, int], reply: Union[str, int]=None, text: str=None, image: str=None) -> str:
        """发送群聊消息（NcatBot 接口）"""
        msg_array = MessageArray()
        if reply is not None:
            msg_array.add_reply(reply)
        if text is not None:
            msg_array.add_text(text)
        if image is not None:
            msg_array.add_image(image)
        return await self.post_group_array_msg(group_id, msg_array)
    
    async def send_group_text(self, group_id: Union[str, int], text: str) -> str:
        """发送群聊文本消息（支持 CQ 码）（NcatBot 接口）"""
        msg_array = MessageArray(text)
        return await self.post_group_array_msg(group_id, msg_array)
    
    async def send_group_plain_text(self, group_id: Union[str, int], text: str) -> str:
        """发送群聊文本消息（不转义）（NcatBot 接口）"""
        msg_array = MessageArray(PlainText(text))
        return await self.post_group_array_msg(group_id, msg_array)
    
    async def send_group_image(self, group_id: Union[str, int], image: str) -> str:
        """发送群图片消息（NcatBot 接口）"""
        result = await self.async_callback("/send_group_msg", {"group_id": group_id, "message": [Image(file=image).to_dict()]})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def send_group_record(self, group_id: Union[str, int], file: str) -> str:
        """发送群语音消息（NcatBot 接口）"""
        result = await self.async_callback("/send_group_msg", {"group_id": group_id, "message": [Record(file=file).to_dict()]})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def send_group_dice(self, group_id: Union[str, int], value: int = 1) -> str:
        """发送群骰子消息（NcatBot 接口）

        Args:
            group_id (Union[str, int]): 群号
            value (int, optional): 骰子点数（暂不支持）. Defaults to 1.
        """
        result = await self.async_callback("/send_group_msg", {"group_id": group_id, "message": [{"type": "dice", "data": {"value": value}}]})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def send_group_rps(self, group_id: Union[str, int], value: int = 1) -> str:
        """发送群猜拳消息（NcatBot 接口）

        Args:
            group_id (Union[str, int]): 群号
            value (int, optional): 猜拳点数（暂不支持）. Defaults to 1.
        """
        result = await self.async_callback("/send_group_msg", {"group_id": group_id, "message": [{"type": "rps", "data": {"value": value}}]})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def send_group_file(self, group_id: Union[str, int], file: str, name: str=None) -> str:
        """发送群文件消息（NcatBot 接口）
        """
        payload = File(file=file, file_name=name).to_dict()
        result = await self.async_callback("/send_group_msg", {"group_id": group_id, "message": [payload]})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def send_group_music(self, group_id: Union[str, int], type: Literal["qq", "163"], id: Union[int, str]) -> str:
        """发送群音乐分享消息（NcatBot 接口）"""
        music = Music(type=type, id=id)
        result = await self.async_callback("/send_group_msg", {"group_id": group_id, "message": [music.to_dict()]})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def send_group_forward_msg(self, group_id: Union[str, int], messages: list[dict], news: list[str], prompt: str, summary: str, source: str) -> str:
        """发送群合并转发消息（NcatBot 接口）"""
        result = await self.async_callback("/send_group_forward_msg", {"group_id": group_id, "messages": messages, "news": news, "prompt": prompt, "summary": summary, "source": source})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def send_group_custom_music(self, group_id: Union[str, int], audio: str, url: str, title: str, content: str=None, image: str=None) -> str:
        """发送群音乐分享消息（NcatBot 接口）"""
        music = Music(type="custom", id=None, url=url, title=title, content=content, image=image)
        result = await self.async_callback("/send_group_msg", {"group_id": group_id, "message": [music.to_dict()]})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def forward_group_single_msg(self, group_id: Union[str, int], message_id: Union[str, int]) -> str:
        """向群聊转发单条消息（顶级接口，一般不开放使用）"""
        result = await self.async_callback("/forward_group_single_msg", {"group_id": group_id, "message_id": message_id})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def group_poke(self, group_id: Union[str, int], user_id: Union[str, int]) -> None:
        """群戳一戳"""
        result = await self.async_callback("/group_poke", {"group_id": group_id, "user_id": user_id})
        APIReturnStatus.raise_if_failed(result)
    
    # ---------------------
    # region 私聊消息发送
    # ---------------------
    async def send_private_msg(self, user_id: Union[str, int], message: list[dict]) -> str:
        """顶级私聊消息接口（一般不开放使用）"""
        if len(message) == 0:
            raise NcatBotValueError("message", "Empty")
        # TODO validate message
        result = await self.async_callback("/send_private_msg", {"user_id": user_id, "message": message})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def post_private_array_msg(self, user_id: Union[str, int], msg: MessageArray) -> str:
        """发送私聊消息（NcatBot 接口）"""
        result = await self.async_callback("/send_private_msg", {"user_id": user_id, "message": msg.to_list()})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def post_private_msg(self, user_id: Union[str, int], text: str=None, image: str=None) -> str:
        """发送私聊消息（NcatBot 接口）"""
        msg_array = MessageArray()
        if text is not None:
            msg_array.add_text(text)
        if image is not None:
            msg_array.add_image(image)
        return await self.post_private_array_msg(user_id, msg_array)
    
    async def send_private_text(self, user_id: Union[str, int], text: str) -> str:
        """发送私聊文本消息（支持 CQ 码）（NcatBot 接口）"""
        msg_array = MessageArray(text)
        return await self.post_private_array_msg(user_id, msg_array)
    
    async def send_private_plain_text(self, user_id: Union[str, int], text: str) -> str:
        """发送私聊文本消息（不转义）（NcatBot 接口）"""
        msg_array = MessageArray(PlainText(text))
        return await self.post_private_array_msg(user_id, msg_array)
    
    async def send_private_image(self, user_id: Union[str, int], image: str) -> str:
        """发送私聊图片消息（NcatBot 接口）"""
        result = await self.async_callback("/send_private_msg", {"user_id": user_id, "message": [Image(file=image).to_dict()]})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def send_private_record(self, user_id: Union[str, int], file: str) -> str:
        """发送私聊语音消息（NcatBot 接口）"""
        result = await self.async_callback("/send_private_msg", {"user_id": user_id, "message": [Record(file=file).to_dict()]})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def send_private_dice(self, user_id: Union[str, int], value: int = 1) -> str:
        """发送私聊骰子消息（NcatBot 接口）"""  
        result = await self.async_callback("/send_private_msg", {"user_id": user_id, "message": [{"type": "dice", "data": {"value": value}}]})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def send_private_rps(self, user_id: Union[str, int], value: int = 1) -> str:
        """发送私聊猜拳消息（NcatBot 接口）"""
        result = await self.async_callback("/send_private_msg", {"user_id": user_id, "message": [{"type": "rps", "data": {"value": value}}]})       
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def send_private_file(self, user_id: Union[str, int], file: str, name: str=None) -> str:
        """发送私聊文件消息（NcatBot 接口）"""
        result = await self.async_callback("/send_private_msg", {"user_id": user_id, "message": [File(file=file, file_name=name).to_dict()]})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def send_private_music(self, user_id: Union[str, int], type: Literal["qq", "163"], id: Union[int, str]) -> str:
        """发送私聊音乐分享消息（NcatBot 接口）"""
        music = Music(type=type, id=id)
        result = await self.async_callback("/send_private_msg", {"user_id": user_id, "message": [music.to_dict()]})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def send_private_forward_msg(self, user_id: Union[str, int], messages: list[dict], news: list[str], prompt: str, summary: str, source: str) -> str:
        """发送私聊合并转发消息（NcatBot 接口）"""
        result = await self.async_callback("/send_private_forward_msg", {"user_id": user_id, "messages": messages, "news": news, "prompt": prompt, "summary": summary, "source": source})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def send_private_custom_music(self, user_id: Union[str, int], audio: str, url: str, title: str, content: str=None, image: str=None) -> str:
        """发送私聊音乐分享消息（NcatBot 接口）"""
        music = Music(type="custom", id=None, url=url, title=title, content=content, image=image)
        result = await self.async_callback("/send_private_msg", {"user_id": user_id, "message": [music.to_dict()]})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def forward_private_single_msg(self, user_id: Union[str, int], message_id: Union[str, int]) -> str:
        """向私聊转发单条消息（顶级接口，一般不开放使用）"""
        result = await self.async_callback("/forward_private_single_msg", {"user_id": user_id, "message_id": message_id})
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def friend_poke(self, user_id: Union[str, int]) -> None:
        """私戳一戳"""
        result = await self.async_callback("/friend_poke", {"user_id": user_id})
        APIReturnStatus.raise_if_failed(result)
    
    # ---------------------
    # region 通用消息接口
    # ---------------------
    
    async def send_poke(self, group_id: Union[str, int] = None, user_id: Union[str, int] = None) -> None:
        """发送戳一戳消息"""
        check_exclusive_argument(group_id, user_id, ["group_id", "user_id"], error=True)
        if user_id:
            result = await self.async_callback("/friend_poke", {"user_id": user_id})
        else:
            result = await self.async_callback("/group_poke", {"group_id": group_id})
        APIReturnStatus.raise_if_failed(result)
    
    async def delete_msg(self, message_id: Union[str, int]) -> dict:
        """撤回消息、删除消息"""
        # TODO: 获取删除消息的结果
        result = await self.async_callback("/delete_msg", {"message_id": message_id})
        APIReturnStatus.raise_if_failed(result)
    
    async def set_msg_emoji_like(self, message_id: Union[str, int], emoji_id: Union[str, int], set: bool = True) -> None:
        """贴表情"""
        result = await self.async_callback("/set_msg_emoji_like", {"message_id": str(message_id), "emoji_id": int(emoji_id), "set": set})
        APIReturnStatus.raise_if_failed(result)
    
    # ---------------------
    # region 合并转发消息发送
    # ---------------------

    async def send_forward_msg(self, group_id: Union[str, int] = None, user_id: Union[str, int] = None, messages: list[GroupMessageEvent] = None, news: list[str] = None, prompt: str = None, summary: str = None, source: str = None) -> str:
        """顶级合并转发消息发送接口（一般不开放使用）

        Args:
            group_id (Union[str, int], optional): _description_. Defaults to None.
            user_id (Union[str, int], optional): _description_. Defaults to None.
            messages (list[GroupMessageEvent], optional): _description_. Defaults to None.
            news (list[str], optional): _description_. Defaults to None.
            prompt (str, optional): _description_. Defaults to None.
            summary (str, optional): _description_. Defaults to None.
            source (str, optional): _description_. Defaults to None.

        Returns:
            MessageAPIReturnStatus: _description_
        """
        check_exclusive_argument(group_id, user_id, ["group_id", "user_id"], error=True)
        data = {
            "messages": messages,
            "news": news,
            "prompt": prompt,
            "summary": summary,
            "source": source
        }
        if group_id is not None:
            data["group_id"] = str(group_id)
        else:
            data["user_id"] = str(user_id)
        result = await self.async_callback("/send_forward_msg", data)
        status = MessageAPIReturnStatus(result)
        return status.message_id
    
    async def post_forward_msg(self, group_id: Union[str, int] = None, user_id: Union[str, int] = None, msg: Forward = None):
        """发送合并转发消息（NcatBot 接口）"""
        if msg is None:
            raise NcatBotValueError("msg", "None")
        return await self.send_forward_msg(group_id, user_id, **msg.to_forward_dict())
    
    async def post_group_forward_msg(self, group_id: Union[str, int], forward: Forward) -> str:
        """发送群合并转发消息（NcatBot 接口）"""
        return await self.post_forward_msg(group_id=group_id, msg=forward)

    async def post_private_forward_msg(self, user_id: Union[str, int], forward: Forward) -> str:
        """发送私聊合并转发消息（NcatBot 接口）"""
        return await self.post_forward_msg(user_id=user_id, msg=forward)
    
    # ---------------------
    # region 消息获取
    # ---------------------
    async def get_group_msg_history(self, group_id: Union[str, int], message_seq: Union[str, int], number: int = 20, reverseOrder: bool = False) -> list[GroupMessageEvent]:
        result = await self.async_callback("/get_group_msg_history", {"group_id": group_id, "message_seq": message_seq, "number": number, "reverseOrder": reverseOrder})
        status = APIReturnStatus(result)
        return [GroupMessageEvent(data) for data in status.data.get("messages")]
    
    async def get_msg(self, message_id: Union[str, int]) -> BaseMessageEvent:
        result = await self.async_callback("/get_msg", {"message_id": message_id})
        status = APIReturnStatus(result)
        return GroupMessageEvent(status.data)
    
    async def get_forward_msg(self, message_id: Union[str, int]) -> Forward:
        result = await self.async_callback("/get_forward_msg", {"message_id": message_id})
        status = APIReturnStatus(result)
        return Forward.from_content(status.data.get("messages"), message_id)
    
    async def get_friend_msg_history(self, user_id: Union[str, int], message_seq: Union[str, int], number: int = 20, reverseOrder: bool = False) -> list[PrivateMessageEvent]:
        result = await self.async_callback("/get_friend_msg_history", {"user_id": user_id, "message_seq": message_seq, "number": number, "reverseOrder": reverseOrder})
        status = APIReturnStatus(result)
        return [PrivateMessageEvent(data) for data in status.data.get("messages")]
    
    async def get_record(self, file: str = None, file_id: str = None, out_format: Literal["mp3", "amr", "wma", "m4a", "ogg", "wav", "flac", "spx"] = "mp3") -> Record:
        """获取语音文件"""
        check_exclusive_argument(file, file_id, ["file", "file_id"])
        result = await self.async_callback("/get_record", {"file": file, "file_id": file_id, "out_format": out_format})
        status = APIReturnStatus(result)
        return Record.from_dict(status.data)
    
    async def get_image(self, file: str = None, file_id: str = None) -> Image:
        """获取图片文件"""
        check_exclusive_argument(file, file_id, ["file", "file_id"])
        result = await self.async_callback("/get_image", {"file": file, "file_id": file_id})
        status = APIReturnStatus(result)
        return Image.from_dict(status.data) 
    
    async def fetch_emoji_like(self, message_id: Union[str, int], emoji_id: Union[str, int], emoji_type: Union[str, int]) -> dict:
        """获取贴表情详情"""
        # TODO: 返回值(不紧急)
        result = await self.async_callback("/fetch_emoji_like", {"message_id": message_id, "emoji_id": emoji_id, "emoji_type": emoji_type})
        status = APIReturnStatus(result)
        return status.data