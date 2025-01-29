from domain import YouTubeVideoLink
from domain import YouTubeContent, ExecuteResult, ExecuteResultType
from infrastructure.repository import YouTubeContentRepository
from strategy import STTStrategyFactory, STTStrategyType
from use_case import YoutubeUseCase

from langchain.llms.base import BaseLLM


# 2. 유튜브 링크로부터 DB에서 데이터를 가져와 타임라인 요약을 생성한다.
class YouTubeGenerateTimelineSummary(YoutubeUseCase):
    def __init__(self, repository: YouTubeContentRepository, llm: BaseLLM):
        self._repository = repository
        self._llm = llm
        self._chain = None

    def execute(self, youtube_url: str, **kwargs) -> ExecuteResult:

        # 1. 유튜브 링크 검증
        try:
            youtube_video_link: YouTubeVideoLink = YouTubeVideoLink(youtube_url)
        except:
            return ExecuteResult(False, ExecuteResultType.INVALID_YOUTUBE_URL)


        # 2. DB 데이터 검사
        content: YouTubeContent = self._repository.find_by_url(youtube_video_link)
        if content is None:
            return ExecuteResult(False, ExecuteResultType.DATA_NOT_FOUND)


        # 3. 스크립트 검사
        if content.script is None:
            return ExecuteResult(False, ExecuteResultType.SCRIPT_NOT_FOUND)
