"""로깅 설정 및 초기화"""
import os
from typing import Optional, Callable, Dict
from .utils import (
    LogLevel,
    LogFunction,
    create_file_logger,
    create_log_functions
)

def setup_logging(gui_callback: Optional[Callable[[str], None]] = None,
                 log_dir: str = "logs") -> Dict[LogLevel, LogFunction]:
    """로깅 시스템 설정"""
    # 로그 디렉토리가 없으면 생성
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 파일 로거 생성
    file_logger = create_file_logger(log_dir)
    
    # 로깅 함수들 생성
    log_functions = create_log_functions(gui_callback, file_logger)
    
    return log_functions

def create_logger(gui_callback: Optional[Callable[[str], None]] = None) -> Dict[LogLevel, LogFunction]:
    """로거 생성 함수"""
    log_functions = setup_logging(gui_callback)
    
    # 편의를 위해 일반적으로 사용되는 함수들을 별도로 추출
    debug = log_functions[LogLevel.DEBUG]
    info = log_functions[LogLevel.INFO]
    success = log_functions[LogLevel.SUCCESS]
    warning = log_functions[LogLevel.WARNING]
    error = log_functions[LogLevel.ERROR]
    critical = log_functions[LogLevel.CRITICAL]
    
    return {
        LogLevel.DEBUG: debug,
        LogLevel.INFO: info,
        LogLevel.SUCCESS: success,
        LogLevel.WARNING: warning,
        LogLevel.ERROR: error,
        LogLevel.CRITICAL: critical
    }