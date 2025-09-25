"""에러 처리 함수"""
import sys
from typing import Optional, Callable, Any
from tkinter import messagebox
from .types import AppError, ErrorType, format_error_message

def create_error_handler(log_callback: Optional[Callable[[str], None]] = None):
    """에러 핸들러 생성"""
    def handle_error(error: AppError) -> None:
        """에러 처리"""
        # 에러 메시지 생성
        error_message = f"⛔ {error.message}"
        if error.details:
            error_message += f"\n\n{error.details}"
        
        # 로그에 기록
        if log_callback:
            log_callback(error_message)
            if error.original_error:
                log_callback(f"원인: {str(error.original_error)}")
        
        # 에러 타입에 따른 처리
        if error.type in [ErrorType.DEVICE_ERROR, ErrorType.SCRIPT_ERROR]:
            messagebox.showwarning("⚠️ 경고", error_message)
        elif error.type == ErrorType.ENVIRONMENT_ERROR:
            if messagebox.askretry("⚠️ 환경 설정 오류", error_message):
                return False  # 재시도
            else:
                sys.exit(1)
        else:
            messagebox.showerror("⛔ 오류", error_message)
        
        return True  # 에러 처리 완료
    
    return handle_error

def create_device_error(error_key: str, **kwargs) -> AppError:
    """디바이스 관련 에러 생성"""
    return AppError(
        type=ErrorType.DEVICE_ERROR,
        message=format_error_message(ErrorType.DEVICE_ERROR, error_key, **kwargs)
    )

def create_script_error(error_key: str, **kwargs) -> AppError:
    """스크립트 관련 에러 생성"""
    return AppError(
        type=ErrorType.SCRIPT_ERROR,
        message=format_error_message(ErrorType.SCRIPT_ERROR, error_key, **kwargs)
    )

def create_environment_error(error_key: str, **kwargs) -> AppError:
    """환경 설정 관련 에러 생성"""
    return AppError(
        type=ErrorType.ENVIRONMENT_ERROR,
        message=format_error_message(ErrorType.ENVIRONMENT_ERROR, error_key, **kwargs)
    )

def create_runtime_error(error_key: str, **kwargs) -> AppError:
    """실행 시간 에러 생성"""
    return AppError(
        type=ErrorType.RUNTIME_ERROR,
        message=format_error_message(ErrorType.RUNTIME_ERROR, error_key, **kwargs)
    )

def safe_execute(func: Callable[..., Any], error_handler: Callable[[AppError], bool], 
                default_return: Any = None, **kwargs) -> Any:
    """안전한 함수 실행"""
    try:
        return func(**kwargs)
    except Exception as e:
        error = AppError(
            type=ErrorType.UNKNOWN_ERROR,
            message=format_error_message(ErrorType.UNKNOWN_ERROR, "unknown", error=str(e)),
            original_error=e
        )
        error_handler(error)
        return default_return