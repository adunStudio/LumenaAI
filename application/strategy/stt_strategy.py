from abc import ABC, abstractmethod


class STTStrategy(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        pass
