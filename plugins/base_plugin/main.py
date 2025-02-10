from ncatbot.plugins_sys import BasePlugin, Event

class hyp_plugin(BasePlugin):
    name = "hyp_plugin"
    version = "0.0.1"
    
    async def on_load(self):
        self.register_handler("ncatbot\.group|ncatbot\.private", self.handle_test)
    
    async def handle_test(self, event: Event):
        print(event.data)
        if event.data['raw_message'] == '测试':
            self.api.post_private_msg(event.data['user_id'], "Ncatbot Plugin 测试成功喵~")
        
        