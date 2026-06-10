import os
import re
import time
import random
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from utils.util import find
from datetime import datetime

# ===============================================================
# 📱 익시오 차단 단어 관리 차단 최대 갯수(200~300개) 확인 스크립트
# - 랜덤한 한국어 단어를 최대 갯수까지 자동으로 추가 후 최대 차단 갯수 팝업을 확인함
# ===============================================================
# - 최종 수정일: 2025-06-24
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
        "appPackage": "com.lguplus.aicallagent",
        "appActivity": "com.lguplus.aicallagent.MainActivity",
        "autoGrantPermissions": True,
        "noReset": True,
        "fullReset": False
    }
    options = UiAutomator2Options().load_capabilities(caps)

    driver = webdriver.Remote("http://localhost:4723", options=options)

    try:
        start_time = datetime.now()
        print(f"🔥 스크립트 시작: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # 차단(300)/차단하지 않을 단어(200)에 따라 숫자 카운트 선택
        try:
            find(driver, AppiumBy.XPATH, '//android.widget.TextView[@text="차단하지 않을 단어"]')
            max_count = 200
        except:
            max_count = 300

        # 2자 이상 한국어 단어 랜덤으로 선택
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "random_korean_words.txt")

        with open(file_path, "r", encoding="utf-8") as f:
            words = [line.strip() for line in f if 2 <= len(line.strip())]
            words = list(set(words))
            selected_words = random.sample(words, min(word_count, len(words)))

        print(f"✅ 총 {len(selected_words)}개의 단어가 선택됨")

        for word in selected_words:
            input_field = find(driver, AppiumBy.CLASS_NAME, 'android.widget.EditText')
            input_field.click()
            input_field.send_keys(word)

            btn_register = find(driver, AppiumBy.XPATH, '//android.widget.TextView[@text="추가"]')
            btn_register.click()

            print(f"🕹️ 단어 '{word}' 등록 완료!")
            time.sleep(0.5)

        # 차단 갯수 초과 팝업 확인
        list_size = find(driver, AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textStartsWith("전체")')
        list_size_text = list_size.text
        list_length = int(re.search(r'(\d+)/', list_size_text).group(1))
        print(f"현재 등록된 단어 갯수: {list_length}")

        if list_length >= max_count:
            input_field.click()
            input_field.send_keys('팝업확인')
            btn_register.click()

            try:
                popup = find(driver, AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("더 이상 추가할 수 없어요")')
                print("✅ 팝업 노출 확인:", popup.text)

                btn_popupClose = find(driver, AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.view.View").instance(3)')
                btn_popupClose.click()
                print("✅ 팝업 닫기 완료! 스크립트 실행 끝!")

            except Exception as e:
                print(f"❌ 팝업 미노출 또는 닫기 실패: {e}")

        end_time = datetime.now()
        print(f"🔥 스크립트 종료: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔥 총 소요 시간: {end_time - start_time}")

    finally:
        driver.quit()

if __name__ == "__main__":
    add_spam_words()
