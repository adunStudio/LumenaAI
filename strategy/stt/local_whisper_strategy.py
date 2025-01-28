from strategy import STTStrategy
from domain import YouTubeScript, YouTubeScriptChunk

import gc
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


class LocalWhisperStrategy(STTStrategy):
    def __init__(self, model_name: str, batch_size: int, clean: bool):
        self._pipe = None
        self._model_name = model_name
        self._batch_size = batch_size
        self._clean = clean

        device = "cuda" if torch.cuda.is_available() else \
            "mps" if torch.backends.mps.is_available() else \
                "cpu"

        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        model = AutoModelForSpeechSeq2Seq.from_pretrained(self._model_name, torch_dtype=torch_dtype)
        model.to(device)

        processor = AutoProcessor.from_pretrained(self._model_name)
        self._pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=torch_dtype,
            device=device,
            chunk_length_s=25,
            batch_size=self._batch_size
        )

    def transcribe(self, audio_path: str) -> str:
        result = self._pipe(audio_path, return_timestamps=True)

        if self._clean:
            self._cleanup()

        return result

    def transcribe_to_script(self, audio_path: str) -> YouTubeScript:
        result = self.transcribe(audio_path)
        youtube_script = YouTubeScript(

            script=result["text"],
            chunks=[
                YouTubeScriptChunk.from_dict(chunk)
                for chunk in result["chunks"]
            ],
        )
        return youtube_script

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
