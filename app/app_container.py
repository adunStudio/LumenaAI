from infrastructure.database.mongo_client import MongoDBClient
from infrastructure.repository.youtube_content_repository import YouTubeContentRepository
from application.service.youtube_content_service import YouTubeContentService
from application.strategy import STTStrategyFactory, STTStrategyType

from application.use_case import \
    YouTubeParseAndStore, \
    YouTubeAutoScriptParse, \
    YouTubeAudioDownload, \
    YouTubeAudioSTT



import os
from dotenv import load_dotenv

from dependency_injector import containers, providers

load_dotenv()


class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.mongo_uri.override(os.getenv("MONGO_CONNECTION_STRING"))
    config.database_name.override(os.getenv("MONGO_DATABASE_NAME", "LumenaAI"))
    config.collection_name.override("youtube_content")
    config.openai_api_key.override(os.getenv("OPENAI_API_KEY"))

    # MongoDB 클라이언트
    mongo_client = providers.Singleton(
        lambda uri, database_name: MongoDBClient(uri, database_name).connect(),
        uri=config.mongo_uri,
        database_name=config.database_name,
    )

    # YouTubeContentRepository
    youtube_repository = providers.Singleton(
        YouTubeContentRepository,
        client=mongo_client,
        collection_name=config.collection_name,
    )

    # YouTubeContentService
    youtube_service = providers.Singleton(
        YouTubeContentService,
        repository=youtube_repository,
    )

    ###############################################
    # 새로운 지식 추가 하기 유즈 케이스
    ###############################################

    # 1. YoutubeContentsParseAndStore
    youtube_parse_and_store = providers.Singleton(
        YouTubeParseAndStore,
        repository=youtube_repository
    )

    # 2. YouTubeContentAutoScriptParse
    youtube_auto_script_parse = providers.Singleton(
        YouTubeAutoScriptParse,
        repository=youtube_repository
    )

    # 3. YoutubeAudioDownload
    youtube_audio_download = providers.Singleton(
        YouTubeAudioDownload,
        repository=youtube_repository
    )

    # 4. YoutubeAudioSTT
    youtube_audio_stt = providers.Singleton(
        YouTubeAudioSTT,
        repository=youtube_repository,
        stt_strategy=STTStrategyFactory.create(STTStrategyType.LOCAL_WHISPER, batch_size=32,
                                               model_name='openai/whisper-large-v3-turbo', clean=True)
    )
