# client.py
from .message import GroupMessage,PrivateMessage

class BotClient:
    """
    一个客户端类，用于处理不同类型的消息和请求。
    """

    def __init__(self):
        """
        初始化 BotClient 实例。

        创建消息处理器、消息发送处理器、请求处理器和通知处理器的字典。
        """

        self.private_message_handlers = {
            'text': [],
            'face': [],
            'image': [],
            'record': [],
            'video': [],
            'at': [],
            'rps': [],
            'dice': [],
            'poke': [],
            'share': [],
            'contact': [],
            'location': [],
            'music': [],
            'reply': [],
            'forward': [],
            'node': [],
            'json': [],
            'mface': [],
            'file': [],
            'lightapp': []
        }
        self.group_message_handlers = {
            'text': [],
            'face': [],
            'image': [],
            'record': [],
            'video': [],
            'at': [],
            'rps': [],
            'dice': [],
            'poke': [],
            'share': [],
            'contact': [],
            'location': [],
            'music': [],
            'reply': [],
            'forward': [],
            'node': [],
            'json': [],
            'mface': [],
            'file': [],
            'lightapp': []
        }

        self.request_handlers = []
        self.notice_handlers = []

    async def private_message_handle(self, message):
        message_ = message.get('message', [])
        types = list(set(i['type'] for i in message_))
        message_obj = PrivateMessage(message)
        for message_type in types:
            for handler in self.private_message_handlers.get(message_type, []):
                await handler(message_obj)
            break


    async def group_message_handle(self, message):
        message_ = message.get('message', [])
        types = list(set(i['type'] for i in message_))
        message_obj = GroupMessage(message)
        for message_type in types:
            for handler in self.group_message_handlers.get(message_type, []):
                await handler(message_obj)
            break

    async def request_handle(self, message):
        """
        处理请求。

        根据请求类型调用相应的处理器。
        """
        for handler in self.request_handlers:
            await handler(message)

    async def notice_handle(self, message):
        """
        处理通知。

        调用所有的通知处理器。
        """
        for handler in self.notice_handlers:
            await handler(message)

    def register_handler(self, handlers_dict, types, func):
        """
        注册处理器。

        将函数注册到指定类型的处理器列表中。
        """
        if not isinstance(types, list):
            types = [types]
        for t in types:
            handlers_dict[t].append(func)

    def private_message(self, types):
        def decorator(func):
            self.register_handler(self.private_message_handlers, types, func)
            return func
        return decorator

    def group_message(self, types):
        def decorator(func):
            self.register_handler(self.group_message_handlers, types, func)
            return func
        return decorator

    def request(self, func):
        self.request_handlers.append(func)
        return func


    def notice(self, func):
        """
        装饰器，用于注册通知处理器。

        :param func: 处理器函数。
        :return: 注册的处理器函数。
        """
        self.notice_handlers.append(func)
        return func