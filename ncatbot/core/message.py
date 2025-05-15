"""Message type definitions for NcatBot."""

from typing import List


class BaseMessage:
    """Base class for all message types."""

    def __init__(self, raw_message: str = ""):
        self.raw_message = raw_message

    async def reply_text(self, text: str) -> None:
        """Reply to this message with text.

        Args:
            text: The text to reply with.
        """
        pass


class GroupMessage(BaseMessage):
    """A message sent in a group chat."""

    def __init__(self, group_id: str = "", user_id: str = "", raw_message: str = ""):
        super().__init__(raw_message)
        self.group_id = group_id
        self.user_id = user_id


class PrivateMessage(BaseMessage):
    """A message sent in a private chat."""

    def __init__(self, user_id: str = "", raw_message: str = ""):
        super().__init__(raw_message)
        self.user_id = user_id


class MessageComponent:
    """Base class for message components."""

    pass


class Text(MessageComponent):
    """A text component in a message."""

    def __init__(self, text: str = ""):
        self.text = text

    def __str__(self) -> str:
        return self.text


class At(MessageComponent):
    """An @mention component in a message."""

    def __init__(self, qq: str = ""):
        self.qq = qq

    def __str__(self) -> str:
        return f"@{self.qq}"


class MessageChain:
    """A chain of message components."""

    def __init__(self, components: List[MessageComponent] = None):
        self.components = components or []

    def __str__(self) -> str:
        return "".join(str(component) for component in self.components)
