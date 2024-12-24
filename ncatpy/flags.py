# encoding: utf-8

"""定义Intents的文件"""

class Intents:
    """定义机器人需要监听的事件通道"""
    def __init__(self,
                 private_event: bool=False,
                 group_event: bool=False,
                 request_event: bool=False,
                 notice_event: bool=False):
        self.private_event = private_event
        self.group_event = group_event
        self.request_event = request_event
        self.notice_event = notice_event

    @classmethod
    def all(cls):
        return cls(True, True, True, True)

    @classmethod
    def none(cls):
        return cls(False, False, False, False)

    @classmethod
    def public(cls):
        return cls(True, True, False, False)

    @classmethod
    def private(cls):
        return cls(True, False, False, False)

    @classmethod
    def group(cls):
        return cls(False, True, False, False)

    @classmethod
    def request(cls):
        return cls(False, False, True, False)

    @classmethod
    def notice(cls):
        return cls(False, False, False, True)
