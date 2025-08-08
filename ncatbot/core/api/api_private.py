from typing import Literal, Union
from .utils import BaseAPI, APIReturnStatus

class PrivateAPI(BaseAPI):
    
    # ---------------------
    # region 文件
    # ---------------------
    async def upload_private_file(self, user_id: Union[str, int], file: str, name: str) -> None:
        result = await self.async_callback("/upload_private_file", {"user_id": user_id, "file": file, "name": name})
        APIReturnStatus.raise_if_failed(result)
    
    async def get_private_file_url(self, file_id: str) -> str:
        result = await self.async_callback("/get_private_file_url", {"file_id": file_id})
        status = APIReturnStatus(result)
        return status.data.get("url")
    
    # ---------------------
    # region 其它
    # ---------------------
    async def set_input_status(self, status: int) -> None:
        """设置输入状态

        Args:
            status (int): 状态码, 0 表示 "对方正在说话", 1 表示 "对方正在输入"
        """
        result = await self.async_callback("/set_input_status", {"status": status})
        APIReturnStatus.raise_if_failed(result)
    
    
    
    
    
    
    
