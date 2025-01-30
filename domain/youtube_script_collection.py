from typing import Optional, List
from html import escape
from .youtube_script import YouTubeScript

class YoutubeScriptCollection:
    def __init__(
        self,
        youtube_url: str,
        auto_script: Optional[YouTubeScript] = None,
        whisper_script: Optional[YouTubeScript] = None,
        refined_script: Optional[YouTubeScript] = None
    ):
        self._youtube_url = youtube_url
        self._auto_script = auto_script
        self._whisper_script = whisper_script
        self._refined_script = refined_script

        self._cached_formatted_auto_script = None
        self._cached_formatted_whisper_script = None
        self._cached_formatted_refined_script = None

    @property
    def youtube_url(self) -> str:
        return self._youtube_url

    @property
    def auto_script(self) -> Optional[YouTubeScript]:
        return self._auto_script

    @property
    def whisper_script(self) -> Optional[YouTubeScript]:
        return self._whisper_script

    @property
    def refined_script(self) -> Optional[YouTubeScript]:
        return self._refined_script

    def set_auto_script(self, script: YouTubeScript):
        self._auto_script = script

    def set_whisper_script(self, script: YouTubeScript):
        self._whisper_script = script

    def set_refined_script(self, script: YouTubeScript):
        self._refined_script = script

    def to_dict(self) -> dict:
        return {
            "youtube_url": self._youtube_url,
            "auto_script": self._auto_script.to_dict() if self._auto_script else None,
            "whisper_script": self._whisper_script.to_dict() if self._whisper_script else None,
            "refined_script": self._refined_script.to_dict() if self._refined_script else None,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            youtube_url=data["youtube_url"],
            auto_script=YouTubeScript.from_dict(data["auto_script"]) if data.get("auto_script") else None,
            whisper_script=YouTubeScript.from_dict(data["whisper_script"]) if data.get("whisper_script") else None,
            refined_script=YouTubeScript.from_dict(data["refined_script"]) if data.get("refined_script") else None,
        )

    def __repr__(self) -> str:
        return (
            f"YouTubeCollectionScript(youtube_url='{self._youtube_url}', "
            f"auto_script={'present' if self._auto_script else 'None'}, "
            f"whisper_script={'present' if self._whisper_script else 'None'}, "
            f"refined_script={'present' if self._refined_script else 'None'})"
        )

    @property
    def formatted_auto_script(self) -> str:
        if self._cached_formatted_auto_script is not None:
            return self._cached_formatted_auto_script

        # 대본 내용을 HTML로 변환
        self._cached_formatted_auto_script = "\n".join(
            f'<div>'
            f'<span class="timestamp">{chunk.formatted_start_time}</span>'
            f' <span class="text">{escape(chunk.text)}</span>'
            f'</div>'
            for chunk in self._auto_script.chunks
        )

        return self._cached_formatted_auto_script

    @property
    def formatted_whisper_script(self) -> str:
        if self._cached_formatted_whisper_script is not None:
            return self._cached_formatted_whisper_script

        # 대본 내용을 HTML로 변환
        self._cached_formatted_whisper_script = "\n".join(
            f'<div>'
            f'<span class="timestamp">{chunk.formatted_start_time}</span>'
            f' <span class="text">{escape(chunk.text)}</span>'
            f'</div>'
            for chunk in self._whisper_script.chunks
        )

        return self._cached_formatted_whisper_script

    @property
    def formatted_refined_script(self) -> str:
        if self._cached_formatted_refined_script is not None:
            return self._cached_formatted_refined_script

        # 대본 내용을 HTML로 변환
        self._cached_formatted_refined_script = "\n".join(
            f'<div>'
            f'<span class="timestamp">{chunk.formatted_start_time}</span>'
            f' <span class="text">{escape(chunk.text)}</span>'
            f'</div>'
            for chunk in self._refined_script.chunks
        )

        return self._cached_formatted_refined_script
