from pathlib import Path

SCRIPT_MAPPING = {
    "ixiO_add_spamList.py": "익시오 - 스팸 번호 추가",
    "ixiO_add_spam_words.py": "익시오 - 스팸 단어 추가",
    "mobileManager_add_spam_number.py": "모바일매니저 - 스팸 번호 추가",
    "spamcallnoti_add_spam_number.py": "스팸전화알림 - 스팸 번호 추가",
    "mobileManager_add_spam_words.py": "모바일매니저 - 스팸 단어 추가",
}


def get_available_scripts():
    """scripts 폴더에 실제로 존재하는 스크립트만 반환 (표시명 → 파일명)"""
    scripts_dir = Path("scripts")
    if not scripts_dir.exists():
        return {}

    return {
        display_name: filename
        for filename, display_name in SCRIPT_MAPPING.items()
        if (scripts_dir / filename).exists()
    }
