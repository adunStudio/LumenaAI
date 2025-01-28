from typing import List, Optional
from domain.youtube_content import YouTubeContent
from domain.youtube_video_link import YouTubeVideoLink
from infrastructure.repository import YouTubeContentRepository


class YouTubeContentService:
    def __init__(self, repository: YouTubeContentRepository):
        self._repository = repository

    def get_content_by_url(self, url: str) -> Optional[YouTubeContent]:
        youtube_video_url = YouTubeVideoLink(url)
        return self._repository.find_by_url(youtube_video_url)

    def list_all_content(self) -> List[YouTubeContent]:
        return self._repository.find_all()

    def update_category(self, url: str, new_category: str) -> bool:
        youtube_video_url = YouTubeVideoLink(url)
        content = self._repository.find_by_url(youtube_video_url)
        if not content:
            return False

        # 카테고리 업데이트
        content.set_category(new_category)
        return self._repository.save(content)

    # delete 할 일이 있을려나~ (데드코드 될듯)
    def delete_content_by_url(self, url: str) -> bool:
        youtube_video_url = YouTubeVideoLink(url)
        return self._repository.delete_by_url(youtube_video_url)
