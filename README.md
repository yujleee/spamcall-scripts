# 📞 AOS 서비스별 스팸 전화 / 단어 자동 추가 테스트 스크립트 (공유용)

본 스크립트는 Android 단말에서, 스팸 전화번호 및 차단 단어를 자동으로 추가하는 테스트 자동화 도구입니다.  
**최대 등록 한도 팝업 확인을 위해 수동 입력 과정 생략**을 목적으로 만들어졌습니다.

> ⚠️ 현재는 **Windows OS** 환경에서만 실행 가능합니다. (Mac 지원은 추후 추가 예정)

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
-   설치 시, **"Add Python to PATH" 체크 필수**

### 2. Appium 설치

터미널(cmd) 창을 열고 아래 명령어 실행:

`bash npm install -g appium`

Appium 설치 이전, Node.js가 설치되어 있어야 합니다. (https://nodejs.org/)

### 3. VSCode 설치

https://code.visualstudio.com/

실행 후, 아래 확장 프로그램 설치:

-   Python

-   Python Environment

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

관리자 권한으로 cmd 실행 후:

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

-   우측 상단의 ▶️ (Run Python File) 버튼 클릭

<br>
<br>

### 📝 기타

-   터미널에 등록완료 로그가 실시간 출력됩니다. 문제가 발생하면 자동으로 중단되고 로그가 표시됩니다.
