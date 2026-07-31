import time

from selenium.common.exceptions import StaleElementReferenceException
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

# =============================================================
# - 요소를 찾아 클릭. 키보드 닫힘 등 직후의 레이아웃 변경으로
#   클릭 시점에 StaleElementReferenceException이 발생하면
#   요소를 다시 찾아 재시도한다.
# - Args (매개변수) :
#       driver : Appium webDriver
#       by : AppiumBy
#       value : ID, Xpath, UIAUTOMATOR 등 Element 지정 값
# =============================================================
def click(driver, by, value, timeout=10, retries=3, retry_delay=0.3):
    last_exc = None
    for _ in range(retries):
        try:
            find(driver, by, value, timeout=timeout).click()
            return
        except StaleElementReferenceException as e:
            last_exc = e
            time.sleep(retry_delay)
    raise last_exc