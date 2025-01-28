from abc import ABC, abstractmethod
from domain import YouTubeScript
from domain import YouTubeContent, ExecuteResult, ExecuteResultType


class YoutubeUseCase(ABC):
    @abstractmethod
    def execute(self, url: str, **kwargs) -> ExecuteResult:
        pass
