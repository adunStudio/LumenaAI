from application.strategy.stt_strategy import STTStrategy


class LocalWhisperXStrategy(STTStrategy):
    def transcribe(self, audio_path: str) -> str:
        pass