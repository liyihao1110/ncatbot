from ncatbot.core.api.async_api import AsyncAPI
from ncatbot.core.api.sync_api import SyncAPI


class BotAPI(AsyncAPI, SyncAPI):
    pass
