from typing import Optional
from pymongo.results import UpdateResult, DeleteResult

from infrastructure.database.mongo_client import MongoDBClient
from domain import YoutubeKeyPointCollection, YoutubeKeyPoint


class YoutubeKeyPointCollectionRepository:
    def __init__(self, client: MongoDBClient, collection_name: str = "youtube_keypoint_collection"):
        self._client = client
        self._db = self._client.get_database()
        self._collection = self._db[collection_name]

    def save(self, collection: YoutubeKeyPointCollection) -> None:
        """핵심 키포인트 컬렉션을 MongoDB에 저장"""
        result: UpdateResult = self._collection.replace_one(
            {"youtube_url": collection.youtube_url},
            collection.to_dict(),
            upsert=True  # 문서가 없으면 삽입
        )
        return result.modified_count > 0 or result.upserted_id is not None

    def get(self, youtube_url: str) -> Optional[YoutubeKeyPointCollection]:
        """MongoDB에서 핵심 키포인트 컬렉션을 조회"""
        collection_data = self._collection.find_one({"youtube_url": youtube_url})
        if collection_data:
            return YoutubeKeyPointCollection.from_dict(collection_data)
        return None

    def delete(self, youtube_url: str) -> bool:
        """MongoDB에서 핵심 키포인트 컬렉션을 삭제"""
        result: DeleteResult = self._collection.delete_one({"youtube_url": youtube_url})
        return result.deleted_count > 0

    def add(self, youtube_url: str, key_point: YoutubeKeyPoint) -> bool:
        """핵심 키포인트를 특정 컬렉션에 추가"""
        update_result = self._collection.update_one(
            {"youtube_url": youtube_url},
            {"$push": {"key_points": key_point.to_dict()}}
        )
        return update_result.modified_count > 0

    def list_collections(self) -> list:
        """모든 유튜브 URL 목록 반환"""
        cursor = self._collection.find({}, {"youtube_url": 1, "_id": 0})
        return [doc["youtube_url"] for doc in cursor]