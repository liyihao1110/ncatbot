from ncatbot.plugin_system.builtin_plugin.filter_registry import register

class CompatibleEnrollment:
    def on_group_message(self, func):
        return register.group_event(func)
    
    def on_private_message(self, func):
        return register.private_event(func)
    
    def on_notice(self, func):
        return register.notice_event(func)
    
    def on_request(self, func):
        return register.request_event(func)
