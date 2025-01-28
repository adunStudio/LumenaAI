from typing import Dict, List

from whisperx.types import TranscriptionResult

from application.strategy import STTStrategy
from domain.value_object import YouTubeScript, YouTubeScriptChunk
import gc
import torch
import whisperx


class LocalWhisperXStrategy(STTStrategy):
    def __init__(self,  model_name: str, batch_size: int, clean: bool):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if torch.cuda.is_available() else "int8"

        self._batch_size = batch_size
        self._model = whisperx.load_model(model_name, device, compute_type=compute_type)
        self.clean = clean

    def transcribe(self, audio_path: str) -> TranscriptionResult:
        audio = whisperx.load_audio(audio_path)
        return self._model.transcribe(audio, batch_size=self._batch_size)

    def transcribe_to_script(self, audio_path: str) -> YouTubeScript:
        result = self.transcribe(audio_path)
        print(result)
        youtube_script = YouTubeScript(
            script=''.join(segment['text'] for segment in result['segments']),
            chunks=[
                YouTubeScriptChunk.from_dict({'timestamp': (segment['start'], segment['end']), 'text': segment['text']})
                for segment in result['segments']
            ],
        )
        return youtube_script

