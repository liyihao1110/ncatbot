# encoding: utf-8

from .apis.user import User
from .apis.message import Message
from .apis.group import Group
from .apis.system import System
from .apis.message_chain import MessageChain

from .apis.status import Status
from .apis.faces import Face
status = Status
face = Face


class BotAPI(User, Message, Group, System, MessageChain):
    """
    API大集结
    """
    def __init__(self, port_or_http: (int, str), max_ids: int = 100, sync: bool = False):
        User.__init__(self, port_or_http=port_or_http, sync=sync)
        Message.__init__(self, port_or_http=port_or_http, sync=sync)
        Group.__init__(self, port_or_http=port_or_http, sync=sync)
        System.__init__(self, port_or_http=port_or_http, sync=sync)
        MessageChain.__init__(self, port_or_http=port_or_http, max_ids=max_ids, sync=sync)
