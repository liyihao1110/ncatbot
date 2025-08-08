from ncatbot.core.event.event_data import BaseEventData
from typing import Literal, Optional

class Status:
    pass

class MetaEvent(BaseEventData):
    post_type: Literal['meta_event'] = None
    meta_event_type: Literal['heartbeat', 'lifecycle'] = None
    sub_type: Optional[Literal['enable', 'disable', 'connect']] = None # lifecycle
    interval: Optional[int] = None # heartbeat
    status: Optional[Status] = None # heartbeat
    def __init__(self, data: dict):
        self.meta_event_type = data.get("meta_event_type")
        self.sub_type = data.get("sub_type", None)
        self.interval = data.get("interval", None)
        self.status = data.get("status", None)
        super().__init__(data)