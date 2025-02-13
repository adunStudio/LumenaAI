from domain import YouTubeVideoLink, YouTubeContent
from domain import ExecuteResult, ExecuteResultType
from domain import YoutubeTimelineSummary, YoutubeTimelineSection
from domain import YoutubeKeyPointCollection, YoutubeKeyPoint
from infrastructure.repository import YoutubeContentRepository, YoutubeKeyPointCollectionRepository
from use_case import YoutubeUseCase

from typing import List
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate


# 2. 유튜브 링크로부터 DB에서 데이터를 가져와 타임라인 요약을 생성한다.
class YouTubeGenerateKeyPointLocal(YoutubeUseCase):
    def __init__(self, content_repository: YoutubeContentRepository, key_point_collection_repository: YoutubeKeyPointCollectionRepository, llm: BaseLLM):
        self._content_repository = content_repository
        self._key_point_collection_repository = key_point_collection_repository
        self._llm = llm
        self._chain = None

    def execute(self, youtube_url: str, **kwargs) -> ExecuteResult:

        # 1. 유튜브 링크 검증
        try:
            youtube_video_link: YouTubeVideoLink = YouTubeVideoLink(youtube_url)
        except:
            return ExecuteResult(False, ExecuteResultType.INVALID_YOUTUBE_URL)


        # 2. DB 데이터 검사
        content: YouTubeContent = self._content_repository.find_by_url(youtube_video_link)
        if content is None:
            return ExecuteResult(False, ExecuteResultType.DATA_NOT_FOUND)

        url = youtube_video_link.url

        key_point_collection: YoutubeKeyPointCollection = self._key_point_collection_repository.get(url)

        if key_point_collection is None:
            return ExecuteResult(False, ExecuteResultType.KEY_POINT_NOT_FOUND)



        # 3. 타임라인 검사
        if content.timeline_summary is None:
            return ExecuteResult(False, ExecuteResultType.TIMELINE_SUMMARY_NOT_FOUND)


        # 4. LLM 체인 생성
        if self._chain is None:
            self._make_chain()


        # 5. 입력 데이터 생성
        summary: YoutubeTimelineSummary = content.timeline_summary

        summary_texts = f"{summary.text}\n"
        for section in summary.sections:
            summary_texts = summary_texts + '\n'
            for text in section.texts:
                summary_texts = summary_texts + f'- {text}\n'

        input_data = {
            "summary": summary_texts
        }


        # 6. 체인 호출 (2회 시도)
        chain_success = False
        for i in range(0, 2):
            try:
                response = self._chain.invoke(input_data)
                chain_success = True
                break
            except Exception as e:
                print(e)
                print('[youtube_generate_key_point] 체인 호출')

        if chain_success is False:
            return ExecuteResult(False, ExecuteResultType.KEY_POINT_FAIL)


        # 7. 핵심 용어 저장소에 저장
        for kp in response.key_points:
            key_point_collection.add_key_point_local1(kp)

        success = self._key_point_collection_repository.save(key_point_collection)
        if success:
            return ExecuteResult(True, ExecuteResultType.KEY_POINT_SUCCESS)
        else:
            return ExecuteResult(False, ExecuteResultType.STORE_FAIL)

    def _make_chain(self):
        # 1. 출력 파서
        key_point_parser = PydanticOutputParser(pydantic_object=YoutubeKeyPointCollectionModel)

        # 2. 프롬프트 템플릿
        key_point_prompt_template = PromptTemplate(
            partial_variables={'output_format': key_point_parser.get_format_instructions()},
            input_variables=["summary"],
            template="""
다음은 유튜브 타임라인 요약 문서입니다. 이 내용을 분석하여 10개의 핵심 용어(KeyPoint)와 설명을 생성하세요.
설명을 생성할 때 영상 위주가 아닌 최대한 전문적이고 구체적으로 추가 설명해주세요. 저는 영상 내용 뿐 아니라 그 용어에 대한 내용을 알고 싶습니다.
중요하지 않더라도 알면 좋을 추가 핵심 용어도 더해주세요.

[타임라인 요약]:
{summary}

[가이드]:
- 필드는 `term`과 `description`을 포함하며, 결과는  10개의 키포인트 리스트로 구성됩니다.
- 반드시 JSON 형식에 맞춰 반환하세요.
- 다른 텍스트는 포함하지 마세요.

[반환 형식]:
{output_format}
        """
        )

        # 3. Chain
        self._chain = key_point_prompt_template | self._llm | key_point_parser


# ✅ (핵심 키포인트 모델)
class YoutubeKeyPointModel(BaseModel):
    term: str = Field(..., description="핵심 용어")
    description: str = Field(..., description="핵심 용어에 대한 설명")


# ✅ (핵심 키포인트 컬렉션 모델)
class YoutubeKeyPointCollectionModel(BaseModel):
    key_points: List[YoutubeKeyPointModel] = Field(..., description="영상에서 추출된 핵심 키포인트 리스트")