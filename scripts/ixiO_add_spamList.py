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

# ======================================================
# 익시오 차단 예외 번호 최대 갯수 확인 스크립트
# ======================================================
# - ✨ 실행 전 확인 사항
# - 익시오 앱 진입 > 스팸 차단 번호 추가 화면까지 진입한 상태에서 실행


def add_spam_number():
    device_name = os.environ.get('APPIUM_DEVICE_NAME')
    platform_version = os.environ.get('APPIUM_PLATFORM_VERSION')
    platform_name = os.environ.get('APPIUM_PLATFORM_NAME', 'android').lower()
    start_num = int(os.environ.get('START_NUM'))
    end_num = int(os.environ.get('END_NUM'))

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
            padded_number = f"070{i:03}"

            if is_ios:
                input_field = find(driver, AppiumBy.CLASS_NAME, 'XCUIElementTypeTextField')
            else:
                input_field = find(driver, AppiumBy.ANDROID_UIAUTOMATOR,
                                   'new UiSelector().className("android.widget.EditText").instance(0)')
            input_field.click()
            input_field.send_keys(str(padded_number))

            # 키보드 닫기 (Android만)
            if not is_ios:
                driver.press_keycode(4)

            if is_ios:
                btn_register = find(driver, AppiumBy.ACCESSIBILITY_ID, '등록')
            else:
                btn_register = find(driver, AppiumBy.ANDROID_UIAUTOMATOR,
                                    'new UiSelector().text("등록")')
            btn_register.click()

            if is_ios:
                all_texts = driver.find_elements(AppiumBy.CLASS_NAME, 'XCUIElementTypeStaticText')
                current_num = 0
                for idx, el in enumerate(all_texts):
                    lbl = el.get_attribute('label') or ''
                    if lbl.startswith('/') and idx > 0:
                        prev = all_texts[idx - 1].get_attribute('label') or ''
                        if prev.strip().isdigit():
                            current_num = int(prev.strip())
                            break
            else:
                registered_num_element = find(driver, AppiumBy.ANDROID_UIAUTOMATOR,
                                              'new UiSelector().textStartsWith("전체")')
                full_text = registered_num_element.text
                current_num = int(re.search(r'(\d+)/', full_text).group(1))

            if current_num >= 600:
                try:
                    if is_ios:
                        popup = find(driver, AppiumBy.ACCESSIBILITY_ID, '더 이상 추가할 수 없어요')
                        print("✅ 팝업 노출 확인:", popup.text)
                        btn_popup_close = find(driver, AppiumBy.XPATH,
                                               '//XCUIElementTypeButton[@name="확인"]')
                    else:
                        popup = find(driver, AppiumBy.ANDROID_UIAUTOMATOR,
                                     'new UiSelector().text("더 이상 추가할 수 없어요")')
                        print("✅ 팝업 노출 확인:", popup.text)
                        btn_popup_close = find(driver, AppiumBy.ANDROID_UIAUTOMATOR,
                                               'new UiSelector().text("확인")')
                    btn_popup_close.click()
                    print("✅ 팝업 닫기 완료! 스크립트 실행 끝!")

                except Exception as e:
                    print(f"❌ 팝업 미노출 또는 닫기 실패: {e}")
                break

            try:
                if padded_number.startswith("070"):
                    display_text = f"070-{padded_number[3:]}"
                elif padded_number.startswith("02") and len(padded_number) == 3:
                    display_text = f"02-{padded_number[2]}"
                else:
                    display_text = padded_number

                if is_ios:
                    find(driver, AppiumBy.IOS_PREDICATE,
                         f'label CONTAINS "{display_text}"', timeout=3)
                else:
                    xpath = f'//android.widget.TextView[contains(@text, "{display_text}")]'
                    find(driver, AppiumBy.XPATH, xpath, timeout=3)

            except Exception:
                print(f"🕹️ ❗️ {display_text} 등록 실패 또는 시간 초과")
                break

            print(f"  스팸번호 {i} 등록 완료")
            time.sleep(0.5)

        end_time = datetime.now()
        print(f"🔥 스크립트 종료: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔥 총 소요 시간: {end_time - start_time}")

    finally:
        driver.quit()


if __name__ == "__main__":
    add_spam_number()
