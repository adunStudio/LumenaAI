from typing import List


class YoutubeTimelineSection:
    def __init__(self, title: str, sec: float, texts: List[str], tip: str):
        self._title = title
        self._sec = sec
        self._texts = texts
        self._tip = tip

    @property
    def title(self) -> str:
        return self._title

    @property
    def sec(self) -> float:
        return self._sec

    @property
    def texts(self) -> List[str]:
        return self._texts

    @property
    def tip(self) -> str:
        return self._tip

    def to_dict(self) -> dict:
        return {
            "title": self._title,
            "sec": self._sec,
            "texts": self._texts,
            "tip": self._tip
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            title=data["title"],
            sec=data["sec"],
            texts=data["texts"],
            tip=data["tip"]
        )

    def __repr__(self) -> str:
        return f"YoutubeTimelineSection(title={self._title}, sec={self._sec}, texts=[{len(self._texts)} lines])"
