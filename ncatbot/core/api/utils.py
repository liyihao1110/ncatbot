import asyncio
from typing import Callable
from ncatbot.utils import get_log, ncatbot_config, NcatBotError
import traceback
import threading
from typing import TypeVar, Callable, Any, Coroutine
T = TypeVar('T')

LOG = get_log("API")

class ExclusiveArgumentError(NcatBotError):
    logger = LOG
    def __init__(self, arg_name1, arg_name2, extra_info="参数互斥"):
        super().__init__(f"{extra_info}: {arg_name1}, {arg_name2}")

def run_coroutine(func: Callable[..., Coroutine[Any, Any, T]], *args, **kwargs):
    result: list[T] = []
    def runner():
        try:
            result.append(asyncio.run(func(*args, **kwargs)))
        except Exception as e:
            result.append(e)
    thread = threading.Thread(target=runner)
    thread.start()
    thread.join()
    if isinstance(result[0], Exception):
        raise result[0]
    return result[0]

def check_exclusive_argument(arg1, arg2, names: list[str], error: bool = False):
    if (arg1 is not None) == (arg2 is not None):
        if arg1 is not None:
            e = ExclusiveArgumentError(*names)
        else:
            e = ExclusiveArgumentError(*names, "至少提供一个参数")
        if error:
            raise e

class NapCatAPIError(Exception):
    def __init__(self, info):
        LOG.error(f"NapCatAPIError: {info}")
        if ncatbot_config.debug:
            LOG.info(f"stacktrace:\n{traceback.format_exc()}")
        super().__init__(info)

class APIReturnStatus:
    retcode: int = None
    message: str = None
    data: dict = None
    
    @classmethod
    def raise_if_failed(cls, data: dict):
        if data.get("retcode") != 0:
            raise NapCatAPIError(data.get("message"))
    
    def __init__(self, data: dict):
        self.raise_if_failed(data)
        self.retcode = data.get("retcode")
        self.message = data.get("message")
        self.data = data.get("data")
    
    def is_success(self):
        return self.retcode == 0
    
    def __str__(self):
        return f"APIReturnStatus(retcode={self.retcode}, message={self.message}, data={self.data})"

class MessageAPIReturnStatus(APIReturnStatus):
    @property
    def message_id(self) -> str:
        return str(self.data.get("message_id"))

class BaseAPI:
    """Base class for all API classes"""
    
    def __init__(self, async_callback: Callable[[str, dict], dict]):
        self.async_callback = async_callback