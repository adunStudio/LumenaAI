from abc import ABC, abstractmethod
from domain.value_object import YouTubeScript
from domain.entity import YouTubeContent, ExecuteResult, ExecuteResultType


class YoutubeUseCase(ABC):
    @abstractmethod
    def execute(self, url: str, **kwargs) -> ExecuteResult:
        pass
