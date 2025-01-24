
import json
import os
import datetime
import threading
import time
import asyncio
import platform
import psutil

from .api import BotAPI
from .setting import SetConfig

_start_time = datetime.datetime.now()
_set = SetConfig()

class OnTime:
    def __init__(self):
        self._tasks_list = {}
        self._stop_events = {}

    def add_time_task(self, trigger_time, thread_name, func):
        print(f"[user] 添加定时任务：{trigger_time} --> {func.__name__}")

        async def task_wrapper(stop_event):
            while not stop_event.is_set():
                _time = time.strftime("%H:%M", time.localtime())
                if _time == trigger_time:
                    print(f"[user] 定时任务触发：{func.__name__}")
                    if asyncio.iscoroutinefunction(func):
                        await func()
                    else:
                        func()
                    break
                await asyncio.sleep(1)

        if thread_name in self._tasks_list:
            print(f"[user] 线程 {thread_name} 已存在，无法重复创建")
            return

        stop_event = threading.Event()
        self._stop_events[thread_name] = stop_event

        def start_async_task():
            asyncio.run(task_wrapper(stop_event))

        task_thread = threading.Thread(target=start_async_task, name=thread_name, daemon=True)
        self._tasks_list[thread_name] = task_thread
        task_thread.start()
        print(f"[user] 线程 {thread_name} 启动成功")

    def cancel_time_task(self, thread_name):
        print(f"[user] 尝试取消线程 {thread_name}")
        stop_event = self._stop_events.get(thread_name)

        if not stop_event:
            print(f"[user] 线程 {thread_name} 不存在")
            return

        stop_event.set()
        self._tasks_list.pop(thread_name, None)
        self._stop_events.pop(thread_name, None)
        print(f"[user] 线程 {thread_name} 已从任务列表中移除")

    def get_tasks_list(self):
        """
        获取所有定时任务的列表。

        :return: 定时任务列表
        """
        print(f"[user] 所有定时任务的列表：{list(self._tasks_list.keys())}")
        return list(self._tasks_list.keys())

class User:
    def __init__(self):
        self.api = BotAPI(use_ws=True)
        self.on_time = OnTime()
        self.commands = ["/退出","/关机","/系统信息","/机器人信息","/设置任务","/设置在线状态","/设置头像","/设置个性签名","/获取好友列表","/帮助"]

    async def on_private_msg(self, msg):
        msg = json.loads(msg)
        if msg['post_type'] != "message":
            return
        command = msg['raw_message']
        if msg['sender']['user_id'] == _set.user_uin:
            if command.startswith("/"):
                if command == self.commands[0]:
                    await self.api.post_private_msg(user_id=_set.user_uin, text="3秒后退出")
                    time.sleep(3)
                    raise SystemExit
                elif command == self.commands[1]:
                    await self.api.post_private_msg(user_id=_set.user_uin, text="已关机")
                    os.system("shutdown -s -t 0") if os.name == "nt" else os.system("shutdown -h now")
                elif command == self.commands[2]:
                    os_level = platform.system()
                    cpu = psutil.cpu_count()
                    cpu_percent = psutil.cpu_percent()
                    mem = psutil.virtual_memory()
                    memory = f"{mem.total / (1024 * 1024 * 1024):.2f}GB"
                    memory_percent = psutil.virtual_memory().percent
                    boot_time = psutil.boot_time()
                    boot_time = datetime.datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M:%S")
                    sys_info = f"系统名称：{os_level}\nCPU：{cpu}核\nCPU使用率：{cpu_percent}%\n内存：{memory}\n内存使用率：{memory_percent}%\n开机时间：{boot_time}"
                    await self.api.post_private_msg(user_id=_set.user_uin, text=sys_info)
                elif command == self.commands[3]:
                    now = datetime.datetime.now()
                    now_time = now.strftime("%Y-%m-%d %H:%M:%S")
                    time_info = now - _start_time
                    days = time_info.days
                    tasks_list = self.on_time.get_tasks_list()
                    bot_info = f"机器人已运行{days}天\n当前时间：{now_time}\n任务列表：{tasks_list}\n警告: 创建的任务不使用请及时删除，创建多个任务会造成严重后果"
                    await self.api.post_private_msg(user_id=_set.user_uin, text=bot_info)
                elif command.split(" ")[0] == self.commands[4]:
                    command_i = command.split(" ")[1]
                    if command_i == "创建":
                        async def test():
                            await self.api.send_group_msg(group_id=command.split(" ")[4], content=command.split(" ")[5])
                        self.on_time.add_time_task(trigger_time=command.split(" ")[2], thread_name=command.split(" ")[3], func=test)
                    elif command_i == "删除":
                        self.on_time.cancel_time_task(thread_name=command.split(" ")[2])
                    else:
                        await self.api.post_private_msg(user_id=_set.user_uin, text="命令错误")
                elif command.split(" ")[0] == self.commands[5]:
                    status = command.split(" ")[1]
                    await self.api.set_online_status(status) and await self.api.post_private_msg(user_id=_set.user_uin, text="设置成功")
                elif command.split(" ")[0] == self.commands[6]:
                    file_path = command.split(" ")[1]
                    await self.api.set_qq_avatar(file_path) and await self.api.post_private_msg(user_id=_set.user_uin, text="设置成功")
                elif command.split(" ")[0] == self.commands[7]:
                    signature = command.split(" ")[1]
                    await self.api.set_self_long_nick(signature) and await self.api.post_private_msg(user_id=_set.user_uin, text="设置成功")
                elif command.split(" ")[0] == self.commands[8]:
                    t = await self.api.get_friend_list(cache=False)
                    data: list = t['data']
                    friend_list: str= ""
                    for i in data:
                        friend_list += f"{i['nickname']} {i['user_id']}\n"
                    await self.api.post_private_msg(user_id=_set.user_uin, text=friend_list)
                elif command == self.commands[9]:

                   await self.api.post_private_msg(user_id=_set.user_uin, text="""
/退出 退出程序
/关机 关闭电脑
/系统信息 获取系统信息
/机器人信息 获取机器人信息
/设置任务 创建/删除任务
/设置在线状态 设置在线状态
/设置头像 设置头像
/设置个性签名 设置个性签名
/获取好友列表 获取好友列表
/帮助 获取帮助

#以下是一些简单的例子:
/设置任务 创建 08:00 新任务 群号 你好
/设置任务 删除 新任务
/设置在线状态 恋爱中
/设置头像 图片网址
/设置个性签名 天天开心
                    """)
                else:
                    await self.api.post_private_msg(user_id=_set.user_uin, text="命令错误")
            else:
                pass
        else:
            pass














