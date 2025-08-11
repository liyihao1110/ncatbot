from typing import Literal, Union
from .utils import BaseAPI, APIReturnStatus, run_coroutine
from ncatbot.core.event.message_segment.message_segment import convert_uploadable_object

class AICharacter:
    def __init__(self, data: dict):
        self.character_id = data.get("character_id")
        self.character_name = data.get("character_name")
        self.preview_url = data.get("preview_url")
        
    def __repr__(self) -> str:
        return f"AICharacter(name={self.character_name})"
    
    def get_details(self) -> dict:
        return {
            "character_id": self.character_id,
            "character_name": self.character_name,
            "preview_url": self.preview_url
        }

class AICharacterList:
    def __init__(self, data: list[dict]):
        self.characters = [AICharacter(item) for item in data]
    
    def __repr__(self) -> str:
        return f"AICharacterList(characters={self.characters})"
    
    def get_search_id_by_name(self, name: str) -> str:
        for character in self.characters:
            if character.character_name == name:
                return character.character_id
        return None

class SupportAPI(BaseAPI):
    
    # ---------------------
    # region AI 声聊
    # ---------------------
    async def get_ai_characters(self, group_id: Union[str, int], chat_type: Literal[1, 2]) -> AICharacterList:
        result = await self.async_callback("/get_ai_characters", {"group_id": group_id, "chat_type": chat_type})
        status = APIReturnStatus(result)
        all_characters = sum([item["characters"] for item in status.data], [])
        return AICharacterList(all_characters)
    
    async def get_ai_record(self, group_id: Union[str, int], character_id: str, text: str) -> str:
        """
        发送 AI 声聊并返回链接 str（似乎用不了）
        :param group_id: 群号
        :param character_id: 角色ID
        :param text: 文本
        :return: 链接
        """
        result = await self.async_callback("/get_ai_record", {"group_id": group_id, "character": character_id, "text": text})
        status = APIReturnStatus(result)
        return status.data
    
    # ---------------------
    # region 状态检查
    # ---------------------

    async def can_send_image(self) -> bool:
        result = await self.async_callback("/can_send_image")
        status = APIReturnStatus(result)
        
        return status.data.get("yes")

    async def can_send_record(self, group_id: Union[str, int]) -> bool:
        result = await self.async_callback("/can_send_record", {"group_id": group_id})
        status = APIReturnStatus(result)
        return status.data.get("yes")
    
    # ---------------------
    # region OCR 相关（仅 windows 可用）
    # ---------------------
    
    async def ocr_image(self, image: str) -> list[dict]:
        # TODO: 返回值(不紧急)
        result = await self.async_callback("/ocr_image", {"image": convert_uploadable_object(image)})
        status = APIReturnStatus(result)
        
        return status.data
    
    # ---------------------
    # region 其它
    # ---------------------
    
    async def get_version_info(self) -> dict:
        """
        获取 NapCat 版本信息
        """
        result = await self.async_callback("/get_version_info")
        status = APIReturnStatus(result)
        return status.data
    
    async def bot_exit(self) -> None:
        """退出机器人"""
        # TODO: 测试
        result = await self.async_callback("/bot_exit")
        APIReturnStatus.raise_if_failed(result)
    
    # ---------------------
    # region 实验性功能
    # ---------------------
    
    pass
    
    # ---------------------
    # region 同步版本接口
    # ---------------------
    
    def get_ai_characters_sync(self, group_id: Union[str, int], chat_type: Literal[1, 2]) -> AICharacterList:
        return run_coroutine(self.get_ai_characters, group_id, chat_type)
    
    def get_ai_record_sync(self, group_id: Union[str, int], character_id: str, text: str) -> str:
        return run_coroutine(self.get_ai_record, group_id, character_id, text)

    def can_send_image_sync(self) -> bool:
        return run_coroutine(self.can_send_image)

    def can_send_record_sync(self, group_id: Union[str, int]) -> bool:
        return run_coroutine(self.can_send_record, group_id)
    
    def ocr_image_sync(self, image: str) -> list[dict]:
        return run_coroutine(self.ocr_image, image)
    
    def get_version_info_sync(self) -> dict:
        return run_coroutine(self.get_version_info)
    
    def bot_exit_sync(self) -> None:
        return run_coroutine(self.bot_exit)
