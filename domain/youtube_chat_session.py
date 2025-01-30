from .youtube_chat_message import AdvancedAIMessage, AdvancedHumanMessage
from typing import List, Union, Dict

AdvancedMessageType = Union[AdvancedAIMessage, AdvancedHumanMessage]


class YoutubeChatSession:
    def __init__(self, youtube_url: str, messages: List[AdvancedMessageType] = None):
        self._youtube_url = youtube_url
        self._messages = messages or []

    @property
    def youtube_url(self) -> str:
        return self._youtube_url

    @property
    def messages(self) -> List[AdvancedMessageType]:
        return self._messages

    def add_message(self, message: AdvancedMessageType):
        self._messages.append(message)

    def to_dict(self) -> dict:
        return {
            "youtube_url": self._youtube_url,
            "messages": [msg.to_dict() for msg in self._messages],
        }

    @classmethod
    def from_dict(cls, data: dict):
        messages = []
        for msg_data in data.get("messages", []):
            if msg_data["type"] == "ai":
                messages.append(AdvancedAIMessage.from_dict(msg_data))
            elif msg_data["type"] == "human":
                messages.append(AdvancedHumanMessage.from_dict(msg_data))

        return cls(youtube_url=data["youtube_url"], messages=messages)

    def __repr__(self) -> str:
        return f"ChatSession(session_id={self._youtube_url}, messages_count={len(self._messages)})"
