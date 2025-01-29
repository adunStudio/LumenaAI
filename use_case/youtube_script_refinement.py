from use_case import YoutubeUseCase

from domain import \
    YouTubeVideoLink, \
    YouTubeScript, \
    YouTubeScriptChunk, \
    YouTubeContent, \
    ExecuteResult, \
    ExecuteResultType
from infrastructure.repository import YouTubeContentRepository

from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List, Tuple
from langchain.output_parsers import PydanticOutputParser, RetryOutputParser
from langchain.llms.base import BaseLLM


# 5. 유튜브 스크립트를 자연스럽게 정제
class YouTubeScriptRefinement(YoutubeUseCase):
    def __init__(self, repository: YouTubeContentRepository, llm: BaseLLM):
        self._repository = repository
        self._llm = llm
        self._chain = None

    def execute(self, youtube_url: str, **kwargs) -> ExecuteResult:
        # 1. 유튜브 링크 검증
        try:
            youtube_video_link = YouTubeVideoLink(youtube_url)
        except:
            return ExecuteResult(False, ExecuteResultType.INVALID_YOUTUBE_URL)


        # 2. DB 데이터 검사
        content: YouTubeContent = self._repository.find_by_url(youtube_video_link)
        if content is None:
            return ExecuteResult(False, ExecuteResultType.DATA_NOT_FOUND)


        # 3. 기존 스크립트 검사(유튜브 자동, 위스퍼)
        if (content.script_auto is None) and (content.script is None):
            return ExecuteResult(False, ExecuteResultType.SCRIPT_NOT_FOUND)


        # 4. LLM 체인 생성
        if self._chain is None:
            self._make_chain()


        # 5. 입력 데이터 생성
        input_data = {
            "description": content.description,
            "script_auto": "\n".join(
                [f"({int(chunk.start_time)}-{int(chunk.end_time)}): {chunk.text}" for chunk in
                 content.script_auto.chunks if chunk.start_time is not None and chunk.end_time is not None]
            ),
            "script_whisper": "\n".join(
                [f"({int(chunk.start_time)}-{int(chunk.end_time)}): {chunk.text}" for chunk in
                 content.script_whisper.chunks if chunk.start_time is not None and chunk.end_time is not None]
            ) if content.script_whisper is not None else 'None',
        }


        # 5. 체인 호출 (2회 시도)
        chain_success = False
        for i in range(0, 2):
            try:
                response = self._chain.invoke(input_data)
                chain_success = True
                break
            except Exception as e:
                print(e)
                print('[youtube_script_refinement] 체인 호출')

        if chain_success is False:
            return ExecuteResult(False, ExecuteResultType.SCRIPT_REFINE_FAIL)


        # 6. 스크립트 생성
        chunks = [
            YouTubeScriptChunk(
                timestamp=chunk.timestamp,
                text=chunk.text,
            )
            for chunk in response.chunks
        ]
        all_text = " ".join(chunk.text for chunk in chunks)
        refine_script = YouTubeScript(all_text, chunks)


        # 7. 저장소에 저장
        content.set_script(refine_script)
        self._repository.save(content)
        success = self._repository.save(content)
        if success:
            return ExecuteResult(True, ExecuteResultType.SCRIPT_REFINE_SUCCESS)
        else:
            return ExecuteResult(False, ExecuteResultType.STORE_FAIL)

    def _make_chain(self):
        # 1. 출력 파서
        refine_output_parser = PydanticOutputParser(pydantic_object=YouTubeScriptChunksModel)

        # 2. 프롬프트 템플릿
        refine_prompt_template = PromptTemplate(
            partial_variables={'output_format': refine_output_parser.get_format_instructions()},
            input_variables=["description", "script_auto", "script_whisper"],
            template="""
다음은 유튜브 영상의 설명과 자막입니다.
[유튜브 영상 설명]:
{description}

[자동 생성 자막]: 
{script_auto}

[Whisper 자막]: 
{script_whisper}

위 정보를 참고하여 더 정확하고 매끄러운 자막 청크를 생성해주세요.
각 청크는 타임스탬프와 텍스트로 구성되어야 합니다.

- 오타가 났거나 애매한 용어는 [유튜브 영상 설명]을 참고해주세요.
- 타임스탬프를 엄격하게 지켜주세요.

반드시 아래 JSON 형식에 맞춰 반환하세요. 다른 텍스트는 포함하지 마세요.
{output_format}
"""
        )

        # 3. Chain
        self._chain = refine_prompt_template | self._llm | refine_output_parser


# YouTubeScriptChunk의 Pydantic 모델 정의
class YouTubeScriptChunkModel(BaseModel):
    timestamp: Tuple[int, int] = Field(..., description="Chunk의 시작 및 끝 타임스탬프")
    text: str = Field(..., description="해당 시간의 스크립트 텍스트")

class YouTubeScriptChunksModel(BaseModel):
    chunks: List[YouTubeScriptChunkModel] = Field(..., description="타임스탬프별 텍스트 조각 리스트")
