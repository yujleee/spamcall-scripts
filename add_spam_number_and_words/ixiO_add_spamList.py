import time
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from utils.util import find

# ======================================================
# 익시오 차단 예외 번호 최대 갯수 확인 스크립트
# ======================================================
# - ✨ 실행 전 확인 사항
# - 익시오 앱 진입 후 실행


def add_spam_number():
    caps = {
        "platformName": "Android",
        "automationName": "UiAutomator2",
        "deviceName": "R3CX20TEEMV",
        "platformVersion": "14",
        "appPackage": "com.lguplus.aicallagent",
        "appActivity": "com.lguplus.aicallagent.MainActivity",
        "autoGrantPermissions": True,
        "noReset": True,        # 앱 데이터 초기화 방지
        "fullReset": False      # 앱 제거 후 재설치 방지
    }

    options = UiAutomator2Options().load_capabilities(caps)

    driver = webdriver.Remote("http://localhost:4723", options=options)

    try:

        # # 1. 설정 탭으로 이동
        # btn_setting = find(driver, AppiumBy.ACCESSIBILITY_ID, "설정")
        # btn_setting.click()

        # # 2. 스팸 알림 및 수신 차단 탭 이동 > 차단 예외 번호 탭 이동
        # menu_spam_noti = find(driver, AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("스팸 알림 및 수신 차단")')
        # menu_spam_noti.click()

        # menu_spam_exception = find(driver, AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("차단 예외 번호")')
        # menu_spam_exception.click()

        # 3. 1부터 600까지 반복
        for i in range(601):

            try:

                # 세 자리 숫자로 입력
                padded_number = f"{i:03}" 

                # 4. 꼭 받아야 할 전화번호를 입력하세요 텍스트 필드 선택
                input_field = find(driver, AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.EditText").instance(0)')
                input_field.click()

                # 5. 숫자 입력
                input_field.send_keys(str(padded_number))

                # 6. 등록버튼 선택
                btn_register = find(driver, AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("등록")')
                btn_register.click()

                print(f"🕹️  스팸번호 {i} 등록 완료")
                time.sleep(0.5)

                # 추가 동작
                # 번호 리스트 뷰에 해당 번호가 추가되었는 지 확인
                # last_items = driver.find_elements(By.ID, "com.example:id/list_item_text")

#                if not last_items or padded_number != last_items[-1].text:
 #                   raise Exception(f"❌ 번호 {padded_number}가 리스트에 제대로 추가되지 않았습니다.")

            # 에러케이스 추가
            except Exception as e:
                print(f"🚨 에러 발생! 현재 번호: {padded_number}")
                print(f"에러 메시지: {e}")
                break  # 반복 중단

        # 추가 동작
        # 005 이후부터 등록 후 리스트 뷰 최상단으로 스크롤



        # 7. 더이상 추가가 불가능하다는 팝업 노출 확인 후 종료 

    finally:
        driver.quit()

if __name__ == "__main__":
    add_spam_number()