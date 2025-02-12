from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from typing import Optional, List, Dict, Any
from langchain.llms.base import LLM
import torch

class LocalHuggingFaceLLM(LLM):
    """LangChain LLM 클래스를 상속하여 Hugging Face 모델을 래핑하는 클래스"""

    model_name: str  # LangChain LLM이 요구하는 속성
    device: str = "auto"
    max_new_tokens: int = 2048
    temperature: float = 0.6
    top_p: float = 0.9

    def __init__(
        self,
        model_name: str,
        device: Optional[str] = "auto",
        max_new_tokens: int = 2048,
        temperature: float = 0.6,
        top_p: float = 0.9
    ):
        """Hugging Face 모델을 로드하고 LangChain LLM으로 변환하는 초기화 메서드"""
        super().__init__()

        # ✅ 내부 속성으로 저장 (Pydantic 필드 문제 방지)
        self._model_name = model_name
        self._device = device
        self._max_new_tokens = max_new_tokens
        self._temperature = temperature
        self._top_p = top_p

        # ✅ 모델 및 토크나이저 로드
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map=self._device
        )

        # ✅ 종료 토큰 설정
        self._eos_token_id = self._get_eos_token_id()

        # ✅ 텍스트 생성 파이프라인 생성
        self._pipeline = pipeline(
            "text-generation",
            model=self._model,
            tokenizer=self._tokenizer,
            max_new_tokens=self._max_new_tokens,
            temperature=self._temperature,
            top_p=self._top_p,
            eos_token_id=self._eos_token_id
        )

    def _get_eos_token_id(self) -> Optional[int]:
        """모델의 종료 토큰 ID를 자동 감지하여 설정"""
        eos_tokens = ["<|end_of_text|>", "<|eot_id|>"]
        for token in eos_tokens:
            token_id = self._tokenizer.convert_tokens_to_ids(token)
            if token_id != self._tokenizer.unk_token_id:  # 존재하는 토큰인지 확인
                return token_id
        return None  # 종료 토큰이 없을 경우 None 반환

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """프롬프트를 입력받아 LLM 출력을 생성"""
        output = self._pipeline(prompt)
        return output[0]["generated_text"]

    @property
    def _llm_type(self) -> str:
        """LangChain 내부에서 LLM 타입을 구분하는 속성"""
        return "HuggingFace_LLM"

    @property
    def model_name(self) -> str:
        """LangChain에서 요구하는 model_name 속성 추가"""
        return self._model_name  # 내부 속성 반환

    @property
    def device(self) -> str:
        """LangChain에서 요구하는 device 속성 추가"""
        return self._device  # 내부 속성 반환

    @property
    def tokenizer(self) -> AutoTokenizer:
        """LangChain에서 요구하는 tokenizer 속성 추가"""
        return self._tokenizer  # 내부 속성 반환

    def generate(self, messages: List[Dict[str, str]]) -> str:
        """ChatOpenAI 스타일의 message 리스트를 받아 응답을 생성"""
        user_message = next(msg["content"] for msg in messages if msg["role"] == "user")
        return self._call(user_message)
