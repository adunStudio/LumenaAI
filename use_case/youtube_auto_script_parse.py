from domain import YouTubeVideoLink
from domain import YouTubeContent, ExecuteResult, ExecuteResultType, YoutubeScriptCollection
from infrastructure.repository import YoutubeContentRepository, YoutubeScriptCollectionRepository
from strategy import STTStrategyFactory, STTStrategyType
from use_case import YoutubeUseCase


# 2. 유튜브 링크로부터 DB에서 데이터를 가져와 유튜브 자동 생성된 스크립트로 최신화한다.
class YouTubeAutoScriptParse(YoutubeUseCase):
    def __init__(self,
                 content_repository: YoutubeContentRepository,
                 script_repository: YoutubeScriptCollectionRepository,
                 ):
        self._content_repository = content_repository
        self._script_repository = script_repository

    def execute(self, youtube_url: str, **kwargs) -> ExecuteResult:

        # 1. 유튜브 링크 검증
        try:
            youtube_video_link: YouTubeVideoLink = YouTubeVideoLink(youtube_url)
        except:
            return ExecuteResult(False, ExecuteResultType.INVALID_YOUTUBE_URL)


        # 2. DB 데이터 검사
        content: YouTubeContent = self._content_repository.find_by_url(youtube_video_link)
        if content is None:
            return ExecuteResult(False, ExecuteResultType.DATA_NOT_FOUND)


        # 3. 스크립트 파싱
        stt_strategy = STTStrategyFactory.create(STTStrategyType.AUTO_YOUTUBE)
        try:
            script = stt_strategy.transcribe_to_script(content.video_id)
        except:
            return ExecuteResult(False, ExecuteResultType.AUTO_SCRIPT_PARSE_FAIL)


        # 4. 저장소에 저장
        script_collection: YoutubeScriptCollection = self._script_repository.get(youtube_video_link.url)
        if script_collection is None:
            script_collection = YoutubeScriptCollection(youtube_video_link.url)

        script_collection.set_auto_script(script)
        success = self._script_repository.save(script_collection)
        if success:
            return ExecuteResult(True, ExecuteResultType.AUTO_SCRIPT_PARSE_SUCCESS)
        else:
            return ExecuteResult(False, ExecuteResultType.STORE_FAIL)
