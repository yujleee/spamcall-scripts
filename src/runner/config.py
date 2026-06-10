from pathlib import Path

# 파일명 → {표시명, 지원 플랫폼} 매핑
SCRIPT_MAPPING = {
    "ixiO_add_spamList.py": {
        "display": "익시오 - 스팸 번호 추가",
        "platforms": ["android", "ios"],
    },
    "ixiO_add_spam_words.py": {
        "display": "익시오 - 스팸 단어 추가",
        "platforms": ["android"],
    },
    "mobileManager_add_spam_number.py": {
        "display": "모바일매니저 - 스팸 번호 추가",
        "platforms": ["android"],
    },
    "spamcallnoti_add_spam_number.py": {
        "display": "스팸전화알림 - 스팸 번호 추가",
        "platforms": ["android"],
    },
    "mobileManager_add_spam_words.py": {
        "display": "모바일매니저 - 스팸 단어 추가",
        "platforms": ["android"],
    },
}


def get_available_scripts(platform="android"):
    """지정한 플랫폼을 지원하고 실제로 존재하는 스크립트 반환 (표시명 → 파일명)"""
    scripts_dir = Path("scripts")
    if not scripts_dir.exists():
        return {}

    return {
        info["display"]: filename
        for filename, info in SCRIPT_MAPPING.items()
        if platform in info["platforms"] and (scripts_dir / filename).exists()
    }
