from use_case import YoutubeUseCase

from domain.youtube_video_link import YouTubeVideoLink
from domain import YouTubeContent, ExecuteResult, ExecuteResultType
from infrastructure.repository import YouTubeContentRepository


# 5. 유튜브 스크립트를 자연스럽게 정제
class YouTubeScriptRefinement(YoutubeUseCase):
    def __init__(self, repository: YouTubeContentRepository):
        self._repository = repository

    def execute(self, youtube_url: str, **kwargs) -> ExecuteResult:
        # 1. 유튜브 링크 검증
        try:
            youtube_video_link = YouTubeVideoLink(youtube_url)
        except:
            return ExecuteResult(False, ExecuteResultType.INVALID_YOUTUBE_URL)


        # 2. DB 데이터 검사
        content: YouTubeContent = self._repository.find_by_url(youtube_video_link)
        if content is None:
            return ExecuteResult(False, ExecuteResultType.DATA_NOT_FOUND)


        # 3. 기존 스크립트 검사(유튜브 자동, 위스퍼)
        if (content.script_auto is None) and (content.script is None):
            return ExecuteResult(False, ExecuteResultType.SCRIPT_NOT_FOUND)

        