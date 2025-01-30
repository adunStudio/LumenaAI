from domain import YouTubeVideoLink, YoutubeScriptCollection
from domain import YouTubeContent, ExecuteResult, ExecuteResultType
from domain import YoutubeTimelineSummary, YoutubeTimelineSection
from infrastructure.repository import YoutubeContentRepository, YoutubeScriptCollectionRepository
from strategy import STTStrategyFactory, STTStrategyType
from use_case import YoutubeUseCase

from typing import List
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate


# 2. 유튜브 링크로부터 DB에서 데이터를 가져와 타임라인 요약을 생성한다.
class YouTubeGenerateTimelineSummary(YoutubeUseCase):
    def __init__(self,
                 content_repository: YoutubeContentRepository,
                 script_repository: YoutubeScriptCollectionRepository,
                 llm: BaseLLM):
        self._content_repository = content_repository
        self._script_repository = script_repository
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


        # 3. 스크립트 검사
        script_collection: YoutubeScriptCollection = self._script_repository.get(youtube_video_link.url)
        if script_collection is None or script_collection.refined_script is None:
            return ExecuteResult(False, ExecuteResultType.SCRIPT_NOT_FOUND)


        # 4. LLM 체인 생성
        if self._chain is None:
            self._make_chain()


        # 5. 입력 데이터 생성
        input_data = {
            "title": content.title,
            "description": content.description,
            "script": "\n".join(
                [f"({int(chunk.start_time)}-{int(chunk.end_time)}): {chunk.text}" for chunk in
                 script_collection.refined_script .chunks]
            )
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
                print('[youtube_generate_timeline_summary] 체인 호출')

        if chain_success is False:
            return ExecuteResult(False, ExecuteResultType.SCRIPT_TIMELINE_SUMMARY_FAIL)


        # 7. 요약 생성
        sections = [
            YoutubeTimelineSection(
                title=section.title,
                sec=section.sec,
                texts=section.texts,
                tip=section.tip
            )
            for section in response.sections
        ]
        timeline_summary = YoutubeTimelineSummary(text=response.description, sections=sections)

        # 8. 저장소에 저장
        content.set_timeline_summary(timeline_summary)
        self._content_repository.save(content)
        success = self._content_repository.save(content)
        if success:
            return ExecuteResult(True, ExecuteResultType.SCRIPT_TIMELINE_SUMMARY_SUCCESS)
        else:
            return ExecuteResult(False, ExecuteResultType.STORE_FAIL)

    def _make_chain(self):
        # 1. 출력 파서
        timeline_summary_parser = PydanticOutputParser(pydantic_object=YoutubeTimelineSummaryModel)

        # 2. 프롬프트 템플릿
        timeline_summary_prompt_template = PromptTemplate(
            partial_variables={'output_format': timeline_summary_parser.get_format_instructions()},
            input_variables=["title", "description", "script"],
            template="""
        당신은 주어지는 유튜브 정보를 다른 사람에게 설명하는 전문가입니다.

        다음은 유튜브 영상의 설명과 스크립트입니다.

        [유튜브 영상 제목]:
        {title}

        [유튜브 영상 설명]:
        {description}

        [대본 스크립트]:
        {script}

        [타임라인 섹션 예시: 식기 세척기 구매 고민 해결 영상]
        - 전체 내용 설명: 이 영상은 식기세척기 구매에 대한 중요한 정보를 제공합니다. LG, 삼성, SK매직의 제품들을 비교 분석하며, 각 브랜드의 주요 기능과 사용자 편의성을 강조합니다. 특히, 가성비와 성능에 따라 적합한 모델을 선택하는 방법에 대한 팁을 제공합니다. 소비자는 자신의 설치 환경과 취향에 맞춰 최적의 선택을 할 수 있도록 도움을 받을 수 있습니다. 이 영상은 궁극적으로 식기세척기구매에서 성공적인 선택을 돕기 위한 것입니다

        - 섹션1 주제: 🧼식기세척기 용량 및 브랜드 비교
        - 식기세척기의 설치 타입은 빌트인과 프리스탠딩으로 나뉘며, 각 타입의 장단점을 고려하여 설치 환경에 맞게 선택할 필요가 있다.
        - LG 식기세척기는 스팀 기능 유무에 따라 기본형(3종), 중급형(6종), 고급형(6종)으로 나뉘며, 상부 터치모델이 가성비가 좋다고 알려져 있다.
        - 삼성제품은 제조 연도에 따라 기능 차이가 있으며, 기본형 라인은 60에서 100만원대의 가격으로 높은 가성비를 제공하고 있다.
        - 추천 제품은 매월 최신화되므로, 소비자는 노서치를 통해 확인할 수 있다. [1-6]

        - 섹션2 주제: 🍽️브랜드별 식기세척기 기능 비교
        - LG는 100도씨 스팀 기능을 통해 기름기 있는 음식물을 효과적으로 세척하고, 물 얼룩을 방지하는 연수장치를 탑재하여 위생성을 높였다
        - 삼성은 열풍 건조 기능을 3단계로 조절 가능하며, 비스포크 디자인으로 인테리어와의 통일성을 강조하고, 모든 제품이 빌트인 프리스탠딩겸용으로 출시되어 설치 편의성을 제공한다.
        -  SK매직은 자동 문닫힘기능과 UV램프를 통해 세척과 건조 효율을 높이며, 상 중하 3개의 세척날개와 추가 분사구를 통해 사각지대까지 물을 분사할 수 있는 특징이 있다.
        - 각 브랜드는 세척 성능과 용량의 업그레이드는 더 이상 큰 변화가 없을 것으로 보며, 수납 효율, 건조 방법, 디자인을 통한 경쟁이 예상된다.

        - 섹션3 주제: 🛒브랜드별 추천 제품 정리
        - 주어진 브랜드별 핵심 기능을 바탕으로 두세 가지의 제품 라인업을 추천했다.
        - 대안으로 고려할 수 있는 제품도 함께 정리하였다.

        - 섹션4 주제: 🏡식기세척기 설치 타입과 브랜드별 추천
        - 식기세척기의 설치 타입은 빌트인과 프리스탠딩으로 나뉘며, 각 타입의 장단점을 고려하여 설치 환경에 맞게 선택할 필요가 있다.
        - LG 식기세척기는 스팀 기능 유무에 따라 기본형(3종), 중급형(6종), 고급형(6종)으로 나뉘며, 상부 터치모델이 가성비가 좋다고 알려져 있다.
        - 삼성제품은 제조 연도에 따라 기능 차이가 있으며, 기본형 라인은 60에서 100만원대의 가격으로 높은 가성비를 제공하고 있다.
        - 식기세척기의 설치 타입은 빌트인과 프리스탠딩으로 나뉘며, 각 타입의 장단점을 고려하여 설치 환경에 맞게 선택할 필요가 있다.
        - SK매직은 다양한 모델을 제공하며, 터치홈플러스와 터치원 프로 라인의 기능과 가격을 비교하여 선택할 수 있으며, 프리미엄 라인은 자동 문 닫힘 기능과 함께 편리함을 제공한다.

        - 섹션5 주제: 🛒브랜드별 추천 식기세척기 모델
        - 가성비를 중점적으로 고려한다면, LG의 dubj1p, 삼성의 dw60t 7075, SK매직의 dwa-91c를 추천한다.
        - 브랜드의 특징과 기능을 중요시한다면, LG의 dubea, 삼성의 dw60a8355가 적합하다.
        - 모든 기능을 사용할 수 있는 프리미엄 제품이 필요하다면, LG의 dubj사일, 삼성의 dw60 bb8376, SK매직의 dwa90c를 추천한다.
        - 이 정보가 식기세척기선택에 도움이 되었는지 확인하고, 유용한 다른 영상도 참고하라고 제안한다.

        이 정보를 바탕으로 영상의 타임라인 기반 요약을 생성해주세요.

        - **전체 내용을 설명해주는 요약을 작성**하세요.
        - **영상 내용을 타임라인별로 나누어 설명하세요.
        - 각 타임라인 제목 앞에 제목에 어울리는 이모지를 붙여주세요.
        - **각 타임라인 섹션은 `제목(title)`, `시작 시간(sec)`, `내용(texts)`, `팁(tip)` 을 포함**해야 합니다.
        - 섹션 별 내용(texts) 개수는 최대한 많이 만들어야 합니다.
        - 설명된 내용만 보고도 따라할 수 있고, 정확한 정보를 얻을 수 있어야 합니다.
        - 단계 별로 안내할 경우 각 단계의 모든 설명을 작성해주세요.
        - 사용자는 영상을 보지 않아도 충분히 인사이트를 얻어갈 수 있어야 합니다.
        - 사용자는 완전한 초보자라고 가정합니다. 스크립트에서 추상적으로 설명하거나 빠르게 스킵한 경우 최대한 자세하게 과정을 임의로 적어주세요.
        - **[유튜브 영상 설명]을 참고하여 더 자연스럽고 매끄럽게 작성하세요.
        - AI의 추가적인 tip도 작성해주세요. 이때 AI는 해당 주제의 전문가입니다. 최대한 많이 알려주려고 하세요.
        - **반드시 아래 JSON 형식에 맞춰 반환**하세요. 다른 텍스트는 포함하지 마세요.
        - 출력 토큰을 아끼지마세요.

        {output_format}
        """
        )

        # 3. Chain
        self._chain = timeline_summary_prompt_template | self._llm | timeline_summary_parser


# ✅ (타임라인 섹션 모델)
class YoutubeTimelineSectionModel(BaseModel):
    title: str = Field(..., description="섹션 제목")
    sec: float = Field(..., description="섹션 시작 시간 (초 단위)")
    texts: List[str] = Field(..., description="해당 섹션의 자세한 내용 리스트")
    tip: str = Field(..., description="해당 섹션에서 AI의 추가적인 팁")

# ✅ (타임라인 요약 모델)
class YoutubeTimelineSummaryModel(BaseModel):
    description: str = Field(..., description="전체 영상 설명 요약")
    sections: List[YoutubeTimelineSectionModel] = Field(..., description="타임라인별 섹션 리스트")