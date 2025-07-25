import os
import time
import random
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from utils.util import find

# ===============================================================
# 📱 모바일 매니저 차단 단어 관리 차단 최대 갯수(200~300개) 확인 스크립트
# - 랜덤한 한국어 단어를 최대 갯수까지 자동으로 추가 후 최대 차단 갯수 팝업을 확인함
# ===============================================================
# - 최종 수정일: 2025-06-24
# ===============================================================
# - ✨ 실행 전 확인 사항
# 0. 동일 폴더 내 random_korean_words.txt 파일 존재 필수!
# 1. 앱 실행 > 설정 > 스팸 차단/예외 설정 > 차단 단어 관리 or 차단하지 않을 단어 관리 진입 후 스크립트 실행
        



def add_spam_words():
    caps = {
        "platformName": "Android",
        "automationName": "UiAutomator2",
        "deviceName": "R3CRB0KPP1", # 연결한 디바이스 명 변경 필요
        "platformVersion": "14",
        "appPackage": "lgt.call", 
        "appActivity": "lgt.call.Main",
        "autoGrantPermissions": True,
        "noReset": True,        # 앱 데이터 초기화 방지
        "fullReset": False      # 앱 제거 후 재설치 방지
    }

    options = UiAutomator2Options().load_capabilities(caps)
    driver = webdriver.Remote("http://localhost:4723", options=options)

    try:

        # 차단(300)/차단하지 않을 단어(200)에 따라 숫자 카운트 선택 
        appbar_title = find(driver, AppiumBy.ID, 'lgt.call:id/appbar_title')
        appbar_title_text = appbar_title.text
        count = 200 if appbar_title_text == '차단하지 않을 단어 관리' else 300

        # 2자 이상 한국어 단어 랜덤으로 선택
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "random_korean_words.txt")

        with open(file_path, "r", encoding="utf-8") as f:
            words = [line.strip() for line in f if 2 <= len(line.strip())]

            words = list(set(words)) # 중복제거
            selected_words = random.sample(words, min(count, len(words)))

        print(f"✅ 총 {len(selected_words)}개의 단어가 선택됨")

        # 단어 추가 루프
        for word in selected_words:

            input_field = find(driver, AppiumBy.ID, 'lgt.call:id/edit_text')
            input_field.click()

            input_field.send_keys(word)

            btn_register = find(driver, AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("등록하기")')
            btn_register.click()

            print(f"🕹️ 단어 '{word}' 등록 완료!")
            
            time.sleep(0.5)
            

        # 차단 갯수 초과 팝업 확인
        list_size = find(driver, AppiumBy.ID, 'lgt.call:id/list_size')
        list_size_text = list_size.text
        list_length = int(list_size_text)

        if list_length == count:

            input_field.click()
            input_field.send_keys('팝업확인')

            btn_register.click()
                        
            try:
                popup = find(driver, AppiumBy.ID, 'lgt.call:id/title')
                print("✅ 팝업 노출 확인:", popup.text)            
            
                btn_popupClose = find(driver, AppiumBy.ID, 'lgt.call:id/confirmButton')
                btn_popupClose.click()

                print("✅ 팝업 닫기 완료! 스크립트 실행 끝!")

            except Exception as e:
                    print(f"❌ 팝업 미노출 또는 닫기 실패: {e}")


    finally:
        driver.quit()

if __name__ == "__main__":
    add_spam_words()