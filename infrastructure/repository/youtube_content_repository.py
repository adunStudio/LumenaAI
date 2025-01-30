from pymongo.results import UpdateResult, DeleteResult

from infrastructure.database.mongo_client import MongoDBClient
from domain.youtube_content import YouTubeContent
from domain.youtube_video_link import YouTubeVideoLink


class YoutubeContentRepository:
    def __init__(self, client: MongoDBClient, collection_name: str = "youtube_content"):
        self._client = client
        self._db = self._client.get_database()
        self._collection = self._db[collection_name]

    def save(self, content: YouTubeContent) -> bool:
        result: UpdateResult = self._collection.replace_one(
            {"url": content.url.url},
            content.to_dict(),
            upsert=True  # 문서가 없으면 삽입
        )
        return result.modified_count > 0 or result.upserted_id is not None

    def find_by_url(self, url: YouTubeVideoLink) -> YouTubeContent:
        document = self._collection.find_one({"url": url.url})
        return YouTubeContent.from_dict(document) if document else None

    def find_all(self) -> [YouTubeContent]:
        documents = self._collection.find()
        return [YouTubeContent.from_dict(doc) for doc in documents]

    def find_without_script_auto(self) -> list[YouTubeContent]:
        documents = self._collection.find(
            {"$or": [{"script_auto": {"$exists": False}}, {"script_auto": None}]}
        )
        return [YouTubeContent.from_dict(doc) for doc in documents]

    def find_without_script(self) -> list[YouTubeContent]:
        documents = self._collection.find(
            {"$or": [{"script": {"$exists": False}}, {"script": None}]}
        )
        return [YouTubeContent.from_dict(doc) for doc in documents]

    def delete_by_url(self, url: str) -> bool:
        result: DeleteResult = self._collection.delete_one({"url": url})
        return result.deleted_count > 0
