from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain.llms.base import LLM
from typing import Optional, List, Any
from langchain.llms.base import LLM
import torch

class LocalHuggingFaceLLM(LLM):
    def __init__(self, model_name: str, device: Optional[str] = "auto", max_new_tokens: int = 2048, temperature: float = 0.6, top_p: float = 0.9):
        super().__init__()
        self.model_name = model_name
        self.device = device
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p

        # ✅ 모델 및 토크나이저 로드
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map=self.device
        )

        # ✅ 텍스트 생성 파이프라인 생성
        self.pipeline = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=self.max_new_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            eos_token_id=self.tokenizer.eos_token_id
        )

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """프롬프트를 입력받아 LLM 출력을 생성"""
        output = self.pipeline(prompt)
        return output[0]["generated_text"]

    @property
    def _llm_type(self) -> str:
        return "HuggingFace_LLM"

    def generate(self, messages: List[dict]) -> str:
        """ChatOpenAI 스타일의 message 리스트를 받아 응답을 생성"""
        user_message = next(msg["content"] for msg in messages if msg["role"] == "user")
        return self._call(user_message)