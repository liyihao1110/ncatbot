'''这个文件夹是一个插件仓库示例'''
from ncatbot.plugins_sys import BasePlugin, Event, CompatibleEnrollment
import os

bot = CompatibleEnrollment # 最不自由的一集

class Test(BasePlugin):
    name = "Test"
    version = "1.0.0"
    
    @bot.group_event()
    async def a(msg):
        print('事件数据1: ',msg)
    
    async def on_load(self):
        # 注册一个事件处理器
        print('装饰器id:',id(bot))
        print('装饰器来源:',CompatibleEnrollment.__module__)
        print('元数据   :',self.meta_data)
        print('工作路径 :',os.getcwd())
        self.register_handler(r"ncatbot\.*", self.handle_test)
    
    async def on_unload(self):
        print('Test插件卸载')
    
    async def handle_test(self, event: Event):
        print(f"处理事件: {event.data}")

@bot.group_event()
async def a(msg):
    print('事件数据2: ',msg)