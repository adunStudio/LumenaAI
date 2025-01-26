from pymongo import MongoClient
from typing import Optional


class MongoDBClient:
    def __init__(self, uri, database_name: str = "LumenaAI"):
        self._uri = uri
        self._database_name = database_name
        self._client = None

    def connect(self) -> None:
        if self._client is None:
            self._client = MongoClient(self._uri)
            print(f"Connected to MongoDB")

        return self

    def get_database(self):
        if self._client is None:
            raise ConnectionError("MongoDB client is not connected. Call `connect()` first.")
        return self._client[self._database_name]

    def close(self) -> None:
        if self._client:
            self._client.close()
            print("MongoDB connection closed.")
            self._client = None