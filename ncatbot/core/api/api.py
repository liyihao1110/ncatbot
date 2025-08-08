from typing import Callable
from .api_account import AccountAPI
from .api_group import GroupAPI
from .api_message import MessageAPI
from .api_private import PrivateAPI
from .api_support import SupportAPI

class BotAPI(AccountAPI, GroupAPI, MessageAPI, PrivateAPI, SupportAPI):
    """统一的 Bot API 类，通过多重继承整合所有 API 功能"""
    
    def __init__(self, async_callback: Callable[[str, dict], dict]):
        # 由于多重继承，只需要初始化一次 BaseAPI
        super().__init__(async_callback)