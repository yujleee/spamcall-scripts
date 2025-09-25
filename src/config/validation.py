"""설정값 검증 함수"""
from typing import Any, Dict, List, Optional, Tuple

# 필수 설정값 정의
REQUIRED_CONFIG = {
    'paths': {
        'scripts_dir': str,
        'resources_dir': str,
        'logs_dir': str
    },
    'gui': {
        'log_window': {
            'height': int,
            'background_color': str,
            'foreground_color': str,
            'cursor_color': str
        },
        'fonts': {
            'os_specific': {
                'Darwin': {
                    'family': str,
                    'size': int
                },
                'Windows': {
                    'family': str,
                    'size': int
                },
                'default': {
                    'family': str,
                    'size': int
                }
            },
            'emoji': {
                'family': str,
                'size': int
            }
        },
        'padding': {
            'default': str,
            'log_frame': str
        }
    }
}

def validate_config(config: Dict[str, Any], required: Dict[str, Any], path: str = '') -> List[str]:
    """재귀적으로 설정값 유효성 검증"""
    errors: List[str] = []
    
    for key, expected_type in required.items():
        current_path = f"{path}.{key}" if path else key
        
        # 키가 존재하는지 확인
        if key not in config:
            errors.append(f"필수 설정 '{current_path}'가 없습니다")
            continue
            
        value = config[key]
        
        # 중첩된 설정 객체인 경우 재귀적으로 검증
        if isinstance(expected_type, dict):
            if not isinstance(value, dict):
                errors.append(
                    f"'{current_path}'는 객체여야 합니다"
                )
                continue
            errors.extend(validate_config(value, expected_type, current_path))
            
        # 기본 타입인 경우 타입 검증
        else:
            if not isinstance(value, expected_type):
                errors.append(
                    f"'{current_path}'의 타입이 잘못되었습니다. "
                    f"예상: {expected_type.__name__}, "
                    f"실제: {type(value).__name__}"
                )
                
            # 특정 필드에 대한 추가 검증
            if key == 'height' and isinstance(value, int):
                if value <= 0:
                    errors.append(
                        f"'{current_path}'는 양수여야 합니다"
                    )
            elif key in ['background_color', 'foreground_color', 'cursor_color']:
                if not isinstance(value, str) or not value.startswith('#'):
                    errors.append(
                        f"'{current_path}'는 '#'으로 시작하는 색상 코드여야 합니다"
                    )
            elif key == 'size' and isinstance(value, int):
                if value <= 0:
                    errors.append(
                        f"'{current_path}'는 양수여야 합니다"
                    )
                    
    return errors