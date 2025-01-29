from typing import List
from .youtube_timeline_summary_section import YoutubeTimelineSection

class YoutubeTimelineSummary:
    def __init__(self, text: str, sections: List[YoutubeTimelineSection]):
        self._text = text
        self._sections = sections

    @property
    def text(self) -> str:
        return self._text

    @property
    def sections(self) -> List[YoutubeTimelineSection]:
        return self._sections

    def to_dict(self) -> dict:
        return {
            "text": self._text,
            "sections": [section.to_dict() for section in self._sections],
        }

    @classmethod
    def from_dict(cls, data: dict):
        sections = [YoutubeTimelineSection.from_dict(section) for section in data["sections"]]
        return cls(text=data["text"], sections=sections)

    def __repr__(self) -> str:
        section_preview = ", ".join(
            [f"({section.sec}s: {section.title[:15]}...)" for section in self._sections[:3]]
        )
        return (
            f"YoutubeTimelineSummary(text='{self._text[:50]}...', "
            f"sections=[{section_preview}, ...] ({len(self._sections)} sections))"
        )
