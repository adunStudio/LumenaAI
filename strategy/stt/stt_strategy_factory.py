from strategy import STTStrategy
from strategy import OpenAIWhisperStrategy
from strategy import LocalWhisperStrategy
from strategy import LocalWhisperXStrategy
from strategy import AutoYoutubeStrategy

from enum import Enum


class STTStrategyType(Enum):
    OPENAI_WHISPER = "openai-whisper"
    LOCAL_WHISPER = "local-whisper"
    LOCAL_WHISPERX = "local-whisperx"
    AUTO_YOUTUBE = 'auto-youtube'


class STTStrategyFactory:
    _cached_strategies = {}  # 전략 객체 캐싱

    @staticmethod
    def create(strategy_type: STTStrategyType, **kwargs) -> STTStrategy:
        cache_key = f"{strategy_type.value}_{kwargs}"

        if cache_key in STTStrategyFactory._cached_strategies:
            return STTStrategyFactory._cached_strategies[cache_key]

        # 새 객체 생성
        if strategy_type == STTStrategyType.OPENAI_WHISPER:
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("OpenAI Whisper API 키가 필요합니다.")
            strategy = OpenAIWhisperStrategy(api_key=api_key)

        elif strategy_type == STTStrategyType.LOCAL_WHISPER:
            model_name = kwargs.get("model_name", "openai/whisper-large-v3-turbo")
            batch_size = kwargs.get("batch_size", 128)
            clean = kwargs.get("clean", True)
            strategy = LocalWhisperStrategy(model_name=model_name, batch_size=batch_size, clean=clean)

        elif strategy_type == STTStrategyType.LOCAL_WHISPERX:
            model_name = kwargs.get("model_name", "large-v2")
            batch_size = kwargs.get("batch_size", 128)
            clean = kwargs.get("clean", True)
            strategy = LocalWhisperXStrategy(model_name=model_name, batch_size=batch_size, clean=clean)

        elif strategy_type == STTStrategyType.AUTO_YOUTUBE:
            strategy = AutoYoutubeStrategy()

        else:
            raise ValueError(f"잘못된 STT 전략 유형: {strategy_type}")

        # 새로 생성한 객체를 캐싱
        STTStrategyFactory._cached_strategies[cache_key] = strategy
        return strategy
