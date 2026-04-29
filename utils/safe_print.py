def safe_print(text):
    """UnicodeEncodeError 없이 안전하게 출력"""
    try:
        print(text)
    except UnicodeEncodeError:
        try:
            safe_text = str(text).encode('cp949', errors='replace').decode('cp949')
            print(safe_text)
        except Exception:
            print("[출력 오류: 특수문자 포함]")
