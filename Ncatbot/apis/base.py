# _*_ coding:utf-8 _*_
# https://github.com/gaojj2000

import os
import asyncio
import aiohttp


# Python3.8版本出现 'staticmethod' object is not callable 报错
def get_media_path(media_path):
    """
    获取媒体的本地绝对路径或网络路径
    """
    if media_path:
        if media_path.startswith('http'):
            return media_path
        elif os.path.isfile(media_path):
            abspath = os.path.abspath(os.path.join(os.getcwd(), media_path)).replace('\\', '\\\\')
            return f"file:///{abspath}"
    return ''


# Python3.8版本出现 'staticmethod' object is not callable 报错
def replace_none(fun):
    """
    去除 json 参数中为 None 的键值对（装饰器自动操作版）
    """
    def decorator(*args, **kwargs):
        data = kwargs.get('json', {})
        if data:
            for key, value in data.copy().items():
                if value is None:
                    del data[key]
            if data:
                kwargs['json'] = data
            else:
                del kwargs['json']
        return fun(*args, **kwargs)
    return decorator


class Base:
    """
    请求的基类
    """
    def __init__(self, port_or_http: (int, str), sync: bool = False):
        self.sync = sync  # 是否使用同步请求
        self.headers = {'Content-Type': 'application/json'}
        self.url = port_or_http if str(port_or_http).startswith('http') else f'http://localhost:{port_or_http}'

    @staticmethod
    def get_media_path(media_path):
        """
        获取媒体的本地绝对路径或网络路径
        """
        if media_path:
            if media_path.startswith('http'):
                return media_path
            elif os.path.isfile(media_path):
                abspath = os.path.abspath(os.path.join(os.getcwd(), media_path)).replace('\\', '\\\\')
                return f"file:///{abspath}"
        return ''
    
    @replace_none
    async def get(self, *args, **kwargs):
        async with aiohttp.ClientSession(self.url, headers=self.headers) as session:
            async with session.get(*args, **kwargs) as response:
                return await response.json()

    @replace_none
    async def post(self, *args, **kwargs):
        async with aiohttp.ClientSession(self.url, headers=self.headers) as session:
            async with session.post(*args, **kwargs) as response:
                return await response.json()

    def __getattribute__(self, item):
        """
        支持自动异步转同步（测试功能可以使用同步，开发机器人建议使用异步）
        """
        if item not in ['get', 'post']:
            item = object.__getattribute__(self, item)
            if asyncio.iscoroutinefunction(item) and object.__getattribute__(self, 'sync'):
                return lambda *args, **kwargs: asyncio.run(item(*args, **kwargs))
            return item
        return object.__getattribute__(self, item)