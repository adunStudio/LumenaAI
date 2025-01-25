from application.strategy.stt_strategy import STTStrategy

import gc
import torch
import whisperx


class LocalWhisperXStrategy(STTStrategy):
    def __init__(self,  model_name: str = "large-v2", batch_size: int = 16):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if torch.cuda.is_available() else "int8"

        self._batch_size = batch_size
        self._model = whisperx.load_model(model_name, device, compute_type=compute_type)

    def transcribe(self, audio_path: str) -> str:
        audio = whisperx.load_audio(audio_path)

        result = self._model.transcribe(audio, batch_size=self._batch_size)
        self._cleanup()

        return result

    def _cleanup(self):
        # GPU 캐시 비우기
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

        # Python 가비지 컬렉션 실행
        gc.collect()

        print("캐시가 성공적으로 비워졌습니다.")
