# 📞 AOS 서비스별 스팸 전화 / 단어 자동 추가 테스트 스크립트 (공유용)

본 스크립트는 Android / iOS 단말에서, 스팸 전화번호 및 차단 단어를 자동으로 추가하는 테스트 자동화 도구입니다.  
**최대 등록 한도 팝업 확인을 위해 수동 입력 과정 생략**을 목적으로 만들어졌습니다.

> ⚠️ **Windows / Mac OS** 환경에서 실행 가능합니다.

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

## 🚀 실행 방법 (Windows)

> ℹ️ 현재 Windows 버전만 배포되어 있습니다.

[Releases 페이지](../../releases)에서 최신 버전을 다운로드합니다.

| 버전 | 파일명 | 대상 |
| ---- | ------ | ---- |
| **포터블 버전** | `Appium.Script.Runner.Portable.zip` | Node.js / Appium / ADB 미설치 환경 |
| **일반 버전** | `Appium.Script.Runner.zip` | Node.js / Appium / ADB 설치 완료 환경 |

> 💡 **처음 사용하거나 개발 환경이 세팅되어 있지 않다면 포터블 버전을 권장합니다.**

<br>

### Window 에서 실행 시
**Privacy-i 프로그램이 설치되어 있다면 adb 연결이 원활하지 않을 수 있습니다.**
GUI 내 '디바이스 연결' 버튼을 선택했음에도 연결되지 않는다면 아래 내용을 참고 바랍니다.
- 단말 USB로 연결 > 디버깅 허용 > 제어판의 장치 관리자 실행 > Android Device 아래 SAMSUNG Android ADB Interface 를 우클릭 > 디바이스 사용/사용안함 버튼을 두어번 실행
- cmd 창을 열어 `adb devices` 를 입력했을 때 단말 정보가 나오면 정상연결.


### Mac OS 에서 실행 시

iOS 스크립트 실행은 Mac에서만 가능합니다.  
포터블 버전을 사용하더라도 **iOS 실행을 위해서는 아래 항목이 미리 세팅되어 있어야 합니다:**

- Xcode 설치 및 WDA(WebDriverAgent) 빌드
- Apple Developer 계정 및 서명 설정 (개인 애플 계정으로도 7일 사용 후 재설정 가능)
- 단말에 WDA 설치 및 신뢰 설정 완료
- Product > Test 실행 시 단말에 Automation Running 문구 떠있으면 프로그램 실행 가능

> ℹ️ 포터블 버전의 자동 설치(Node.js / Appium / ADB)는 Android 환경 구성에 해당하며, WDA 세팅은 포함되지 않습니다.

<br>

### 포터블 버전

1. `Appium.Script.Runner.Portable.zip` 다운로드 후 압축 해제
2. `Appium Script Runner Portable` 폴더 안의 `Appium Script Runner Portable.exe` 실행
3. 최초 실행 시 Node.js, Appium, ADB를 자동으로 다운로드하여 설치
   - **인터넷 연결이 필요하며, 설치에 수 분이 소요될 수 있습니다**
   - 설치 완료 후 이후 실행부터는 바로 시작됩니다

> ⚠️ `.exe` 파일만 따로 꺼내서 실행하면 동작하지 않습니다.  
> 반드시 **폴더 전체**를 유지한 채로 실행해야 합니다.

<br>

### 일반 버전

아래 항목이 모두 설치 및 환경변수 설정이 완료되어 있어야 합니다:

- JDK
- Android Studio (`JAVA_HOME`, `ANDROID_HOME` 환경변수 설정)
- Node.js (https://nodejs.org/)

**Appium 설치** (터미널/cmd를 관리자 모드로 실행):

```
npm install -g appium
```

설치 후 아래 명령어로 환경이 올바르게 설정되었는지 확인합니다:

```
npm install -g appium-doctor
appium-doctor
```

❌ 마크가 뜨는 항목이 있다면 해당 문제를 해결한 후 재실행합니다.

준비가 완료되면:

1. `Appium.Script.Runner.zip` 다운로드 후 압축 해제
2. `Appium Script Runner` 폴더 안의 `Appium Script Runner.exe` 실행

> ⚠️ `.exe` 파일만 따로 꺼내서 실행하면 동작하지 않습니다.  
> 반드시 **폴더 전체**를 유지한 채로 실행해야 합니다.

