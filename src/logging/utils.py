"""로깅 유틸리티 함수"""
import os
import logging
from datetime import datetime
from enum import Enum, auto
from typing import Optional, Callable, Any, List
from dataclasses import dataclass
from pathlib import Path

class LogLevel(Enum):
    """로그 레벨 정의"""
    DEBUG = auto()      # 디버깅용 상세 정보
    INFO = auto()       # 일반적인 정보
    SUCCESS = auto()    # 성공 메시지
    WARNING = auto()    # 경고
    ERROR = auto()      # 오류
    CRITICAL = auto()   # 심각한 오류

@dataclass
class LogMessage:
    """로그 메시지 데이터 클래스"""
    level: LogLevel
    message: str
    timestamp: datetime = datetime.now()
    emoji: Optional[str] = None
    details: Optional[str] = None

# 레벨별 이모지 매핑
LEVEL_EMOJIS = {
    LogLevel.DEBUG: "🔍",
    LogLevel.INFO: "ℹ️",
    LogLevel.SUCCESS: "✅",
    LogLevel.WARNING: "⚠️",
    LogLevel.ERROR: "⛔",
    LogLevel.CRITICAL: "🚨"
}

# 레벨별 로깅 함수 타입
LogFunction = Callable[[str, Optional[Any]], None]

def create_file_logger(log_dir: str = "logs") -> logging.Logger:
    """파일 로거 생성"""
    # 로그 디렉토리 생성
    os.makedirs(log_dir, exist_ok=True)
    
    # 로거 설정
    logger = logging.getLogger("AppiumScriptRunner")
    logger.setLevel(logging.DEBUG)
    
    # 이미 핸들러가 있다면 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 파일 핸들러 추가
    log_file = Path(log_dir) / f"app_{datetime.now():%Y%m%d_%H%M%S}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def create_log_functions(gui_callback: Optional[Callable[[str], None]] = None,
                        file_logger: Optional[logging.Logger] = None) -> dict[LogLevel, LogFunction]:
    """레벨별 로깅 함수 생성"""
    
    def create_log_function(level: LogLevel) -> LogFunction:
        def log_func(message: str, details: Any = None) -> None:
            # 로그 메시지 생성
            emoji = LEVEL_EMOJIS.get(level, "")
            full_message = f"{emoji} {message}" if emoji else message
            
            # GUI 로깅
            if gui_callback:
                gui_callback(full_message)
                if details:
                    gui_callback(f"   {details}")
            
            # 파일 로깅
            if file_logger:
                # 로깅 레벨 매핑
                log_level = {
                    LogLevel.DEBUG: logging.DEBUG,
                    LogLevel.INFO: logging.INFO,
                    LogLevel.SUCCESS: logging.INFO,
                    LogLevel.WARNING: logging.WARNING,
                    LogLevel.ERROR: logging.ERROR,
                    LogLevel.CRITICAL: logging.CRITICAL
                }.get(level, logging.INFO)
                
                file_logger.log(log_level, message)
                if details:
                    file_logger.log(log_level, f"Details: {details}")
        
        return log_func
    
    # 각 레벨별 로깅 함수 생성
    return {
        level: create_log_function(level)
        for level in LogLevel
    }

def format_log_message(msg: LogMessage) -> str:
    """로그 메시지 포맷팅"""
    emoji = msg.emoji or LEVEL_EMOJIS.get(msg.level, "")
    timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    message = f"{emoji} {msg.message}" if emoji else msg.message
    
    if msg.details:
        return f"[{timestamp}] {message}\n   {msg.details}"
    return f"[{timestamp}] {message}"

def create_log_history() -> List[LogMessage]:
    """로그 히스토리 생성"""
    return []

def add_to_history(history: List[LogMessage], message: LogMessage) -> None:
    """로그 히스토리에 메시지 추가"""
    history.append(message)