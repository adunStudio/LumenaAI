from .youtube_key_point import YoutubeKeyPoint

from typing import List, Dict

class YoutubeKeyPointCollection:
    def __init__(self, youtube_url: str, key_points: List[YoutubeKeyPoint] = None, key_points_local1: List[YoutubeKeyPoint] = None):
        self._youtube_url = youtube_url
        self._key_points = key_points or []
        self._key_points_local1 = key_points_local1 or []

    @property
    def youtube_url(self) -> str:
        return self._youtube_url

    @property
    def key_points(self) -> List[YoutubeKeyPoint]:
        return self._key_points

    @property
    def key_points_local1(self) -> List[YoutubeKeyPoint]:
        return self._key_points_local1

    def add_key_point(self, key_point: YoutubeKeyPoint):
        self._key_points.append(key_point)

    def add_key_point_local1(self, key_point: YoutubeKeyPoint):
        self._key_points_local1.append(key_point)

    def to_dict(self) -> Dict[str, List[Dict[str, str]]]:
        return {
            "youtube_url": self._youtube_url,
            "key_points": [key_point.to_dict() for key_point in self._key_points],
            "key_points_local1": [key_point.to_dict() for key_point in self._key_points_local1]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, List[Dict[str, str]]]):
        key_points = [YoutubeKeyPoint.from_dict(item) for item in data.get("key_points", [])]
        key_points_local1 = [YoutubeKeyPoint.from_dict(item) for item in data.get("key_points_local1", [])]
        return cls(youtube_url=data["youtube_url"], key_points=key_points, key_points_local1=key_points_local1)

    def __repr__(self) -> str:
        return f"YoutubeKeyPointCollection(youtube_url={self._youtube_url}, key_points_count={len(self._key_points)}, key_points_local1_count={len(self._key_points_local1)})"