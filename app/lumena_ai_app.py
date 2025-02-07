from app import AppContainer
from service import YoutubeContentService, YoutubeScriptCollectionService, YoutubeKeyPointCollectionService, YoutubeChatService
from use_case import YouTubeParseAndStore
from use_case import YouTubeAutoScriptParse
from use_case import YouTubeAudioDownload
from use_case import YouTubeAudioSTT
from use_case import YouTubeScriptRefinement
from use_case import YouTubeGenerateTimelineSummary
from use_case import YouTubeGenerateKeyPoint

class LumenaAIApp:
    def __init__(self):
        print("LumenaAIApp")

        self._container = AppContainer()

        # 서비스
        self._youtube_content_service: YoutubeContentService = self._container.youtube_content_service()
        self._youtube_script_service: YoutubeScriptCollectionService = self._container.youtube_script_collection_service()
        self._youtube_key_point_service: YoutubeKeyPointCollectionService = self._container.youtube_key_point_service()
        self._youtube_chat_service: YoutubeChatService = self._container.youtube_chat_service()

        # 새로운 지식 유즈-케이스
        self._youtube_parse_and_store: YouTubeParseAndStore = self._container.youtube_parse_and_store()
        self._youtube_auto_script_parse: YouTubeAutoScriptParse = None # self._container.youtube_auto_script_parse()
        self._youtube_audio_download: YouTubeAudioDownload = None #self._container.youtube_audio_download()
        self._youtube_audio_stt: YouTubeAudioSTT = None #self._container.youtube_audio_stt()
        self._youtube_script_refinement: YouTubeScriptRefinement = self._container.youtube_script_refinement()
        self._youtube_generate_timeline_summary: YouTubeGenerateTimelineSummary = self._container.youtube_generate_timeline_summary()
        self._youtube_generate_key_point: YouTubeGenerateKeyPoint = self._container.youtube_generate_key_point()


        # 캐싱
        self._cached_youtube_contents = None

        # 프로퍼티
        self._selected_youtube_content = None
        self._selected_youtube_chat = None
        self._selected_youtube_key_point_collection = None
        self._selected_youtube_script_collection = None

        self._view_mode = 'large'
        self._search_query = ''
        self._page = 'main' # or add


    def cache_clear(self):
        self._cached_youtube_contents = None

    def get_all_youtube_contents(self):
        if self._cached_youtube_contents is not None:
            return self._cached_youtube_contents

        self._cached_youtube_contents = self._youtube_content_service.list_all_content()
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
               or self._search_query in content.channel.lower()
               or any(self._search_query in tag.lower() for tag in content.tags)
        ]

        return all_youtube_contents


    def question(self, user_msg):
        return self._youtube_chat_service.question(
            self._selected_youtube_content,
            self._selected_youtube_script_collection.refined_script,
            user_msg
        )

    @property
    def search_query(self):
        return self._search_query

    def set_search_query(self, search_query):
        self._search_query = search_query

    def select_youtube_content(self, youtube_content):
        if self._selected_youtube_content == youtube_content:
            return

        self._selected_youtube_content = youtube_content

        url: str = youtube_content.url.url
        self._selected_youtube_chat = self._youtube_chat_service.get_session(url)
        self._selected_youtube_key_point_collection = self._youtube_key_point_service.get_collection(url)
        self._selected_youtube_script_collection = self._youtube_script_service.get_script_collection(url)

    @property
    def script_collection(self):
        return self._selected_youtube_script_collection

    @property
    def key_point_collection(self):
        return self._selected_youtube_key_point_collection

    @property
    def chat(self):
        return self._selected_youtube_chat

    def select_youtube_content_by_url(self, url):
        content = self._youtube_content_service.get_content_by_url(url)
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
    def first_parse_and_store(self, url: str):
        return self._youtube_parse_and_store.execute(url)

    def second_auto_script_parse(self, url: str):
        if self._youtube_auto_script_parse is None:
            self._youtube_auto_script_parse = self._container.youtube_auto_script_parse()

        return self._youtube_auto_script_parse.execute(url)

    def third_audio_download(self, url: str):
        if self._youtube_audio_download is None:
            self._youtube_audio_download = self._container.youtube_audio_download()

        return self._youtube_audio_download.execute(url)

    def fourth_audio_stt(self, url: str):
        if self._youtube_audio_stt is None:
            self._youtube_audio_stt = self._container.youtube_audio_stt()

        return self._youtube_audio_stt.execute(url)

    def fifth_script_refinement(self, url: str):
        return self._youtube_script_refinement.execute(url)

    def six_generate_timeline_summary(self, url: str):
        return self._youtube_generate_timeline_summary.execute(url)

    def seven_generate_key_point(self, url: str):
        return self._youtube_generate_key_point.execute(url)
