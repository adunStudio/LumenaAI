from infrastructure.database.mongo_client import MongoDBClient
from infrastructure.repository.youtube_content_repository import YouTubeContentRepository
from service.youtube_content_service import YouTubeContentService
from strategy import LocalWhisperStrategy, STTStrategyFactory, STTStrategyType

from use_case import \
    YouTubeParseAndStore, \
    YouTubeAutoScriptParse, \
    YouTubeAudioDownload, \
    YouTubeAudioSTT, \
    YouTubeScriptRefinement

from langchain_openai import ChatOpenAI


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
    config.whisper_model_name.override("openai/whisper-large-v3-turbo")

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

    # STTStrategy
    stt_strategy = providers.Singleton(
        LocalWhisperStrategy,
        model_name=config.whisper_model_name,
        batch_size=32,
        clean=True
    )

    # YouTubeContentService
    youtube_service = providers.Singleton(
        YouTubeContentService,
        repository=youtube_repository,
    )

    ###############################################
    # LLM
    ###############################################

    llm_openai = providers.Singleton(
        ChatOpenAI,
        model="gpt-4o-mini",
        api_key=config.openai_api_key
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
        stt_strategy=stt_strategy
    )

    # 5. YoutubeScriptRefinement
    youtube_script_refinement = providers.Singleton(
        YouTubeScriptRefinement,
        repository=youtube_repository,
        llm=llm_openai
    )
