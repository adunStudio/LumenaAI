import yt_dlp
import os

from domain.youtube_video_link import YouTubeVideoLink
from domain.youtube_content import YouTubeContent
from infrastructure.repository import YouTubeContentRepository


# 유튜브 링크로부터 데이터를 가져와 엔티티를 생성, 저장소에 저장하고 오디오를 저장한다.
class YouTubeContentDownloadAndStore:
    PATH = 'downloads/'

    def __init__(self, repository: YouTubeContentRepository):
        self._repository = repository

    def execute(self, youtube_url: str, category: str = '', custom_folder:str=None) -> bool:
        # 1. 유튜브 링크 검증
        youtube_video_link = YouTubeVideoLink(youtube_url)

        if self._repository.find_by_url(youtube_video_link) is not None:
            print("데이터가 이미 존재합니다.")
            success = True

            content = self._repository.find_by_url(youtube_video_link)
        else:
            # 2. 메타 데이터 가져오기
            metadata = self._fetch_metadata(youtube_video_link)

            # 3. YouTubeContent 엔티티 생성
            content = YouTubeContent(
                title=metadata['title'],
                channel=metadata['channel'],
                thumbnail=metadata['thumbnail'],
                url=youtube_video_link,
                description=metadata.get('description', ''),
                tags=metadata.get('tags', []),
                category=category
            )

            # 4. 저장소에 저장
            success = self._repository.save(content)
            if success:
                print('데이터 저장 완료')

        # 5. 오디오 파일 다운로드
        if success:
            self._download_audio(youtube_video_link, content.title, content.category, custom_folder)

        return success

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

    @staticmethod
    def _download_audio(video_link: YouTubeVideoLink, file_name: str, category: str, custom_folder=None) -> None:
        download_folder = os.path.join(YouTubeContentDownloadAndStore.PATH, category)

        if custom_folder is not None:
            download_folder = os.path.join(custom_folder, category)

        print(download_folder)

        os.makedirs(download_folder, exist_ok=True)

        file_path = os.path.join(download_folder, f"{file_name}.mp3")

        # 파일 중복 검사
        if os.path.exists(file_path):
            print(f"파일이 이미 존재합니다: {file_path}")
            return

        # yt-dlp 옵션 설정
        ydl_opts = {
            'format': 'bestaudio/best',  # 최적의 오디오 품질 선택
            'outtmpl': os.path.join(download_folder, f"{file_name}.%(ext)s"),  # 파일 저장 경로
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',  # 오디오 추출
                    'preferredcodec': 'mp3',  # MP3로 변환
                    'preferredquality': '192',  # 오디오 품질
                }
            ],
            'quiet': True,  # 다운로드 중 출력 최소화
        }

        try:
            # yt-dlp를 사용해 다운로드
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"오디오 다운로드 중: {video_link.url}")
                ydl.download([video_link.url])
            print(f"오디오가 성공적으로 다운로드되어 저장되었습니다: {file_path}")
        except Exception as e:
            print(f"오디오 다운로드 실패: {e}")
            raise
