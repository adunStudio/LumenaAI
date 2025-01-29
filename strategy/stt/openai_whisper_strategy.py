from strategy import STTStrategy

from openai import OpenAI

import re
from typing import List
from domain import YouTubeScript, YouTubeScriptChunk
from langchain.schema import Document
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import OpenAIWhisperParser
import time


class OpenAIWhisperStrategy(STTStrategy):
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenAI Whisper API 키가 필요합니다.")

        self._api_key = api_key
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
        loader = GenericLoader(AudioBlobLoader(audio_path),
                               OpenAIWhisperParser(api_key=self._api_key, response_format="srt"))

        docs = loader.load()
        return self._convert_documents_to_youtube_script(docs)

    def _timestamp_to_seconds(self, timestamp: str) -> float:
        """타임스탬프 (00:00:00,000) 형식을 초(float)로 변환"""
        h, m, s_ms = timestamp.split(":")
        s, ms = s_ms.split(",")
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0

    def _clean_text(self, text: str) -> str:
        """텍스트에서 불필요한 숫자 및 라인 번호 제거"""
        text = re.sub(r"^\d+\s*", "", text)  # 앞쪽 라인 번호 제거
        # text = re.sub(r"\s*\d+\s*", " ", text)  # 문장 중간 숫자(단독) 제거
        return text.strip()

    def _extract_chunks(self, document: Document) -> List[YouTubeScriptChunk]:
        """Document 객체에서 YouTubeScriptChunk 리스트를 추출하는 함수"""

        chunks = []
        lines = document.page_content.split("\n")

        timestamp_pattern = re.compile(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})")

        i = 0
        while i < len(lines):
            match = timestamp_pattern.search(lines[i])
            if match:
                start_time = self._timestamp_to_seconds(match.group(1))
                end_time = self._timestamp_to_seconds(match.group(2))

                text = []
                i += 1
                while i < len(lines) and not timestamp_pattern.search(lines[i]):
                    cleaned_line = self._clean_text(lines[i].strip())  # 불필요한 숫자 제거
                    if cleaned_line:  # 빈 문자열 제거
                        text.append(cleaned_line)
                    i += 1

                if text:
                    chunk = YouTubeScriptChunk(timestamp=(start_time, end_time), text=" ".join(text))
                    chunks.append(chunk)
            else:
                i += 1

        return chunks

    def _convert_documents_to_youtube_script(self, documents: List[Document]) -> YouTubeScript:
        """Document 객체 리스트를 YouTubeScript 객체로 변환하는 함수"""

        all_chunks = []
        full_script = ""

        for document in documents:
            chunks = self._extract_chunks(document)
            all_chunks.extend(chunks)
            full_script += " ".join(chunk.text for chunk in chunks) + " "

        return YouTubeScript(script=full_script.strip(), chunks=all_chunks)



from typing import Iterable

from langchain_community.document_loaders.blob_loaders import FileSystemBlobLoader
from langchain_community.document_loaders.blob_loaders.schema import Blob, BlobLoader


class AudioBlobLoader(BlobLoader):

    def __init__(self, file_path: str):
        self._file_path = file_path

    def yield_blobs(self) -> Iterable[Blob]:
        loader = FileSystemBlobLoader(self._file_path)
        for blob in loader.yield_blobs():
            yield blob