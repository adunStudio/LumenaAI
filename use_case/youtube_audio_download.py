from domain.youtube_video_link import YouTubeVideoLink
from domain import YouTubeContent, ExecuteResult, ExecuteResultType
from infrastructure.repository import YoutubeContentRepository
from use_case import YoutubeUseCase

import os
import yt_dlp


# 3. 유튜브 링크로부터 오디오를 다운로드한다..
class YouTubeAudioDownload(YoutubeUseCase):
    PATH = 'downloads/'
    COOKIES_PATH: str = 'cookie.txt'

    def __init__(self, repository: YoutubeContentRepository):
        self._repository = repository

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


        # 3. 폴더 생성
        download_folder = os.path.join(kwargs.get("download_path", YouTubeAudioDownload.PATH), content.channel)
        os.makedirs(download_folder, exist_ok=True)


        # 4. 파일 중복 검사
        file_name = str(content.video_id)
        file_path = os.path.join(download_folder, f'{file_name}.mp3')
        if os.path.exists(file_path):
            return ExecuteResult(True, ExecuteResultType.AUDIO_DOWNLOAD_SUCCESS)


        # 5. yt-dlp 옵션 설정
        ydl_opts = {
            'format': 'bestaudio/best',  # 최적의 오디오 품질 선택
            'outtmpl': os.path.join(download_folder, f"{file_name}.%(ext)s"),  # 파일 저장 경로
            'cookies': YouTubeAudioDownload.COOKIES_PATH,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',  # 오디오 추출
                    'preferredcodec': 'mp3',      # MP3로 변환
                    'preferredquality': '192',    # 오디오 품질
                }
            ],
            'quiet': True,  # 다운로드 중 출력 최소화
        }


        # 6. yt-dlp를 사용해 다운로드
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"오디오 다운로드 중: {youtube_video_link.url}")
                ydl.download([youtube_video_link.url])
            print(f"오디오가 성공적으로 다운로드되어 저장되었습니다: {file_path}")
            return ExecuteResult(True, ExecuteResultType.AUDIO_DOWNLOAD_SUCCESS)

        except Exception as e:
            print(f"오디오 다운로드 실패: {e}")
            return ExecuteResult(False, ExecuteResultType.AUDIO_DOWNLOAD_FAIL)


