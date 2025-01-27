from domain.value_object.youtube_video_link import YouTubeVideoLink
from domain.entity import YouTubeContent, ExecuteResult, ExecuteResultType
from infrastructure.repository import YouTubeContentRepository
from application.strategy import STTStrategyFactory, STTStrategyType
from application.use_case import YoutubeUseCase


# 2. 유튜브 링크로부터 DB에서 데이터를 가져와 유튜브 자동 생성된 스크립트로 최신화한다.
class YouTubeAutoScriptParse(YoutubeUseCase):
    def __init__(self, repository: YouTubeContentRepository):
        self._repository = repository

    def execute(self, youtube_url: str) -> ExecuteResult:

        # 1. 유튜브 링크 검증
        try:
            youtube_video_link: YouTubeVideoLink = YouTubeVideoLink(youtube_url)
        except:
            return ExecuteResult(False, ExecuteResultType.INVALID_YOUTUBE_URL)


        # 2. DB 데이터 검사
        content: YouTubeContent = self._repository.find_by_url(youtube_video_link)
        if content is None:
            return ExecuteResult(False, ExecuteResultType.DATA_NOT_FOUND)


        # 3. 스크립트 파싱
        stt_strategy = STTStrategyFactory.create(STTStrategyType.AUTO_YOUTUBE)
        try:
            script_auto = stt_strategy.transcribe_to_script(content.video_id)
        except:
            return ExecuteResult(False, ExecuteResultType.AUTO_SCRIPT_PARSE_FAIL)


        # 4. 저장소에 저장
        content.set_script_auto(script_auto)
        self._repository.save(content)
        success = self._repository.save(content)
        if success:
            return ExecuteResult(True, ExecuteResultType.STORE_SUCCESS)
        else:
            return ExecuteResult(False, ExecuteResultType.STORE_FAIL)
