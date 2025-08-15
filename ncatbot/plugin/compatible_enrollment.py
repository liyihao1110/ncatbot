from ncatbot.plugin_system.builtin_plugin.filter_registry import register

class CompatibleEnrollment:
    group_event = register.group_event
    private_event = register.private_event
    notice_event = register.notice_event
    request_event = register.request_event