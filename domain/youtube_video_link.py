from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs


@dataclass(frozen=True)
class YouTubeVideoLink:
    raw_url: str
    _url: str = field(init=False, repr=False)

    def __post_init__(self):
        if not self.is_valid_youtube_link(self.raw_url):
            raise Exception(f"유효하지 않은 유튜브 링크입니다: {self.raw_url}")
        object.__setattr__(self, "_url", self.extract_video_link(self.raw_url))

    @property
    def url(self) -> str:
        return self._url

    @staticmethod
    def is_valid_youtube_link(url: str) -> bool:
        try:
            parsed_url = urlparse(url)
            if parsed_url.netloc not in ["www.youtube.com", "youtube.com", "youtu.be"]:
                return False

            query_params = parse_qs(parsed_url.query)
            # 유튜브 영상 ID가 포함된 경우만 True
            return "v" in query_params or parsed_url.netloc == "youtu.be"
        except Exception:
            return False

    @staticmethod
    def extract_video_link(url: str) -> str:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # youtu.be 단축 링크 처리
        if parsed_url.netloc == "youtu.be":
            video_id = parsed_url.path.lstrip("/")
            return f"https://www.youtube.com/watch?v={video_id}"

        # www.youtube.com 링크 처리
        video_id = query_params.get("v", [None])[0]
        if not video_id:
            raise Exception(f"유튜브 영상 ID를 찾을 수 없습니다: {url}")
        return f"https://www.youtube.com/watch?v={video_id}"

    def __str__(self) -> str:
        return self.url

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, YouTubeVideoLink):
            return False
        return self.url == other.url

    def __hash__(self) -> int:
        return hash(self.url)
