from infrastructure.repository import YoutubeChatRepository
from domain import YouTubeVideoLink, YoutubeChatSession, YouTubeScript, YouTubeContent
from domain import AdvancedAIMessage, AdvancedHumanMessage

from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

import shutil
import os

class YoutubeChatService:
    def __init__(self, embedding, llm: BaseLLM, repository: YoutubeChatRepository):
        self._embedding = embedding
        self._llm = llm
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

    def question(self, content: YouTubeContent, script: YouTubeScript,  user_msg: str):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.split_text(script.script)

        persist_dir = "./chroma_data"

        vectorstore = Chroma(
            embedding_function=self._embedding,
            persist_directory=persist_dir,
            collection_name=content.video_id
        )

        if vectorstore is None:
            vectorstore = Chroma.from_texts(
                texts=texts,
                embedding=self._embedding,
                persist_directory=persist_dir,
                collection_name=content.video_id
            )

        retriever = vectorstore.as_retriever()

        system_prompt = ("""
                    주어진 유튜브 영상의 설명과 스크립트 맥락을 사용하여 질문에 답하세요.
                    답을 모르면 모른다고 하세요.

                    [유튜브 영상 설명]:
                    {description}

                    [스크립트 맥락]:
                    {context}
                    """.format(description=content.description, context="{context}"))

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )

        question_answer_chain = create_stuff_documents_chain(self._llm, prompt)
        chain = create_retrieval_chain(retriever, question_answer_chain)

        response = chain.invoke({"input": user_msg})
        answer = response['answer']

        chat_session = self.get_session(content.url.url)
        if chat_session is None:
            chat_session = YoutubeChatSession(content.url.url)

        chat_session.add_message(AdvancedHumanMessage(content=user_msg))
        chat_session.add_message(AdvancedAIMessage(content=answer))

        self._repository.save_session(chat_session)

        return answer

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