from typing import Literal, Union
from .utils import BaseAPI, APIReturnStatus, run_coroutine

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
    
    async def post_private_file(self, user_id: Union[str, int], image: str=None, record: str=None, video: str=None, file: str=None) -> str:
        count = sum(1 for arg in [image, record, video, file] if arg is not None)
        if count != 1:
            raise ValueError("只能上传一个文件")
        if image is not None:
            return await self.send_private_image(user_id, image)
        elif record is not None:
            return await self.send_private_record(user_id, record)
        elif video is not None:
            return await self.send_private_video(user_id, video)
        elif file is not None:
            return await self.send_private_file(user_id, file)
        else:
            raise ValueError("必须上传一个文件")
    
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
    
    # ---------------------
    # region 同步版本接口
    # ---------------------
    
    def upload_private_file_sync(self, user_id: Union[str, int], file: str, name: str) -> None:
        return run_coroutine(self.upload_private_file, user_id, file, name)
    
    def get_private_file_url_sync(self, file_id: str) -> str:
        return run_coroutine(self.get_private_file_url, file_id)
    
    def post_private_file_sync(self, user_id: Union[str, int], image: str=None, record: str=None, video: str=None, file: str=None) -> str:
        return run_coroutine(self.post_private_file, user_id, image, record, video, file)
    
    def set_input_status_sync(self, status: int) -> None:
        return run_coroutine(self.set_input_status, status)
