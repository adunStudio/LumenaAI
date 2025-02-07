from enum import Enum


class ExecuteResultType(Enum):
    DUPLICATE_CONTENT = "중복된 콘텐츠입니다."
    INVALID_YOUTUBE_URL = "유효하지 않은 유튜브 링크입니다."
    STORE_SUCCESS = "데이터 저장에 성공했습니다."
    STORE_FAIL = "데이터 저장에 실패했습니다."
    DATA_NOT_FOUND = "데이터가 존재하지 않습니다."
    AUTO_SCRIPT_PARSE_SUCCESS = "스크립트 판별에 성공했습니다."
    AUTO_SCRIPT_PARSE_FAIL = "스크립트 판별에 실패했습니다."
    AUDIO_DOWNLOAD_SUCCESS = "오디오 파일 다운로드가 완료됐습니다."
    AUDIO_DOWNLOAD_FAIL = "오디오 파일 다운로드가 실패했습니다."
    AUDIO_NOT_EXIST = "오디오 파일이 없습니다."
    STT_SUCCESS = "STT를 성공했습니다."
    STT_FAIL = "STT를 실패했습니다."
    SCRIPT_NOT_FOUND = "스크립트가 없습니다."
    SCRIPT_REFINE_SUCCESS = "스크립트를 매끄럽게 만들었습니다."
    SCRIPT_REFINE_FAIL = "스크립트를 매끄럽게 만들기에 실패했습니다.."
    SCRIPT_TIMELINE_SUMMARY_FAIL = "타임라인 요약 생성에 실패했습니다."
    SCRIPT_TIMELINE_SUMMARY_SUCCESS = "타임라인 요약 생성을 완료했습니다."
    TIMELINE_SUMMARY_NOT_FOUND = "타임라인을 찾지 못했습니다."
    KEY_POINT_FAIL = "핵심 용어 생성에 실패했습니다."
    KEY_POINT_SUCCESS = "핵심 용어 생성에 성공했습니다."


class ExecuteResult:
    def __init__(self, result: bool, result_type: ExecuteResultType):
        self._result = result
        self._result_type = result_type

    @property
    def result(self):
        return self._result

    @property
    def result_type(self):
        return self._result_type

    @property
    def message(self):
        return self._result_type.value
