from infrastructure.repository import YoutubeChatRepository
from domain import YouTubeVideoLink, YoutubeChatSession, YouTubeScript, YouTubeContent
from domain import AdvancedAIMessage, AdvancedHumanMessage

from langchain_core.messages import AIMessage, HumanMessage
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import RetrievalQA

import shutil
import os

class YoutubeChatService:
    def __init__(self, embedding, llm0: BaseLLM, llm1: BaseLLM,  repository: YoutubeChatRepository):
        self._embedding = embedding
        self._llm0 = llm0
        self._llm1 = llm1
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

    def question(self, content: YouTubeContent, script: YouTubeScript,  user_msg: str, index: int):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=300)
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

        # 📝 Q&A 형식의 프롬프트로 변경
        qa_prompt = PromptTemplate(
            template="""당신은 유튜브 영상의 내용을 분석하는 AI입니다.
            아래의 정보를 기반으로 질문에 답변하세요.

            [유튜브 영상 제목]: {title}
            [유튜브 영상 설명]: {description}
            [참고 문맥]: {context}

            답변은 한 문장으로 작성하세요. 질문을 반복하거나 추가 정보를 제공하지 마세요.

            질문: {query}
            답변:\n\n""",
            input_variables=["title", "description", "context", "query"]
        )

        print(index)
        if index == 0:
            test_chain = qa_prompt | self._llm0
        else:
            test_chain = qa_prompt | self._llm1

        # 🔥 리트리버에서 검색된 문서 가져오기
        retrieved_docs = retriever.get_relevant_documents(user_msg)

        # 🔥 검색된 문서들을 문자열로 변환
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])


        # 질문 수행
        response = test_chain.invoke({
            "query": user_msg,
            "title": content.title,
            "description": content.description,
            "context": context
        })

        if isinstance(response, AIMessage):
            answer = response.content
        else:
            answer = response

        chat_session = self.get_session(content.url.url)
        if chat_session is None:
            chat_session = YoutubeChatSession(content.url.url)

        chat_session.add_message(AdvancedHumanMessage(content=user_msg))
        chat_session.add_message(AdvancedAIMessage(content=answer))

        self._repository.save_session(chat_session)

        return answer