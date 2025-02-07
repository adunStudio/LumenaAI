from typing import List, Dict

class YoutubeKeyPoint:
    def __init__(self, term: str, description: str) -> object:
        self._term = term
        self._description = description

    @property
    def term(self) -> str:
        return self._term

    @property
    def description(self) -> str:
        return self._description

    def to_dict(self) -> Dict[str, str]:
        return {
            "term": self._term,
            "description": self._description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]):
        return cls(
            term=data["term"],
            description=data["description"]
        )

    def __repr__(self) -> str:
        return f"YoutubeKeyPoint(term={self._term}, description={self._description[:30]}...)"