from application.strategy.stt_strategy import STTStrategy

import gc
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


class LocalWhisperStrategy(STTStrategy):
    def __init__(self, model_name: str):
        device = "cuda" if torch.cuda.is_available() else \
                 "mps" if torch.backends.mps.is_available() else \
                 "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        model = AutoModelForSpeechSeq2Seq.from_pretrained(model_name, torch_dtype=torch_dtype)
        model.to(device)

        processor = AutoProcessor.from_pretrained(model_name)
        self._pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=torch_dtype,
            device=device,
            chunk_length_s=25,
            batch_size=128
        )

    def transcribe(self, audio_path: str) -> str:
        result = self._pipe(audio_path, return_timestamps=True)
        return result

    def _cleanup(self):
        # GPU 캐시 비우기
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

        # Python 가비지 컬렉션 실행
        gc.collect()

        # MPS 사용 시 캐시 비우기
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

        print("캐시가 성공적으로 비워졌습니다.")