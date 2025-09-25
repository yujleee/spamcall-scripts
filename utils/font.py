import platform
from src.config import get_config

def get_log_font():
    """현재 OS에 맞는 로그용 폰트 반환"""
    os_name = platform.system()
    os_fonts = get_config('gui.fonts.os_specific')
    font_config = os_fonts.get(os_name, os_fonts['default'])
    return (font_config['family'], font_config['size'])