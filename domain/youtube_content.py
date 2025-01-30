from .youtube_script import YouTubeScript
from .youtube_video_link import YouTubeVideoLink
from .youtube_timeline_summary import YoutubeTimelineSummary
from typing import List, Dict, Optional
import re


class YouTubeContent:
    def __init__(self, title: str, channel: str, thumbnail: str, url: YouTubeVideoLink, description: str, tags: List[str], category: str = ''
                 , timeline_summary: Optional[YoutubeTimelineSummary] = None):

        self._title = title
        self._channel = channel
        self._thumbnail = thumbnail
        self._url = url
        self._description = description
        self._tags = tags
        self._category = category
        self._timeline_summary = timeline_summary

    @property
    def title(self) -> str:
        return self._title

    @property
    def channel(self) -> str:
        return self._channel

    def set_channel(self, channel) -> str:
        self._channel = channel

    @property
    def thumbnail(self) -> str:
        return self._thumbnail

    @property
    def url(self) -> YouTubeVideoLink:
        return self._url

    @property
    def video_id(self) -> str:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", self.url.url)
        return match.group(1) if match else None

    @property
    def description(self) -> str:
        return self._description

    @property
    def tags(self) -> List[str]:
        return self._tags

    @property
    def category(self) -> str:
        return self._category

    @property
    def timeline_summary(self) -> Optional[YoutubeTimelineSummary]:
        return self._timeline_summary

    def set_timeline_summary(self, timeline_summary: YoutubeTimelineSummary):
        self._timeline_summary = timeline_summary

    def set_category(self, category: str):
        self._category = category

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "channel": self.channel,
            "thumbnail": self.thumbnail,
            "url": self.url.url,
            "description": self.description,
            "tags": self.tags,
            "category": self.category,
            "timeline_summary": self.timeline_summary.to_dict() if self._timeline_summary else None,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'YouTubeContent':
        return cls(
            title=data["title"],
            channel=data['channel'],
            thumbnail=data["thumbnail"],
            url=YouTubeVideoLink(data["url"]),  # 문자열을 YouTubeVideoLink 객체로 변환
            description=data["description"],
            tags=data["tags"],
            category=data.get("category", ""),
            timeline_summary=YoutubeTimelineSummary.from_dict(data["timeline_summary"]) if data.get('timeline_summary') else None,
        )

    def __repr__(self) -> str:
        return f"YouTubeContent(title={self.title}, url={self.url.url}, category={self.category})"
