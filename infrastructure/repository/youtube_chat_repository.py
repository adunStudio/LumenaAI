from typing import Optional

from infrastructure.database.mongo_client import MongoDBClient
from domain import YoutubeChatSession, AdvancedMessageType

class YoutubeChatRepository:
    def __init__(self, client: MongoDBClient, collection_name: str = "youtube_chat"):
        self._client = client
        self._db = self._client.get_database()
        self._collection = self._db[collection_name]

    def save_session(self, session: YoutubeChatSession) -> None:
        session_data = session.to_dict()
        self._collection.update_one(
            {"youtube_url": session.youtube_url},
            {"$set": session_data},
            upsert=True
        )

    def get_session(self, youtube_url: str) -> Optional[YoutubeChatSession]:
        session_data = self._collection.find_one({"youtube_url": youtube_url})
        if session_data:
            return YoutubeChatSession.from_dict(session_data)
        return None

    def delete_session(self, youtube_url: str) -> bool:
        result = self._collection.delete_one({"youtube_url": youtube_url})
        return result.deleted_count > 0

    def add_message_to_session(self, youtube_url: str, message: AdvancedMessageType) -> bool:
        update_result = self._collection.update_one(
            {"youtube_url": youtube_url},
            {"$push": {"messages": message.to_dict()}}
        )
        return update_result.modified_count > 0

    def list_sessions(self) -> list:
        cursor = self._collection.find({}, {"youtube_url": 1, "_id": 0})
        return [doc["youtube_url"] for doc in cursor]