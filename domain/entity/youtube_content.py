from domain.value_object import YouTubeVideoLink
from domain.value_object import YouTubeScript
from typing import List, Dict, Optional


class YouTubeContent:
    def __init__(self, title: str, thumbnail: str, url: YouTubeVideoLink, description: str, tags: List[str], category: str = '', script: Optional[YouTubeScript] = None):
        self._title = title
        self._thumbnail = thumbnail
        self._url = url
        self._description = description
        self._tags = tags
        self._category = category
        self._script = script

    @property
    def title(self) -> str:
        return self._title

    @property
    def thumbnail(self) -> str:
        return self._thumbnail

    @property
    def url(self) -> YouTubeVideoLink:
        return self._url

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
    def script(self) -> Optional[YouTubeScript]:
        return self._script

    def set_category(self, category: str):
        self._category = category

    def set_script(self, script: YouTubeScript):
        self._script = script

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "thumbnail": self.thumbnail,
            "url": self.url.url,
            "description": self.description,
            "tags": self.tags,
            "category": self.category,
            "script": self.script.to_dict() if self.script else None,  # YouTubeScript를 dict로 변환
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'YouTubeContent':
        return cls(
            title=data["title"],
            thumbnail=data["thumbnail"],
            url=YouTubeVideoLink(data["url"]),  # 문자열을 YouTubeVideoLink 객체로 변환
            description=data["description"],
            tags=data["tags"],
            category=data.get("category", ""),
            script=YouTubeScript.from_dict(data["script"]) if data.get("script") else None,
        )

    def __repr__(self) -> str:
        return f"YouTubeContent(title={self.title}, url={self.url.url}, category={self.category})"
