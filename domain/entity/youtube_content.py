from domain.value_object import YouTubeVideoLink
from typing import List, Dict


class YouTubeContent:
    def __init__(self, title: str, thumbnail: str, url: YouTubeVideoLink, description: str, tags: List[str], category: str = ''):
        self._title = title
        self._thumbnail = thumbnail
        self._url = url
        self._description = description
        self._tags = tags
        self._category = category

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

    def set_category(self, category: str):
        self._category = category

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "thumbnail": self.thumbnail,
            "url": self.url.url,
            "description": self.description,
            "tags": self.tags,
            "category": self.category,
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
        )


