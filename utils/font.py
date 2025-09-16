import platform

OS_FONTS = {
    'Darwin': ('AppleSDGothicNeo', 12),      
    'Windows': ('Segoe UI Emoji', 10),    
}


def get_log_font():
    """현재 OS에 맞는 로그용 폰트 반환"""
    os_name = platform.system()
    return OS_FONTS.get(os_name, ('Segoe UI Emoji', 10))  # 기본값