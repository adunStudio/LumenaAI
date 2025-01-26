from app import AppContainer
from application.service import YouTubeContentService


class LumenaAIApp:
    def __init__(self):
        self._container = AppContainer()
        self._youtube_service: YouTubeContentService = self._container.youtube_service()

        self._cached_youtube_contents = None
        self._selected_youtube_content = None

        self._view_mode = 'large'

    def get_all_youtube_contents(self):
        if self._cached_youtube_contents is not None:
            return self._cached_youtube_contents

        self._cached_youtube_contents = self._youtube_service.list_all_content()
        return self._cached_youtube_contents

    def select_youtube_content(self, youtube_content):
        self._selected_youtube_content = youtube_content

    @property
    def selected_youtube_content(self):
        return self._selected_youtube_content

    def set_view_mode(self, mode):
        self._view_mode = mode

    @property
    def view_mode(self):
        return self._view_mode
