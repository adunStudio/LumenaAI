from abc import ABC, abstractmethod
from domain.value_object import YouTubeScript

class STTStrategy(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        pass

    @abstractmethod
    def transcribe_to_script(self, audio_path: str) -> YouTubeScript:
        pass