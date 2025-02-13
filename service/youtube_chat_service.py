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
from langchain.chains import RetrievalQA

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
                아래의 정보를 기반으로 질문에 답하세요.

                [유튜브 영상 제목]: {title}
                [유튜브 영상 설명]: {description}

                질문: {query}
                답변:""",
            input_variables=["title", "description", "query"]
        )

        # 🔥 RetrievalQA 체인 생성 (묻고 답하기 방식)
        # question_answer_chain = RetrievalQA.from_chain_type(
        #     llm=self._llm,
        #     retriever=retriever,
        #     chain_type="stuff",  # 검색된 문서를 한 번에 사용
        #     #chain_type_kwargs={"prompt": qa_prompt},
        #     combine_docs_chain_kwargs={"prompt": qa_prompt}
        # )

        test_chain = qa_prompt | self._llm

        # 질문 수행
        response = test_chain.invoke({
            "query": user_msg,
            "title": content.title,
            "description": content.description
        })

        answer = response['answer']

        chat_session = self.get_session(content.url.url)
        if chat_session is None:
            chat_session = YoutubeChatSession(content.url.url)

        chat_session.add_message(AdvancedHumanMessage(content=user_msg))
        chat_session.add_message(AdvancedAIMessage(content=answer))

        self._repository.save_session(chat_session)

        return answer