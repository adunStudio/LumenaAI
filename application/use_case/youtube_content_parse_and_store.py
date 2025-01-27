import yt_dlp

from domain.value_object.youtube_video_link import YouTubeVideoLink
from domain.entity import YouTubeContent, ExecuteResult, ExecuteResultType
from infrastructure.repository import YouTubeContentRepository


# 1. 유튜브 링크로부터 데이터를 가져와 엔티티를 생성, 저장소에 저장한다.
class YouTubeContentParseAndStore:

    def __init__(self, repository: YouTubeContentRepository):
        self._repository = repository

    def execute(self, youtube_url: str, category: str = '기타') -> ExecuteResult:
        # 1. 유튜브 링크 검증
        try:
            youtube_video_link = YouTubeVideoLink(youtube_url)
        except:
            return ExecuteResult(False, ExecuteResultType.INVALID_YOUTUBE_URL)


        # 2. 중복 검사
        if self._repository.find_by_url(youtube_video_link) is not None:
            return ExecuteResult(False, ExecuteResultType.DUPLICATE_CONTENT)


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
            category=category
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
