from typing import Literal, Union
from .utils import BaseAPI, APIReturnStatus

class SupportAPI(BaseAPI):
    
    # ---------------------
    # region AI 声聊
    # ---------------------
    async def get_ai_characters(self, group_id: Union[str, int], chat_type: Literal[1, 2]) -> list[dict]:
        # TODO: 返回值
        result = await self.async_callback("/get_ai_characters", {"group_id": group_id, "chat_type": chat_type})
        status = APIReturnStatus(result)
        status.raise_if_failed()
        return status.data
    
    async def get_ai_record(self, group_id: Union[str, int], character: str, text: str) -> dict:
        result = await self.async_callback("/get_ai_record", {"group_id": group_id, "character": character, "text": text})
        status = APIReturnStatus(result)
        status.raise_if_failed()
        return status.data
    
    # ---------------------
    # region 状态检查
    # ---------------------

    async def can_send_image(self) -> bool:
        result = await self.async_callback("/can_send_image")
        status = APIReturnStatus(result)
        status.raise_if_failed()
        return status.data.get("yes")

    async def can_send_record(self, group_id: Union[str, int]) -> bool:
        result = await self.async_callback("/can_send_record", {"group_id": group_id})
        status = APIReturnStatus(result)
        status.raise_if_failed()
        return status.data.get("yes")
    
    # ---------------------
    # region OCR 相关（仅 windows 可用）
    # ---------------------
    
    async def ocr_image(self, image: str) -> list[dict]:
        # TODO: 返回值
        # TODO: 支持本地文件
        result = await self.async_callback("/ocr_image", {"image": image})
        status = APIReturnStatus(result)
        status.raise_if_failed()
        return status.data
    
    # ---------------------
    # region 其它
    # ---------------------
    
    async def get_version_info(self) -> dict:
        result = await self.async_callback("/get_version_info")
        status = APIReturnStatus(result)
        status.raise_if_failed()
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
