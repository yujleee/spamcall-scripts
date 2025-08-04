# 📞 AOS 서비스별 스팸 전화 / 단어 자동 추가 테스트 스크립트 (공유용)

본 스크립트는 Android 단말에서, 스팸 전화번호 및 차단 단어를 자동으로 추가하는 테스트 자동화 도구입니다.  
**최대 등록 한도 팝업 확인을 위해 수동 입력 과정 생략**을 목적으로 만들어졌습니다.

> ⚠️ 현재 **Windows OS** 환경에서 모든 스크립트 실행 가능합니다.
> ⚠️ **Mac OS**는 익시오 스팸 번호 차단/등록만 현재 가능합니다. (나머지 스크립트 실행 확인 후 보완 예정)

---

<br>

## ✅ 테스트 목적

| 항목         | 테스트 내용                                 |
| ------------ | ------------------------------------------- |
| 1. 차단 번호 | 번호 최대 등록 후, 최대 개수 도달 팝업 확인 |
| 2. 차단 단어 | 단어 최대 등록 후, 등록 제한 팝업 확인      |

자동으로 번호 및 단어를 순차적으로 입력하기 때문에, **스크립트 진행 시간이 적지 않게 소요됩니다.**  
스크립트가 돌아가는 동안 다른 작업을 하셔도 무방합니다.

| 서비스명      | 등록 개수    | 예상 소요 시간 |
| ------------- | ------------ | -------------- |
| 익시오        | 최대 600개   | 약 50분        |
| 모바일 매니저 | 약 200~600개 | 약 30~50분     |
| 스팸전화알림  | 약 100개     | 약 15분        |

---

<br>
<br>

-   스크립트 실행 방법은 아래와 같으며 Python, Appium, Vscode가 설치되어 있는 경우 4번부터 진행해도 무방합니다.

## 🧰 사전 준비 사항 (한 번만 하면 됨)

### 1. Python 설치

-   https://www.python.org/downloads/
-   버전 3.10 이상
-   설치 시, **"Add Python to PATH" 체크 필수**

### 2. Appium 설치

터미널(cmd) 창을 관리자 모드로 열고 아래 명령어 실행:

`bash npm install -g appium`

Appium 설치 이전, 아래 프로그램들이 설치되어 있어야 합니다.
설치와 관련해서는 구글 참조 바랍니다.

-   JDK
-   Android Studio 설치 및 환경변수 설정 (JAVA_HOME, ANDROID_HOME)
-   Node.js (https://nodejs.org/)

터미널을 연 후 아래 명령어 실행:
appium-doctor 는 현재 환경이 Appium을 실행하기에 적합한지 체크 후 보여주는 패키지입니다.

`bash npm install appium-doctor`

appium-doctor 설치 후 아래 명령어를 실행하면 환경 설정이 제대로 되었는지 확인 가능합니다.

`bash appium-doctor`

만약 명령어 실행 시 ❌ 마크가 뜨는 행이 있다면 그 행과 관련된 문제를 해결해준 후 재실행하면 됩니다.

### 3. VSCode 설치

https://code.visualstudio.com/

실행 후, 아래 확장 프로그램 설치:

-   Python

-   Python Environment

mac의 경우 파이썬 인터프리터를 지정해주어야 합니다.

cmd + shift + p > pyhton interpreter 선택 하면 어떤 파이썬 버전으로 실행할 것인지 지정이 가능합니다.
아래 경로를 참고하여 3.10 버전 이상의 경로를 지정해 줍니다.

`/usr/local/bin/python3` (인텔 mac)  
`/opt/homebrew/bin/python3` (M1 이상 mac)

<br>
<br>

## 📦 스크립트 다운로드 및 환경 설정

### 4. 스크립트 다운로드

GitHub Repository에서 Code > Download Zip 클릭하여 다운로드
또는 Git을 아는 경우:

`bash git clone [레포주소]`

### 5. 패키지 설치

VSCode를 열고, Ctrl + ~ 로 터미널을 열어 아래 명령어 입력:

`bash pip install -r requirements.txt`

<br>
<br>

## 📱 AOS 단말 연결 및 실행

### 6. AOS 단말기와 PC 연결 (USB 케이블)

단말에서 개발자 옵션 > USB 디버깅 활성화 필수

### 7. 단말기 확인

터미널에서 다음 명령어 입력:

`bash adb devices`
입력 후 나오는 단말기 ID 값을 기억해두세요. (예: R3CX20TEEMV)

<br>
<br>

## ⚙️ 스크립트 설정 (기기 정보 변경)

### 8. deviceName과 OS 버전 설정

add_spam_number() 함수 안의 caps 값 중 아래 부분 수정:

```python
"deviceName": "R3CX20TEEMV",  # 7번에서 확인한 단말기 ID 입력
"platformVersion": "14",      # 단말의 Android OS 버전에 맞게 수정
```

<br>
<br>

## 🚀 실행

### 9. Appium 서버 실행

(win) 관리자 권한으로 cmd 실행
(mac) 터미널 실행 후:

`bash appium`
"Appium REST http interface listener started..." 메시지가 뜨면 성공

### 10. VSCode에서 스크립트 실행

-   \*.py 파일 열기

| 서비스                   | 파일명                           |
| ------------------------ | -------------------------------- |
| 익시오                   | ixiO_add_spamList.py             |
| 모바일매니저 > 스팸 번호 | mobileManager_add_spam_number.py |
| 모바일매니저 > 스팸 단어 | mobileManager_add_spam_words.py  |
| 스팸전화알림             | spamcallnoti_add_spam_number.py  |

-   (win) 우측 상단의 ▶️ (Run Python File) 버튼 클릭
-   (mac) vscode 내 터미널에서 `bash python3 ./add_spam_number_and_words/파일명.py` 입력

<br>
<br>

### 📝 기타

-   터미널에 등록완료 로그가 실시간 출력됩니다. 문제가 발생하면 자동으로 중단되고 로그가 표시됩니다.
