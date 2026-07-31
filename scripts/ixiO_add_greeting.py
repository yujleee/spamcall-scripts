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
from utils.util import find, click
from datetime import datetime


def _dump_debug_state(driver, tag):
    """실패 시점의 화면 상태(스크린샷 + page_source)를 debug/ 폴더에 저장한다."""
    debug_dir = os.path.join(BASE_DIR, "debug")
    os.makedirs(debug_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = os.path.join(debug_dir, f"{tag}_{stamp}")
    try:
        driver.get_screenshot_as_file(f"{base_path}.png")
    except Exception:
        pass
    try:
        with open(f"{base_path}.xml", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
    except Exception:
        pass
    return base_path


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

            try:
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
                if is_ios:
                    input_field.send_keys(greeting_word)
                else:
                    # 이 바텀시트의 EditText는 표준 setText(send_keys)에 반응하지 않아
                    # InvalidElementStateException이 발생한다. UiAutomator2의 IME
                    # 입력 제스처(mobile: type)를 사용해야 정상 입력된다.
                    driver.execute_script('mobile: type', {'text': greeting_word})

                if not is_ios:
                    # 뒤로가기 키(keycode 4)는 키보드가 아직 안 떠 있는 타이밍에
                    # 눌리면 키보드 대신 바텀시트 자체를 닫아버리는 레이스가 있어
                    # 키보드 전용 종료 명령을 사용한다.
                    if driver.is_keyboard_shown():
                        driver.hide_keyboard()

                if is_ios:
                    click(driver, AppiumBy.ACCESSIBILITY_ID, '확인')
                else:
                    # 키보드 닫힘 애니메이션으로 레이아웃이 막 바뀐 직후라
                    # 찾은 요소가 클릭 시점에 stale해지는 경우가 있어 재시도한다.
                    click(driver, AppiumBy.ANDROID_UIAUTOMATOR,
                          'new UiSelector().text("확인")')

                time.sleep(0.5)

                print(f"✅ 인사말 #{i} 추가 완료: '{greeting_word}'")
                time.sleep(0.8)
            except Exception:
                debug_path = _dump_debug_state(driver, f"greeting_{i}_fail")
                print(f"🧩 실패 시점 화면 저장: {debug_path}.png / {debug_path}.xml")
                raise

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
