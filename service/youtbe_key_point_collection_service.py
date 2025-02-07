from infrastructure.repository import YoutubeKeyPointCollectionRepository
from domain import YouTubeVideoLink, YoutubeKeyPointCollection, YoutubeKeyPoint


class YoutubeKeyPointCollectionService:
    def __init__(self, repository: YoutubeKeyPointCollectionRepository):
        self._repository = repository
        self._cached_key_point_collection = {}

    def get_collection(self, url):
        if self._cached_key_point_collection.get(url) is not None:
            return self._cached_key_point_collection.get(url)

        if YouTubeVideoLink.is_valid_youtube_link(url) is False:
            return None

        key_point_collection = self._repository.get(url)
        if key_point_collection is None:
            key_point_collection = YoutubeKeyPointCollection(url)

        self._cached_key_point_collection[url] = key_point_collection

        return key_point_collection