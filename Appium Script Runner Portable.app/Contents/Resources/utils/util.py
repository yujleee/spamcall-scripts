from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# =============================================================
# ✨ 스크립트 진행에 필요한 유틸 함수
# - 최종 수정일: 2025-06-24
# =============================================================


# =============================================================
# - UI 단일 요소 찾는 함수
# - Args (매개변수) :
#       driver : Appium webDriver
#       by : AppiumBy
#       value : ID, Xpath, UIAUTOMATOR 등 Element 지정 값
# =============================================================
def find(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))

# =============================================================
# - UI 모든 요소 찾는 함수
# - Args (매개변수) :
#       driver : Appium webDriver
#       by : AppiumBy
#       value : ID, Xpath, UIAUTOMATOR 등 Element 지정 값
# =============================================================
def find_all(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((by, value)))