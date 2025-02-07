from typing import Optional

from pymongo.results import UpdateResult, DeleteResult

from infrastructure.database.mongo_client import MongoDBClient
from domain import YoutubeScriptCollection


class YoutubeScriptCollectionRepository:
    def __init__(self, client: MongoDBClient, collection_name: str = "youtube_script_collection"):
        self._client = client
        self._db = self._client.get_database()
        self._collection = self._db[collection_name]

    def save(self, script: YoutubeScriptCollection) -> bool:
        result: UpdateResult = self._collection.replace_one(
            {"youtube_url": script.youtube_url},
            script.to_dict(),
            upsert=True  # 문서가 없으면 삽입
        )
        return result.modified_count > 0 or result.upserted_id is not None

    def get(self, youtube_url: str) -> Optional[YoutubeScriptCollection]:
        script_data = self._collection.find_one({"youtube_url": youtube_url})
        if script_data:
            return YoutubeScriptCollection.from_dict(script_data)
        return None

    def delete(self, script: YoutubeScriptCollection) -> bool:
        result: DeleteResult = self._collection.delete_one({"youtube_url": script.youtube_url})
        return result.deleted_count > 0
