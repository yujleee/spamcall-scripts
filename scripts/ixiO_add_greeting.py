import re
import time
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from utils.util import find
from datetime import datetime


def add_greeting():
    device_name = os.environ.get('APPIUM_DEVICE_NAME')
    platform_version = os.environ.get('APPIUM_PLATFORM_VERSION')
    platform_name = os.environ.get('APPIUM_PLATFORM_NAME', 'android').lower()
    start_num = int(os.environ.get('START_NUM', '1'))
    end_num = int(os.environ.get('END_NUM', '97'))

    if not device_name or not platform_version:
        print("❌ 디바이스 정보가 설정되지 않았습니다.")
        print("GUI에서 실행해주세요.")
        sys.exit(1)

    is_ios = platform_name == 'ios'

    if is_ios:
        caps = {
            "platformName": "iOS",
            "automationName": "XCUITest",
            "udid": device_name,
            "deviceName": "iPhone",
            "platformVersion": platform_version,
            "bundleId": "com.lguplus.aicallagent",
            "noReset": True,
            "fullReset": False,
        }
        options = XCUITestOptions().load_capabilities(caps)
    else:
        caps = {
            "platformName": "Android",
            "automationName": "UiAutomator2",
            "deviceName": device_name,
            "platformVersion": platform_version,
            "appPackage": "com.lguplus.aicallagent",
            "appActivity": "com.lguplus.aicallagent.MainActivity",
            "autoGrantPermissions": True,
            "noReset": True,
            "fullReset": False,
        }
        options = UiAutomator2Options().load_capabilities(caps)

    driver = webdriver.Remote("http://localhost:4723", options=options)

    try:
        start_time = datetime.now()
        print(f"🔥 스크립트 시작: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        for i in range(start_num, end_num + 1):
            print(f"🔁 {i - start_num + 1}/{end_num - start_num + 1}번째 인사말 추가")

            if is_ios:
                btn_greeting = find(driver, AppiumBy.ACCESSIBILITY_ID, '인사말 추가')
            else:
                btn_greeting = find(driver, AppiumBy.ANDROID_UIAUTOMATOR,
                                   'new UiSelector().text("인사말 추가")')
            btn_greeting.click()

            greeting_word = f"인사말 추가 테스트 {i}"

            if is_ios:
                input_field = find(driver, AppiumBy.ACCESSIBILITY_ID, '인사말을 입력하세요')
            else:
                try:
                    input_field = find(driver, AppiumBy.ANDROID_UIAUTOMATOR,
                                       'new UiSelector().text("인사말을 입력하세요")')
                                      
                except Exception:
                    input_field = find(driver, AppiumBy.ANDROID_UIAUTOMATOR,
                                        'new UiSelector().className("android.widget.EditText").instance(1)')
            input_field.click()
            input_field.send_keys(greeting_word)

            if not is_ios:
                driver.press_keycode(4)

            if is_ios:
                btn_confirm = find(driver, AppiumBy.ACCESSIBILITY_ID, '확인')
            else:
                btn_confirm = find(driver, AppiumBy.ANDROID_UIAUTOMATOR,
                                    'new UiSelector().text("확인")')
            btn_confirm.click()

           
            time.sleep(0.5)

            print(f"✅ 인사말 #{i} 추가 완료: '{greeting_word}'")
            time.sleep(0.8)

        if is_ios:
            btn_save = find(driver, AppiumBy.ACCESSIBILITY_ID, '저장')
        else:
            btn_save = find(driver, AppiumBy.ANDROID_UIAUTOMATOR,
                                'new UiSelector().text("저장")')
        btn_save.click()
        end_time = datetime.now()
        print(f"🔥 스크립트 종료: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔥 총 소요 시간: {end_time - start_time}")

    finally:
        driver.quit()


if __name__ == "__main__":
    add_greeting()
