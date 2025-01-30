from langchain_core.messages import AIMessage, HumanMessage
import tiktoken
from typing import Dict, Any


class AdvancedAIMessage(AIMessage):
    _enc: tiktoken.Encoding = None

    def __init__(self, content: str, tokens: int = 0, check_tokens: bool = True):
        super().__init__(content=content)
        self._tokens = tokens

        if not isinstance(AdvancedAIMessage._enc, tiktoken.Encoding):
            AdvancedAIMessage._enc = tiktoken.encoding_for_model("gpt-4o-mini")

        # 토큰이 이미 존재하면 토큰 재계산을 하지 않음
        if tokens == 0 and check_tokens:
            self._tokens = len(AdvancedAIMessage._enc.encode(content))

    @property
    def role(self) -> str:
        return 'ai'

    @property
    def tokens(self) -> int:
        return self._tokens

    def to_dict(self) -> dict:
        return {"type": "ai", "content": self.content, "tokens": self._tokens}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(content=data["content"], tokens=data.get("tokens", 0), check_tokens=False)


class AdvancedHumanMessage(HumanMessage):
    _enc: tiktoken.Encoding = None

    def __init__(self, content: str, tokens: int = 0, check_tokens: bool = True):
        super().__init__(content=content)
        self._tokens = tokens

        if not isinstance(AdvancedHumanMessage._enc, tiktoken.Encoding):
            AdvancedHumanMessage._enc = tiktoken.encoding_for_model("gpt-4o-mini")

        # 토큰이 이미 존재하면 토큰 재계산을 하지 않음
        if tokens == 0 and check_tokens:
            self._tokens = len(AdvancedHumanMessage._enc.encode(content))

    @property
    def role(self) -> str:
        return 'human'

    @property
    def tokens(self) -> int:
        return self._tokens

    def to_dict(self) -> dict:
        return {"type": "human", "content": self.content, "tokens": self._tokens}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(content=data["content"], tokens=data.get("tokens", 0), check_tokens=False)
