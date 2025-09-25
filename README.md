# 📞 AOS 서비스별 스팸 전화 / 단어 자동 추가 테스트 스크립트

본 스크립트는 Android 단말에서, 스팸 전화번호 및 차단 단어를 자동으로 추가하는 테스트 자동화 도구입니다.  
**최대 등록 한도 팝업 확인을 위해 수동 입력 과정을 자동화**하여 시간을 절약할 수 있습니다.

> ⚠️ Windows와 Mac OS 모두 지원합니다.

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

### 3. 스크립트 실행

### 지원하는 스크립트

| 서비스       | 기능          | 파일명                             |
| ------------ | ------------- | ---------------------------------- |
| 익시오       | 스팸번호 등록 | `ixiO_add_spamList.py`             |
|              | 스팸단어 등록 | `ixiO_add_spam_words.py`           |
| 모바일매니저 | 스팸번호 등록 | `mobileManager_add_spam_number.py` |
|              | 스팸단어 등록 | `mobileManager_add_spam_words.py`  |
| 스팸전화알림 | 스팸번호 등록 | `spamcallnoti_add_spam_number.py`  |

#### A. 실행 파일 사용 (권장)

1. `Appium Script Runner.exe` 실행
2. "디바이스 연결" 버튼 클릭
3. 단말 화면 이동 및 스크립트 선택 후 실행

-   실행환경 확인 후 환경 설정이 되어있지 않을 경우에는 포터블 실행환경을 설치, 설정합니다.

#### B. VS Code에서 직접 실행

하단 방법으로 프로그램 설치 및 환경 설정 후 실행
Python, Appium, Vscode가 설치되어 있는 경우 4번부터 진행해도 무방합니다.

## 🧰 사전 준비 사항 (한 번만 하면 됨)

### 1. Python 설치

-   https://www.python.org/downloads/
-   버전 3.10 이상
-   설치 시, **"Add Python to PATH" 체크 필수**

<br>
<br>

### 2. Appium 설치

터미널(cmd) 창을 관리자 모드로 열고 아래 명령어 실행:

`npm install -g appium`

Appium 설치 이전, 아래 프로그램들이 설치되어 있어야 합니다.
설치와 관련해서는 구글 참조 바랍니다.

-   JDK
-   Android Studio 설치 및 환경변수 설정 (JAVA_HOME, ANDROID_HOME)
-   Node.js (https://nodejs.org/)

터미널을 연 후 아래 명령어 실행:
appium-doctor 는 현재 환경이 Appium을 실행하기에 적합한지 체크 후 보여주는 패키지입니다.

`npm install appium-doctor`

appium-doctor 설치 후 아래 명령어를 실행하면 환경 설정이 제대로 되었는지 확인 가능합니다.

`appium-doctor`

만약 명령어 실행 시 ❌ 마크가 뜨는 행이 있다면 그 행과 관련된 문제를 해결해준 후 재실행하면 됩니다.

<br>
<br>

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

`git clone [레포주소]`

### 5. 패키지 설치

VSCode를 열고, Ctrl + ~ 로 터미널을 열어 아래 명령어 입력:

`pip install -r requirements.txt`

<br>
<br>

### 6. 프로그램 실행

`main.py` 로 이동하여 파일 실행

-   (win) 우측 상단의 ▶️ (Run Python File) 버튼 클릭
-   (mac) vscode 내 터미널에서 `python3 ./add_spam_number_and_words/파일명.py` 입력

-   디바이스 연결 버튼 클릭
-   스크립트 선택 후 단말 화면 이동 > 스크립트 실행 버튼 클릭

## 📝 로그 확인

-   실행 중인 스크립트의 진행 상황이 GUI 창에 실시간으로 표시됩니다.
-   상세 로그는 `logs` 폴더의 로그 파일에서 확인할 수 있습니다.
-   오류 발생 시 팝업으로 알림이 표시되며, 로그에 상세 내용이 기록됩니다.
