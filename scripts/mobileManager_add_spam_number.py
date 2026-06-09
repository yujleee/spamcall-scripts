import time
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from utils.util import find
from datetime import datetime


# ===============================================================
# 📱 모바일 매니저 차단 번호 관리 차단 최대 갯수 (600개) 확인 스크립트
# - 차단 번호 / 차단하지 않을 번호의 최대 갯수까지 자동으로 추가 후 최대 갯수 팝업을 확인함
# ===============================================================
# - ✨ 실행 전 확인 사항
# - 앱 실행 > 설정 > 스팸 차단/예외 설정 > 차단 번호 관리 or 차단하지 않을 번호 관리 진입 후 스크립트 실행



def add_spam_number():
    device_name = os.environ.get('APPIUM_DEVICE_NAME')
    platform_version = os.environ.get('APPIUM_PLATFORM_VERSION')
    start_num = int(os.environ.get('START_NUM'))
    end_num = int(os.environ.get('END_NUM'))

    if not device_name or not platform_version:
        print("❌ 디바이스 정보가 설정되지 않았습니다.")
        print("GUI에서 실행해주세요.")
        sys.exit(1)

    caps = {
        "platformName": "Android",
        "automationName": "UiAutomator2",
        "deviceName": device_name,
        "platformVersion": platform_version,
        "appPackage": "lgt.call", 
        "appActivity": "lgt.call.Main",
        "autoGrantPermissions": True,
        "noReset": True,        # 앱 데이터 초기화 방지
        "fullReset": False      # 앱 제거 후 재설치 방지
    }

    options = UiAutomator2Options().load_capabilities(caps)

    driver = webdriver.Remote("http://localhost:4723", options=options)

    try:

        start_time = datetime.now()
        print(f"🔥 스크립트 시작: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        for i in range(start_num, end_num + 1):

            # 세 자리 숫자로 입력
            padded_number = f"{i:03}" 

            input_field = find(driver, AppiumBy.ID, 'lgt.call:id/spam_number_allow_block_edit_number')
            input_field.click()

            input_field.send_keys(str(padded_number))

            btn_register = find(driver, AppiumBy.ID, 'lgt.call:id/spam_number_allow_block_register_button')
            btn_register.click()

            if i <= end_num :
                print(f"🕹️ 번호 {i} 등록 완료!")
            
            time.sleep(0.3)

           # 차단 갯수 초과 팝업 확인
            list_count_field = find(driver, AppiumBy.ID, 'lgt.call:id/spam_number_block_list_count')
            list_count = int(list_count_field.text)

            if list_count >= 600:
                try:
                    popup = find(driver, AppiumBy.ID, 'lgt.call:id/title')
                    print("✅ 팝업 노출 확인:", popup.text)            
                
                    btn_popupClose = find(driver, AppiumBy.ID, 'lgt.call:id/confirmButton')
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
    add_spam_number()