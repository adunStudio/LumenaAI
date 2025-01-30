from infrastructure.repository import YoutubeChatRepository
from domain import YouTubeVideoLink, YoutubeChatSession

class YoutubeChatService:
    def __init__(self, vector_db, repository: YoutubeChatRepository):
        self._vector_db = vector_db
        self._repository = repository
        self._cached_session = {}

    def get_session(self, url):
        if self._cached_session.get(url) is not None:
            return self._cached_session.get(url)

        if YouTubeVideoLink.is_valid_youtube_link(url) is False:
            return None

        session = self._repository.get_session(url)
        if session is None:
            session = YoutubeChatSession(url)

        self._cached_session[url] = session

        return session

    # def add_message_to_session(self, session_id: str, sender: str, message: str):
    #     message_data = {"sender": sender, "message": message, "timestamp": datetime.now()}
    #     self.db.sessions.update_one(
    #         {"_id": session_id},
    #         {"$push": {"messages": message_data}}
    #     )
    #
    # def handle_user_message(self, session_id: str, user_message: str) -> str:
    #     # 과거 대화 기록 불러오기
    #     session = self.db.sessions.find_one({"_id": session_id})
    #     messages = session["messages"]
    #
    #     # RAG 기반 응답 생성
    #     context = "\n".join([f'{msg["sender"]}: {msg["message"]}' for msg in messages])
    #     response = self.chain.run({"context": context, "question": user_message})
    #
    #     # 응답 저장 및 반환
    #     self.add_message_to_session(session_id, "AI", response)
    #     return response