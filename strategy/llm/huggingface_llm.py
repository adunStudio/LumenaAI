from typing import Any, List, Optional, Dict
from langchain.llms.base import BaseLLM
from langchain.schema import LLMResult, Generation
from transformers import pipeline, AutoTokenizer, BitsAndBytesConfig
import torch
from pydantic import Field, PrivateAttr


class HuggingFaceLLM(BaseLLM):
    """LangChain에서 Hugging Face 모델을 실행할 수 있도록 래핑하는 LLM 클래스"""

    model_id: str = Field(..., description="Hugging Face 모델 ID")
    max_new_tokens: int = Field(1024, description="생성할 최대 토큰 수")
    temperature: float = Field(0.6, description="샘플링 다양성을 조절하는 온도 값")
    top_k: int = Field(50, description="샘플링 시 고려할 후보 단어 개수")
    device: str = Field("auto", description="디바이스 설정 (auto, cpu, cuda 등)")
    quantization: Optional[str] = Field(None, description="양자화 설정 (4bit, 8bit, 16bit)")

    # ❗ Pydantic에서 처리하지 않도록 Private 변수로 설정
    _tokenizer: Any = PrivateAttr()
    _pipeline: Any = PrivateAttr()

    def __init__(self, model_id: str, quantization: Optional[str] = None, **kwargs):
        super().__init__(model_id=model_id, quantization=quantization, **kwargs)  # ✅ 필수 필드 초기화
        self.model_id = model_id
        self.quantization = quantization

        # Pydantic의 데이터 모델에서 제외하기 위해 Private 변수 사용
        self._tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        self._pipeline = self._load_pipeline()

    def _load_pipeline(self):
        """Hugging Face 파이프라인을 로드하고, 양자화를 적용"""
        quantization_config = None
        model_kwargs = {}

        # 8비트 양자화 적용
        if self.quantization == "8bit":
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
                bnb_8bit_compute_dtype=torch.float16  # FP16 연산 (속도 최적화)
            )

        # 4비트 양자화 적용
        elif self.quantization == "4bit":
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )

        # 16비트 연산 (FP16)
        elif self.quantization == "16bit":
            model_kwargs["torch_dtype"] = torch.float16  # FP16 적용

        # `pipeline` 생성
        return pipeline(
            "text-generation",
            model=self.model_id,
            tokenizer=self._tokenizer,  # ✅ Private 변수 사용
            device_map=self.device,
            quantization_config=quantization_config,
            model_kwargs=model_kwargs,
            max_new_tokens=self.max_new_tokens,
            temperature=self.temperature,
            top_k=self.top_k
        )

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """LangChain과 호환되는 `_call()` 메서드 구현 (단일 프롬프트 처리)"""
        response = self._pipeline(prompt)  # ✅ Private 변수 사용
        return response[0]["generated_text"]

    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> LLMResult:
        """LangChain의 `_generate()` 구현 - 여러 개의 프롬프트를 한 번에 처리"""
        generations = []
        for prompt in prompts:
            response = self._call(prompt)
            generations.append([Generation(text=response)])

        return LLMResult(generations=generations)

    @property
    def tokenizer(self):
        """토크나이저에 접근할 수 있도록 `@property`로 제공"""
        return self._tokenizer

    @property
    def pipeline(self):
        """파이프라인에 접근할 수 있도록 `@property`로 제공"""
        return self._pipeline

    @property
    def _identifying_params(self) -> dict:
        """LangChain에서 모델 설정을 확인할 수 있도록 설정"""
        return {
            "model_id": self.model_id,
            "quantization": self.quantization,
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "top_k": self.top_k,
        }

    @property
    def _llm_type(self) -> str:
        """모델 타입을 반환"""
        return "huggingface_llm"
