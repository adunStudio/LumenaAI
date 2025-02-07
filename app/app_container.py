from infrastructure.database.mongo_client import MongoDBClient
from infrastructure.repository import YoutubeContentRepository, YoutubeScriptCollectionRepository, YoutubeChatRepository, YoutubeKeyPointCollectionRepository
from service import YoutubeContentService, YoutubeScriptCollectionService, YoutubeChatService, YoutubeKeyPointCollectionService
from strategy import LocalWhisperStrategy, STTStrategyFactory, STTStrategyType, OpenAIWhisperStrategy
from langchain_openai import OpenAIEmbeddings

from use_case import \
    YouTubeParseAndStore, \
    YouTubeAutoScriptParse, \
    YouTubeAudioDownload, \
    YouTubeAudioSTT, \
    YouTubeScriptRefinement, \
    YouTubeGenerateTimelineSummary, \
    YouTubeGenerateKeyPoint

from langchain_openai import ChatOpenAI


import os
from dotenv import load_dotenv

from dependency_injector import containers, providers

load_dotenv()


class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.mongo_uri.override(os.getenv("MONGO_CONNECTION_STRING"))
    config.database_name.override(os.getenv("MONGO_DATABASE_NAME", "LumenaAI"))
    config.youtube_content_collection_name.override("youtube_content")
    config.youtube_chat_collection_name.override("youtube_chat")
    config.youtube_key_point_collection_name.override("youtube_keypoint_collection")
    config.youtube_script_collection_name.override("youtube_script_collection")
    config.openai_api_key.override(os.getenv("OPENAI_API_KEY"))
    config.whisper_model_name.override("openai/whisper-large-v3-turbo")

    ###############################################
    # LLM
    ###############################################

    llm_openai = providers.Singleton(
        ChatOpenAI,
        model="gpt-4o-mini",
        api_key=config.openai_api_key
    )

    embedding_openai = providers.Singleton(
        OpenAIEmbeddings,
        api_key=config.openai_api_key
    )


    ###############################################
    # DB
    ###############################################
    mongo_client = providers.Singleton(
        lambda uri, database_name: MongoDBClient(uri, database_name).connect(),
        uri=config.mongo_uri,
        database_name=config.database_name,
    )


    ###############################################
    # YoutubeContent
    ###############################################
    youtube_content_repository = providers.Singleton(
        YoutubeContentRepository,
        client=mongo_client,
        collection_name=config.youtube_content_collection_name,
    )

    youtube_content_service = providers.Singleton(
        YoutubeContentService,
        repository=youtube_content_repository,
    )


    ###############################################
    # YoutubeScriptCollection
    ###############################################
    youtube_script_collection_repository = providers.Singleton(
        YoutubeScriptCollectionRepository,
        client=mongo_client,
        collection_name=config.youtube_script_collection_name,
    )

    youtube_script_collection_service = providers.Singleton(
        YoutubeScriptCollectionService,
        repository=youtube_script_collection_repository,
    )


    ###############################################
    # YoutubeKeyPointCollection
    ###############################################
    youtube_key_point_collection_repository = providers.Singleton(
        YoutubeKeyPointCollectionRepository,
        client=mongo_client,
        collection_name=config.youtube_key_point_collection_name,
    )

    youtube_key_point_service = providers.Singleton(
        YoutubeKeyPointCollectionService,
        repository=youtube_key_point_collection_repository,
    )


    ###############################################
    # YoutubeChat
    ###############################################
    youtube_chat_repository = providers.Singleton(
        YoutubeChatRepository,
        client=mongo_client,
        collection_name=config.youtube_chat_collection_name,
    )

    youtube_chat_service = providers.Singleton(
        YoutubeChatService,
        embedding=embedding_openai,
        llm=llm_openai,
        repository=youtube_chat_repository,
    )


    ###############################################
    # STT
    ###############################################

    # STTStrategy
    # stt_strategy = providers.Singleton(
    #     LocalWhisperStrategy,
    #     model_name=config.whisper_model_name,
    #     batch_size=32,
    #     clean=True
    # )
    stt_strategy = providers.Singleton(
        OpenAIWhisperStrategy,
        api_key=config.openai_api_key
    )


    ###############################################
    # 새로운 지식 추가 하기 유즈 케이스
    ###############################################

    # 1. YoutubeContentsParseAndStore
    youtube_parse_and_store = providers.Singleton(
        YouTubeParseAndStore,
        repository=youtube_content_repository
    )

    # 2. YouTubeContentAutoScriptParse
    youtube_auto_script_parse = providers.Singleton(
        YouTubeAutoScriptParse,
        content_repository=youtube_content_repository,
        script_repository=youtube_script_collection_repository
    )

    # 3. YoutubeAudioDownload
    youtube_audio_download = providers.Singleton(
        YouTubeAudioDownload,
        repository=youtube_content_repository
    )

    # 4. YoutubeAudioSTT
    youtube_audio_stt = providers.Singleton(
        YouTubeAudioSTT,
        content_repository=youtube_content_repository,
        script_repository=youtube_script_collection_repository,
        stt_strategy=stt_strategy
    )

    # 5. YoutubeScriptRefinement
    youtube_script_refinement = providers.Singleton(
        YouTubeScriptRefinement,
        content_repository=youtube_content_repository,
        script_repository=youtube_script_collection_repository,
        llm=llm_openai
    )

    # 6. YouTubeGenerateTimelineSummary
    youtube_generate_timeline_summary = providers.Singleton(
        YouTubeGenerateTimelineSummary,
        content_repository=youtube_content_repository,
        script_repository=youtube_script_collection_repository,
        llm=llm_openai
    )

    # 7. YoutubeGenerateKeyPoint
    youtube_generate_key_point = providers.Singleton(
        YouTubeGenerateKeyPoint,
        content_repository=youtube_content_repository,
        key_point_collection_repository=youtube_key_point_collection_repository,
        llm=llm_openai
    )