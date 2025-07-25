# AOS 서비스별 스팸 전화 / 단어 추가 테스트 스크립트 모음 (공유용)

-   이 스크립트들은 Window OS에서 작성되었으며 현재는 Window 에서만 실행 가능합니다. (Mac 용은 추후 작업 예정)
-   AOS 단말만 실행이 가능합니다.

-   이 스크립트들은 서비스 별로 아래와 같은 목적을 가지고 있습니다.

1. 차단 번호 / 차단 예외 번호 최대 갯수 추가 후 팝업 알림 확인
2. 스팸 차단 단어 / 스팸 예외 단어 최대 갯수 추가 후 팝업 알림 확인

-   수동으로 번호 및 단어를 추가하는 과정을 자동화한 스크립트기 때문에 스크립트가 완료되기 까지 최대 갯수를 추가하는 시간이 소요됩니다. 돌리는 동안 다른 작업을 하고 계시면 됩니다.
    -   익시오 (최대 600개) : 약 50분
    -   모바일매니저 (최대 300개) : 약 30분
    -   스팸전화알림 (약 100개) : 약 15분

# 스크립트 실행 방법

-   Python, Appium, Vscode가 이미 설치되어 있다면 4번부터 참고

1. Python 설치
2. Appium 설치
3. VsCode 설치 및 python 관련 Extension 설치
    - Python, Python Environment 등
4. 해당 레포지토리에서 파일(zip) 다운로드 혹은 clone
    - 파일을 다운로드 받는 경우 : code > download Zip
5. VsCode 내 터미널 (단축키: ctrl+` )을 열고 아래 명령어 입력
   (스크립트 실행을 위한 패키지 설치)

```
pip install -r requirements.txt
```

6. AOS 단말 usb로 연결 및 cmd 창 오픈
7. `adb devices` 로 단말 deviceName 확인
8. 스크립트 초반부 caps 변수 내 값 변경 (아래 코드 참조)

```
def add_spam_number():
    caps = {
        "platformName": "Android",
        "automationName": "UiAutomator2",
        "deviceName": "R3CX20TEEMV", # 이 부분 값 변경
        "platformVersion": "14", # OS가 다르다면 변경
```

9. cmd 창 관리자 권한으로 오픈하여 `appium` 입력하여 appium 서버 실행
10. 스크립트 실행 (우측 상단 ▷ 버튼 선택)
