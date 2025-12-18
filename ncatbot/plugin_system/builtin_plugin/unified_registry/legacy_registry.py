class LegacyRegistry:
    def __init__(self):
        self._notice_event = []
        self._request_event = []

    def notice_event(self, func):
        self._notice_event.append(func)
        return func

    def request_event(self, func):
        self._request_event.append(func)
        return func


legacy_registry = LegacyRegistry()
