from .youtube_key_point import YoutubeKeyPoint

from typing import List, Dict

class YoutubeKeyPointCollection:
    def __init__(self, youtube_url: str, key_points: List[YoutubeKeyPoint] = None):
        self._youtube_url = youtube_url
        self._key_points = key_points or []

    @property
    def youtube_url(self) -> str:
        return self._youtube_url

    @property
    def key_points(self) -> List[YoutubeKeyPoint]:
        return self._key_points

    def add_key_point(self, key_point: YoutubeKeyPoint):
        self._key_points.append(key_point)

    def to_dict(self) -> Dict[str, List[Dict[str, str]]]:
        return {
            "youtube_url": self._youtube_url,
            "key_points": [key_point.to_dict() for key_point in self._key_points]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, List[Dict[str, str]]]):
        key_points = [YoutubeKeyPoint.from_dict(item) for item in data.get("key_points", [])]
        return cls(youtube_url=data["youtube_url"], key_points=key_points)

    def __repr__(self) -> str:
        return f"YoutubeKeyPointCollection(youtube_url={self._youtube_url}, key_points_count={len(self._key_points)})"