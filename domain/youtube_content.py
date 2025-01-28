from .youtube_script import YouTubeScript
from .youtube_video_link import YouTubeVideoLink
from typing import List, Dict, Optional
import re
from html import escape


class YouTubeContent:
    def __init__(self, title: str, channel: str, thumbnail: str, url: YouTubeVideoLink, description: str, tags: List[str], category: str = ''
                 , script: Optional[YouTubeScript] = None
                 , script_whisper: Optional[YouTubeScript] = None
                 , script_auto: Optional[YouTubeScript] = None):

        self._title = title
        self._channel = channel
        self._thumbnail = thumbnail
        self._url = url
        self._description = description
        self._tags = tags
        self._category = category
        self._script = script
        self._script_whisper = script_whisper
        self._script_auto = script_auto

        self._cached_formatted_script = None
        self._cached_formatted_script_whisper = None
        self._cached_formatted_script_auto = None

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
    def script(self) -> Optional[YouTubeScript]:
        return self._script

    @property
    def formatted_script(self) -> str:
        if self._cached_formatted_script is not None:
            return self._cached_formatted_script

        # 대본 내용을 HTML로 변환
        self._cached_formatted_script = "\n".join(
            f'<div>'
            f'<span class="timestamp">{chunk.formatted_start_time}</span>'
            f' <span class="text">{escape(chunk.text)}</span>'
            f'</div>'
            for chunk in self.script.chunks
        )

        return self._cached_formatted_script

    @property
    def formatted_script_whisper(self) -> str:
        if self._cached_formatted_script_whisper is not None:
            return self._cached_formatted_script_whisper

        # 대본 내용을 HTML로 변환
        self._cached_formatted_script_whisper = "\n".join(
            f'<div>'
            f'<span class="timestamp">{chunk.formatted_start_time}</span>'
            f' <span class="text">{escape(chunk.text)}</span>'
            f'</div>'
            for chunk in self.script_whisper.chunks
        )

        return self._cached_formatted_script_whisper

    @property
    def script_whisper(self) -> Optional[YouTubeScript]:
        return self._script_whisper

    @property
    def script_auto(self) -> Optional[YouTubeScript]:
        return self._script_auto

    @property
    def formatted_script_auto(self) -> str:
        if self._cached_formatted_script_auto is not None:
            return self._cached_formatted_script_auto

        # 대본 내용을 HTML로 변환
        self._cached_formatted_script_auto = "\n".join(
            f'<div>'
            f'<span class="timestamp">{chunk.formatted_start_time}</span>'
            f' <span class="text">{escape(chunk.text)}</span>'
            f'</div>'
            for chunk in self.script_auto.chunks
        )

        return self._cached_formatted_script_auto

    def set_category(self, category: str):
        self._category = category

    def set_script(self, script: YouTubeScript):
        self._script = script

    def set_script_whisper(self, script: YouTubeScript):
        self._script_whisper = script

    def set_script_auto(self, script: YouTubeScript):
        self._script_auto = script

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "channel": self.channel,
            "thumbnail": self.thumbnail,
            "url": self.url.url,
            "description": self.description,
            "tags": self.tags,
            "category": self.category,
            "script": self.script.to_dict() if self.script else None,  # YouTubeScript를 dict로 변환
            "script_whisper": self.script_whisper.to_dict() if self.script_whisper else None,  # YouTubeScript를 dict로 변환
            "script_auto": self.script_auto.to_dict() if self.script_auto else None,  # YouTubeScript를 dict로 변환
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
            script=YouTubeScript.from_dict(data["script"]) if data.get("script") else None,
            script_whisper=YouTubeScript.from_dict(data["script_whisper"]) if data.get("script_whisper") else None,
            script_auto=YouTubeScript.from_dict(data["script_auto"]) if data.get("script_auto") else None,
        )

    def __repr__(self) -> str:
        return f"YouTubeContent(title={self.title}, url={self.url.url}, category={self.category})"
