from ncatbot.plugin_system.builtin_plugin.unified_registry import filter_registry, command_registry

class CompatibleEnrollment:
    group_event = filter_registry.group_filter
    private_event = filter_registry.private_filter
    notice_event = None
    request_event = None
