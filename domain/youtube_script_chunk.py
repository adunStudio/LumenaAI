class YouTubeScriptChunk:
    def __init__(self, timestamp: tuple, text: str):
        self._timestamp = timestamp
        self._text = text

    @property
    def timestamp(self) -> tuple:
        return self._timestamp

    @property
    def start_time(self) -> float:
        return self._timestamp[0]

    @property
    def formatted_start_time(self) -> str:
        minutes, seconds = divmod(int(self.start_time), 60)  # 초를 분과 초로 변환
        return f"{minutes}:{seconds:02}"  # 두 자리 초로 포맷

    @property
    def end_time(self) -> float:
        return self._timestamp[1]

    @property
    def text(self) -> str:
        return self._text

    def to_dict(self) -> dict:
        return {
            "timestamp": self._timestamp,
            "text": self._text,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            timestamp=tuple(data["timestamp"]),
            text=data["text"]
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, YouTubeScriptChunk):
            return False
        return self._timestamp == other.timestamp and self._text == other.text
