"""에러 타입과 메시지 정의"""
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Dict, Any

class ErrorType(Enum):
    """에러 타입 정의"""
    DEVICE_ERROR = auto()        # 디바이스 관련 오류
    SCRIPT_ERROR = auto()        # 스크립트 관련 오류
    ENVIRONMENT_ERROR = auto()   # 환경 설정 오류
    RUNTIME_ERROR = auto()       # 실행 시간 오류
    NETWORK_ERROR = auto()       # 네트워크 관련 오류
    PERMISSION_ERROR = auto()    # 권한 관련 오류
    UNKNOWN_ERROR = auto()       # 알 수 없는 오류

@dataclass
class AppError:
    """애플리케이션 에러 데이터 클래스"""
    type: ErrorType
    message: str
    details: Optional[str] = None
    original_error: Optional[Exception] = None
    context: Optional[Dict[str, Any]] = None

# 에러 메시지 템플릿
ERROR_MESSAGES = {
    ErrorType.DEVICE_ERROR: {
        "not_found": "연결된 디바이스를 찾을 수 없습니다.",
        "multiple": "여러 개의 디바이스가 연결되어 있습니다. 하나만 연결해주세요.",
        "unauthorized": "디바이스에 대한 권한이 없습니다. USB 디버깅이 활성화되어 있는지 확인해주세요.",
        "offline": "디바이스가 오프라인 상태입니다.",
    },
    ErrorType.SCRIPT_ERROR: {
        "not_found": "스크립트 파일을 찾을 수 없습니다: {path}",
        "invalid": "잘못된 스크립트 파일입니다: {path}",
        "execution_failed": "스크립트 실행 중 오류가 발생했습니다: {error}",
    },
    ErrorType.ENVIRONMENT_ERROR: {
        "tool_missing": "필수 도구가 설치되지 않았습니다: {tool}",
        "setup_failed": "환경 설정 중 오류가 발생했습니다: {error}",
        "path_error": "경로를 찾을 수 없습니다: {path}",
    },
    ErrorType.RUNTIME_ERROR: {
        "process_failed": "프로세스 실행 중 오류가 발생했습니다: {error}",
        "timeout": "작업 시간이 초과되었습니다.",
        "memory_error": "메모리가 부족합니다.",
    },
    ErrorType.NETWORK_ERROR: {
        "connection_failed": "네트워크 연결에 실패했습니다: {error}",
        "timeout": "네트워크 요청 시간이 초과되었습니다.",
    },
    ErrorType.PERMISSION_ERROR: {
        "access_denied": "접근이 거부되었습니다: {path}",
        "insufficient_permissions": "권한이 부족합니다: {details}",
    },
    ErrorType.UNKNOWN_ERROR: {
        "unknown": "알 수 없는 오류가 발생했습니다: {error}",
    }
}

def format_error_message(error_type: ErrorType, error_key: str, **kwargs) -> str:
    """에러 메시지 포맷팅"""
    try:
        template = ERROR_MESSAGES[error_type][error_key]
        return template.format(**kwargs)
    except (KeyError, ValueError):
        return f"알 수 없는 오류가 발생했습니다. ({error_type}: {error_key})"