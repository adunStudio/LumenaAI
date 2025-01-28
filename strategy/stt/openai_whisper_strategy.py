from strategy import STTStrategy
from domain import YouTubeScript
from openai import OpenAI


class OpenAIWhisperStrategy(STTStrategy):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI Whisper API 키가 필요합니다.")

        self._client = OpenAI(api_key=api_key)

    def transcribe(self, audio_path: str) -> str:
        with open(audio_path, "rb") as audio_file:
            response = self._client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json"
            )
        return response

    def transcribe_to_script(self, audio_path: str) -> YouTubeScript:
        pass