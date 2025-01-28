from .youtube_script_chunk import YouTubeScriptChunk

from typing import List


class YouTubeScript:
    def __init__(self, script: str, chunks: List[YouTubeScriptChunk]):
        self._script = script
        self._chunks = chunks

    @property
    def script(self) -> str:
        return self._script

    @property
    def chunks(self) -> List[YouTubeScriptChunk]:
        return self._chunks

    def to_dict(self) -> dict:
        return {
            "text": self._script,
            "chunks": [chunk.to_dict() for chunk in self._chunks],
        }

    @classmethod
    def from_dict(cls, data: dict):
        chunks = [YouTubeScriptChunk.from_dict(chunk) for chunk in data["chunks"]]
        return cls(script=data["text"], chunks=chunks)

    def __repr__(self) -> str:
        chunk_preview = ", ".join(
            [f"({chunk.start_time}-{chunk.end_time}: {chunk.text[:15]}...)" for chunk in self._chunks[:3]]
        )
        return (
            f"YouTubeScript("
            f"script='{self._script[:50]}...', "  # 전체 스크립트의 앞 50자만 표시
            f"chunks=[{chunk_preview}, ...] ({len(self._chunks)} chunks)"
            f")"
        )
