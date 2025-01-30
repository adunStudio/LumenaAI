from domain import YouTubeVideoLink
from domain import YouTubeContent, ExecuteResult, ExecuteResultType, YoutubeScriptCollection
from infrastructure.repository import YoutubeContentRepository, YoutubeScriptCollectionRepository
from strategy import STTStrategy
from use_case import YoutubeUseCase

import os


# 4. 유튜브 오디오 -> STT -> 저장
class YouTubeAudioSTT(YoutubeUseCase):
    PATH = 'downloads/'

    def __init__(self,
                 content_repository: YoutubeContentRepository,
                 script_repository: YoutubeScriptCollectionRepository,
                 stt_strategy: STTStrategy):

        self._content_repository = content_repository
        self._script_repository = script_repository
        self._stt_strategy = stt_strategy

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

        script_collection: YoutubeScriptCollection = self._script_repository.get(youtube_video_link.url)
        if script_collection is not None and script_collection.whisper_script is not None:
            return ExecuteResult(True, ExecuteResultType.STT_SUCCESS)


        # 3. 파일 검사
        download_folder = os.path.join(kwargs.get("download_path", YouTubeAudioSTT.PATH), content.channel)
        file_name = str(content.video_id)

        file_path = os.path.join(download_folder, f'{file_name}.mp3')
        if not os.path.exists(file_path):
            return ExecuteResult(False, ExecuteResultType.AUDIO_NOT_EXIST)


        # 4. STT
        try:
            script = self._stt_strategy.transcribe_to_script(file_path)
        except:
            return ExecuteResult(False, ExecuteResultType.STT_FAIL)


        # 5. 저장소에 저장
        if script_collection is None:
            script_collection = YoutubeScriptCollection(youtube_video_link.url)

        script_collection.set_whisper_script(script)
        success = self._script_repository.save(script_collection)
        if success:
            return ExecuteResult(True, ExecuteResultType.STT_SUCCESS)
        else:
            return ExecuteResult(False, ExecuteResultType.STORE_FAIL)
