"""설정 관리 유틸리티 함수"""
import os
import json
from typing import Any, Dict, Optional
from .validation import validate_config, REQUIRED_CONFIG

# 전역 설정 저장소
_config: Optional[Dict[str, Any]] = None

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """설정 파일을 로드하고 전역 설정 저장소에 저장"""
    global _config
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"설정 파일을 찾을 수 없습니다: {config_path}"
        )
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            _config = json.load(f)
        
        # 설정값 유효성 검증
        errors = validate_config(_config, REQUIRED_CONFIG)
        if errors:
            raise ValueError(
                "설정값 검증 실패:\n" + "\n".join(f"- {err}" for err in errors)
            )
            
        return _config
    except json.JSONDecodeError as e:
        raise ValueError(f"설정 파일 형식이 잘못되었습니다: {e}")
    except Exception as e:
        raise Exception(f"설정 파일 로드 중 오류 발생: {e}")

def get_config(key: str = None) -> Any:
    """설정값 조회. key가 None이면 전체 설정 반환"""
    global _config
    
    if _config is None:
        _config = load_config()
    
    if key is None:
        return _config
        
    # 점(.) 구분자로 중첩된 키 접근 지원
    keys = key.split('.')
    value = _config
    for k in keys:
        try:
            value = value[k]
        except (KeyError, TypeError):
            raise KeyError(f"설정에서 '{key}' 키를 찾을 수 없습니다")
    
    return value

def set_config(key: str, value: Any) -> None:
    """설정값 변경"""
    global _config
    
    if _config is None:
        _config = load_config()
    
    keys = key.split('.')
    target = _config
    
    # 마지막 키를 제외한 모든 키에 대해 딕셔너리 생성
    for k in keys[:-1]:
        target = target.setdefault(k, {})
    
    # 마지막 키에 값 설정
    target[keys[-1]] = value