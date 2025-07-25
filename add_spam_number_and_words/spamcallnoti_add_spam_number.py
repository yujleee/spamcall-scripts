import time
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from utils.util import find

# ===============================================================
# 📱 스팸전화알림 번호 직접 차단 / 차단제외 번호 설정 최대 갯수 (100개) 확인 스크립트
# - 차단 번호 / 차단 제외 번호의 최대 갯수까지 자동으로 추가 후 최대 갯수 팝업 확인 및 새 번호 추가 확인
# ===============================================================
# - 최종 수정일: 2025-06-30
# ===============================================================
# - ✨ 실행 전 확인 사항
# - 앱 실행 > 안심설정 > 번호 직접 차단 or 차단제외 번호 설정 진입한 후 스크립트 실행



def add_spam_number():
    caps = {
        "platformName": "Android",
        "automationName": "UiAutomator2",
        "deviceName": "R3CRB0KPP1", # 연결한 디바이스 명 변경 필요
        "platformVersion": "14", # OS 다를 경우 변경 필요
        "appPackage": "com.lguplus.spamcallnoti", 
        "appActivity": "com.lguplus.spamcallnoti.activity.mainactivity.MainActivity",
        "autoGrantPermissions": True,
        "noReset": True,        # 앱 데이터 초기화 방지
        "fullReset": False      # 앱 제거 후 재설치 방지
    }

    options = UiAutomator2Options().load_capabilities(caps)

    driver = webdriver.Remote("http://localhost:4723", options=options)

    try:

        # 1부터 100까지 등록 (101은 팝업 확인용)
        for i in range(1, 102):

            # 세 자리 숫자로 입력
            padded_number = f"{i:03}" 

            btn_add_number = find(driver, AppiumBy.ACCESSIBILITY_ID, '시작번호 추가 버튼')
            btn_add_number.click()

            input_field = find(driver, AppiumBy.ID, 'com.lguplus.spamcallnoti:id/id_et_inputtxt')
            input_field.click()

            input_field.send_keys(str(padded_number))

            btn_register = find(driver, AppiumBy.ID, 'com.lguplus.spamcallnoti:id/id_btn_dialog_pos')
            btn_register.click()

            if i <= 100 :
                print(f"🕹️ 번호 {i} 등록 완료!")
            
            time.sleep(0.5)

           # 차단 갯수 초과 팝업 확인
            if i > 100:
                try:
                    popup = find(driver, AppiumBy.ID, 'com.lguplus.spamcallnoti:id/id_tv_dialog_content_center')
                    print("✅ 팝업 노출 확인:", popup.text)            
                
                    btn_popup_add = find(driver, AppiumBy.ID, 'com.lguplus.spamcallnoti:id/id_btn_dialog_pos')
                    btn_popup_add.click()

                    print("✅ 번호 추가 후 팝업 닫기 완료! 스크립트 실행 끝!")

                except Exception as e:
                       print(f"❌ 팝업 미노출 또는 닫기 실패: {e}")

            
    finally:
        driver.quit()

if __name__ == "__main__":
    add_spam_number()