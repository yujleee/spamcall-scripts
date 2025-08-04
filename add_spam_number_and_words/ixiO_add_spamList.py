import platform
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

# ======================================================
# 익시오 차단 예외 번호 최대 갯수 확인 스크립트
# ======================================================
# - ✨ 실행 전 확인 사항
# - 익시오 앱 진입 > 스팸 차단 번호 추가 화면까지 진입한 상태에서 실행


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
        
        start_time = datetime.now()
        print(f"🔥 스크립트 시작: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # 3. 1부터 600까지 반복
        for i in range(598,601):

                # 세 자리 숫자로 입력
                padded_number = f"{i:03}" 

                # 4. 꼭 받아야 할 전화번호를 입력하세요 텍스트 필드 선택
                input_field = find(driver, AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.EditText").instance(0)')
                input_field.click()

                # 5. 숫자 입력
                input_field.send_keys(str(padded_number))
                
                # mac OS일 경우 키패드 내리기
                if platform.system() == 'Darwin':
                    driver.hide_keyboard()

                # 6. 등록버튼 선택
                btn_register = find(driver, AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("등록")')
                btn_register.click()
                
                if i >= 600:
                    try:
                        popup = find(driver, AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("더 이상 추가할 수 없어요")')
                        print("✅ 팝업 노출 확인:", popup.text)            
                    
                        btn_popupClose = find(driver, AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("확인")')
                        btn_popupClose.click()

                        print("✅ 팝업 닫기 완료! 스크립트 실행 끝!")
                        break

                    except Exception as e:
                        print(f"❌ 팝업 미노출 또는 닫기 실패: {e}")
                        break 
                
                try:
                    xpath = f'//android.widget.TextView[@text="{padded_number}"]'
                    find(driver, AppiumBy.XPATH, xpath, timeout=5)
                
                except Exception:
                    print(f"🕹️ ❗️ {padded_number} 등록 실패 또는 시간 초과")
                    break

    
                print(f"  스팸번호 {i} 등록 완료")
                time.sleep(0.5)

            
        
        # 종료 시각 및 소요 시간 기록
        end_time = datetime.now()
        print(f"🔥 스크립트 종료: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔥 총 소요 시간: {end_time - start_time}")

    finally:
        driver.quit()

if __name__ == "__main__":
    add_spam_number()