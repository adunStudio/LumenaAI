import yt_dlp
import os

from domain.value_object import YouTubeVideoLink, YouTubeScript, YouTubeScriptChunk
from domain.entity import YouTubeContent
from infrastructure.repository import YouTubeContentRepository
from application.strategy import STTStrategy

import time


# 유튜브 콘텐츠의 스크립트를 최신화한다.
class YouTubeContentSTTScriptUpdate:
    PATH = 'downloads/'

    def __init__(self, repository: YouTubeContentRepository, stt_strategy: STTStrategy):
        self._repository = repository
        self._stt_strategy = stt_strategy

    def execute(self, youtube_content: YouTubeContent, custom_folder: str = None) -> bool:

        start_time = time.time()

        if custom_folder is not None:
            download_folder = os.path.join(custom_folder, youtube_content.category)
        else:
            download_folder = os.path.join(YouTubeContentSTTScriptUpdate.PATH, youtube_content.category)

        file_path = os.path.join(download_folder, f"{youtube_content.title}.mp3")

        # 파일 중복 검사
        if not os.path.exists(file_path):
            print(f"파일이 존재 하지 않습니다: {file_path}")
            return False

        try:
            stt_result = self._stt_strategy.transcribe(file_path)

        except:
            print(f"STT 실패: {file_path}")
            return False

        youtube_script = YouTubeScript(
            script=stt_result["text"],
            chunks=[
                YouTubeScriptChunk.from_dict(chunk)
                for chunk in stt_result["chunks"]
            ],
        )

        youtube_content.set_script(youtube_script)

        result = self._repository.save(youtube_content)

        if result:
            end_time = time.time()
            print(f'스크립트 저장 성공({youtube_content.title}) 수행 시간: {end_time - start_time:.4f}초')
        else:
            print(f'스크립트 저장 실패({youtube_content.title})')

        return result