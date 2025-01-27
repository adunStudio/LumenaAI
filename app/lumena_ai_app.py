from app import AppContainer
from application.service import YouTubeContentService


class LumenaAIApp:
    def __init__(self):
        print("LumenaAIApp")
        self._container = AppContainer()
        self._youtube_service: YouTubeContentService = self._container.youtube_service()

        self._cached_youtube_contents = None
        self._selected_youtube_content = None

        self._view_mode = 'large'
        self._search_query = ''

    def get_all_youtube_contents(self):
        if self._cached_youtube_contents is not None:
            return self._cached_youtube_contents

        self._cached_youtube_contents = self._youtube_service.list_all_content()
        return self._cached_youtube_contents

    def get_search_youtube_contents(self):
        all_list = self.get_all_youtube_contents()

        if self._search_query == '':
            return all_list

        all_youtube_contents = [
            content
            for content in all_list
            if self._search_query in content.title.lower()
               or self._search_query in content.description.lower()
               or any(self._search_query in tag.lower() for tag in content.tags)
        ]

        return all_youtube_contents

    @property
    def search_query(self):
        return self._search_query

    def set_search_query(self, search_query):
        self._search_query = search_query

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
