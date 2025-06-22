from typing import Callable

class APIReturnStatus:
    retcode: int = None
    message: str = None
    data: dict = None
    def __init__(self, data: dict):
        self.retcode = data.get("retcode")
        self.message = data.get("message")
        self.data = data.get("data")
    
    def is_success(self):
        return self.retcode == 0

class MessageAPIReturnStatus(APIReturnStatus):
    @property
    def message_id(self) -> str:
        return str(self.data.get("message_id"))
    

class BotAPI:
    def __init__(self, async_callback: Callable[[str, dict], dict]):
        self.async_callback = async_callback
        
    async def simple_send_private_msg(self, user_id: str, message: dict) -> MessageAPIReturnStatus:
        return MessageAPIReturnStatus(await self.async_callback("/send_private_msg", {"user_id": user_id, "message": message}))
