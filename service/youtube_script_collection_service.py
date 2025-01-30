from infrastructure.repository import YoutubeScriptCollectionRepository
from domain import YouTubeVideoLink, YoutubeScriptCollection

class YoutubeScriptCollectionService:
    def __init__(self, repository: YoutubeScriptCollectionRepository):
        self._repository = repository
        self._cached_script_collection = {}

    def get_script_collection(self, url):
        if self._cached_script_collection.get(url) is not None:
            return self._cached_script_collection.get(url)

        if YouTubeVideoLink.is_valid_youtube_link(url) is False:
            return None

        script_collection = self._repository.get(url)
        if script_collection is None:
            script_collection = YoutubeScriptCollection(url)

        self._cached_script_collection[url] = script_collection

        return script_collection