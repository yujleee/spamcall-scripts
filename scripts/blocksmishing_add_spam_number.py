import time
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import TimeoutException
from utils.util import find
from datetime import datetime


# ===============================================================
# 📱 LGU+ 스팸전화알림 번호 추가 스크립트
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

        for i in range(start_num, end_num + 1):

            # 세 자리 숫자로 입력
            padded_number = f"{i:03}" 

            btn_add_number = find(driver, AppiumBy.ACCESSIBILITY_ID, '번호추가')
            btn_add_number.click()

            input_field = find(driver, AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("addNum")')
            input_field.click()

            input_field.send_keys(str(padded_number))

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

            print(f"🕹️ 번호 {i} 등록 완료!")

        end_time = datetime.now()
        print(f"🔥 스크립트 종료: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔥 총 소요 시간: {end_time - start_time}")   
        
    finally:
        driver.quit()

if __name__ == "__main__":
    add_spam_number()
