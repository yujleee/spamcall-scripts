import os
import time
import random
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import TimeoutException
from utils.util import find
from datetime import datetime


# ===============================================================
# 📱 LGU+ 스팸전화알림 차단 단어 추가 스크립트
# - 랜덤한 한국어 단어를 최대 갯수까지 자동으로 추가 후 최대 차단 갯수 팝업을 확인함
# ===============================================================
# - ✨ 실행 전 확인 사항
# 0. 동일 폴더 내 random_korean_words.txt 파일 존재 필수!
# 1. 앱 실행 > 설정 > 스팸 차단/예외 설정 > 차단 단어 관리 or 차단하지 않을 단어 관리 진입 후 스크립트 실행
        



def add_spam_words():
    device_name = os.environ.get('APPIUM_DEVICE_NAME')
    platform_version = os.environ.get('APPIUM_PLATFORM_VERSION')
    word_count = int(os.environ.get('WORD_COUNT'))

    if not device_name or not platform_version:
        print("❌ 디바이스 정보가 설정되지 않았습니다.")
        print("GUI에서 실행해주세요.")
        sys.exit(1)

    caps = {
        "platformName": "Android",
        "automationName": "UiAutomator2",
        "deviceName": device_name, 
        "platformVersion": platform_version,
        "appPackage": "com.lguplus.blocksmishing", 
        "appActivity": "com.lguplus.blocksmishing.HybridMainActivity",
        "autoGrantPermissions": True,
        "noReset": True,        # 앱 데이터 초기화 방지
        "fullReset": False      # 앱 제거 후 재설치 방지
    }

    options = UiAutomator2Options().load_capabilities(caps)
    driver = webdriver.Remote("http://localhost:4723", options=options)

    try:
        start_time = datetime.now()
        print(f"🔥 스크립트 시작: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # 2자 이상 한국어 단어 랜덤으로 선택
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "random_korean_words.txt")

        with open(file_path, "r", encoding="utf-8") as f:
            words = [line.strip() for line in f if 2 <= len(line.strip())]

            words = list(set(words)) # 중복제거
            selected_words = random.sample(words, min(word_count, len(words)))

        print(f"✅ 총 {len(selected_words)}개의 단어가 선택됨")

        # 단어 추가 루프
        for word in selected_words:

            btn_add_text = find(driver, AppiumBy.ACCESSIBILITY_ID, '문구추가')
            btn_add_text.click()

            input_field = find(driver, AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("addText")')
            input_field.click()

            input_field.send_keys(word)

            btn_register = find(driver, AppiumBy.ACCESSIBILITY_ID, '등록')
            btn_register.click()

            time.sleep(0.3)

            # 최대 등록 개수 팝업이 뜨면 확인을 누르고 반복을 종료
            try:
                btn_popup_confirm = find(
                    driver,
                    AppiumBy.ACCESSIBILITY_ID,
                    '확인',
                    timeout=1
                )
                btn_popup_confirm.click()
                print("✅ 최대 등록 개수 팝업 확인 완료. 스크립트를 종료합니다.")
                break
            except TimeoutException:
                pass

            print(f"🕹️ 단어 '{word}' 등록 완료!")

        end_time = datetime.now()
        print(f"🔥 스크립트 종료: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔥 총 소요 시간: {end_time - start_time}")
    finally:
        driver.quit()

if __name__ == "__main__":
    add_spam_words()
