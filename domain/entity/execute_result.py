from enum import Enum


class ExecuteResultType(Enum):
    DUPLICATE_CONTENT = "중복된 콘텐츠입니다."
    INVALID_YOUTUBE_URL = "유효하지 않은 유튜브 링크입니다."
    STORE_SUCCESS = "데이터 저장에 성공했습니다."
    STORE_FAIL = "데이터 저장에 실패했습니다."
    DATA_NOT_FOUND = "데이터가 존재하지 않습니다."
    AUTO_SCRIPT_PARSE_FAIL = "스크립트 판별에 실패했습니다."


class ExecuteResult:
    def __init__(self, result: bool, message: ExecuteResultType):
        self._result = result
        self._message = message

    @property
    def result(self):
        return self._result

    @property
    def message(self):
        return self._message
