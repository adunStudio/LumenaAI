from app import AppContainer
from application.service import YouTubeContentService
from application.use_case import YouTubeContentParseAndStore
from application.use_case import YouTubeContentAutoScriptParse

class LumenaAIApp:
    def __init__(self):
        print("LumenaAIApp")
        self._container = AppContainer()
        self._youtube_service: YouTubeContentService = self._container.youtube_service()
        self._youtube_parse_and_store: YouTubeContentParseAndStore = self._container.youtube_parse_and_store()
        self._youtube_auto_script_parse: YouTubeContentAutoScriptParse = self._container.youtube_auto_script_parse()

        self._cached_youtube_contents = None
        self._selected_youtube_content = None

        self._view_mode = 'large'
        self._search_query = ''
        self._page = 'main' # or add


    def cache_clear(self):
        self._cached_youtube_contents = None

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

    def select_youtube_content_by_url(self, url):
        content = self._youtube_service.get_content_by_url(url)
        self.select_youtube_content(content)

    @property
    def selected_youtube_content(self):
        return self._selected_youtube_content

    @property
    def page(self):
        return self._page

    def set_page(self, page):
        self._page = page

    def set_view_mode(self, mode):
        self._view_mode = mode

    @property
    def view_mode(self):
        return self._view_mode


    ### 유튜브 분석 & 요약 유즈케이스
    def first_parse_and_store(self, url):
        return self._youtube_parse_and_store.execute(url)

    def second_auto_script_parse(self, url):
        return self._youtube_auto_script_parse.execute(url)
