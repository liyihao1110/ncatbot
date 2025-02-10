import sys
from pathlib import Path
# 动态添加项目根目录到 sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # 上移两级目录（plugins → NcatBot）
sys.path.append(str(PROJECT_ROOT))
'''如果安装了ncatbot包请删除1-6行'''
'''这个文件夹是一个插件仓库示例'''
from ncatbot.plugins_sys import BasePlugin, Event, CompatibleEnrollment
import os

bot = CompatibleEnrollment() # 最不自由的一集

class Test(BasePlugin):
    name = "Test"
    version = "1.0.0"
    
    async def on_load(self):
        # 注册一个事件处理器
        print('元数据   :',self.meta_data)
        print('工作路径 :',os.getcwd())
        self.register_handler("ncatbot\.group|ncatbot\.private", self.handle_test)
    
    async def on_unload(self):
        print('Test插件卸载')
    
    async def handle_test(self, event: Event):
        print(f"处理事件: {event.data}")