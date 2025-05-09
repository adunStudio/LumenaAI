import yt_dlp, os

from domain.youtube_video_link import YouTubeVideoLink
from domain import YouTubeContent, ExecuteResult, ExecuteResultType
from infrastructure.repository import YoutubeContentRepository
from use_case import YoutubeUseCase


# 1. 유튜브 링크로부터 데이터를 가져와 엔티티를 생성, 저장소에 저장한다.
class YouTubeParseAndStore(YoutubeUseCase):
    COOKIES_PATH: str = 'cookie.txt'

    def __init__(self, repository: YoutubeContentRepository):
        self._repository = repository

    def execute(self, youtube_url: str, **kwargs) -> ExecuteResult:
        print(os.path.abspath(YouTubeParseAndStore.COOKIES_PATH))

        # 1. 유튜브 링크 검증
        try:
            youtube_video_link = YouTubeVideoLink(youtube_url)
        except:
            return ExecuteResult(False, ExecuteResultType.INVALID_YOUTUBE_URL)


        # 2. 중복 검사
        if self._repository.find_by_url(youtube_video_link) is not None:
            return ExecuteResult(True, ExecuteResultType.DUPLICATE_CONTENT)


        # 3. 메타 데이터 가져오기
        try:
            metadata = self._fetch_metadata(youtube_video_link)
        except:
            return ExecuteResult(False, ExecuteResultType.INVALID_YOUTUBE_URL)


        # 4. YouTubeContent 엔티티 생성
        content = YouTubeContent(
            title=metadata['title'],
            channel=metadata['channel'],
            thumbnail=metadata['thumbnail'],
            url=youtube_video_link,
            description=metadata.get('description', ''),
            tags=metadata.get('tags', []),
            category=kwargs.get("category", '기타')
        )


        # 5. 저장소에 저장
        success = self._repository.save(content)
        if success:
            return ExecuteResult(True, ExecuteResultType.STORE_SUCCESS)
        else:
            return ExecuteResult(False, ExecuteResultType.STORE_FAIL)


    @staticmethod
    def _fetch_metadata(video_link: YouTubeVideoLink):
        ydl_opts = {
            'quiet': True,
            'cookiefile': YouTubeParseAndStore.COOKIES_PATH,
            'http_headers': {
                'Accept-Language': 'ko',  # HTTP 요청에 한국어 언어 설정
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_link.url, download=False)

            return {
                'title': info.get('title', 'Unknown Title'),
                'channel': info.get('channel', 'Unknown Channel'),
                'thumbnail': info.get('thumbnail', 'Unknown Thumbnail'),
                'url': info.get('original_url', 'Unknown Url'),
                'description': info.get('description', 'Unknown Description'),
                'tags': info.get('tags', [])
            }
