from ncatbot.plugin_system.builtin_plugin.unified_registry import filter_registry, command_registry
from ncatbot.plugin_system.builtin_plugin.unified_registry.legacy_registry import legacy_registry
class CompatibleEnrollment:
    group_event = filter_registry.group_filter
    private_event = filter_registry.private_filter
    notice_event = legacy_registry.notice_event
    request_event = legacy_registry.request_event
