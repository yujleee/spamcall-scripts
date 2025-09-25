import os
import sys
import platform
import subprocess
import zipfile
import tarfile
import urllib.request
from pathlib import Path
import json

def setup_unicode_environment():
    """유니코드 환경 설정 - 가장 먼저 호출"""
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    if sys.platform == 'win32':
        try:
            subprocess.run(['chcp', '65001'], shell=True, capture_output=True, timeout=5)
        except:
            pass

# GUI에서 재정의할 수 있는 출력 함수
safe_print = None
_log_callback = None

def set_log_callback(callback):
    """GUI에서 로그 콜백 함수 설정"""
    global _log_callback
    _log_callback = callback

def _default_safe_print(text):
    """기본 안전한 출력 함수"""
    try:
        if _log_callback:
            _log_callback(text)
        print(text)
    except UnicodeEncodeError:
        try:
            safe_text = str(text).encode('cp949', errors='replace').decode('cp949')
            if _log_callback:
                _log_callback(safe_text)
            print(safe_text)
        except:
            msg = "[출력 오류: 특수문자 포함]"
            if _log_callback:
                _log_callback(msg)
            print(msg)

# 초기화
if safe_print is None:
    safe_print = _default_safe_print

def get_runtime_paths():
    """OS별 런타임 경로 반환"""
    if getattr(sys, 'frozen', False):
        # exe로 패키징된 경우
        base_dir = Path(sys.executable).parent
    else:
        # 개발 환경
        base_dir = Path(__file__).parent
    
    runtime_dir = base_dir / "runtime"
    system = platform.system().lower()
    
    if system == "windows":
        os_dir = runtime_dir / "windows"
    elif system == "darwin":
        os_dir = runtime_dir / "macos"
    else:
        safe_print("❌ 지원하지 않는 OS입니다.")
        return None
    
    return {
        'base_dir': base_dir,
        'runtime_dir': runtime_dir,
        'os_dir': os_dir,
        'node_dir': os_dir / "node",
        'appium_dir': os_dir / "appium",
        'adb_dir': os_dir / "adb",
        'system': system
    }

def check_runtime_exists():
    """실행환경이 이미 설치되어 있는지 확인"""
    try:
        paths = get_runtime_paths()
        if not paths:
            return False
            
        system = paths['system']
        
        # 필수 파일들 확인
        if system == "windows":
            required_files = [
                paths['node_dir'] / "node.exe",
                paths['node_dir'] / "npm.cmd",
                paths['adb_dir'] / "adb.exe"
            ]
            # Appium 확인 (설치 후 생성되는 파일)
            appium_executable = paths['appium_dir'] / "node_modules" / ".bin" / "appium.cmd"
        else:  # macOS
            required_files = [
                paths['node_dir'] / "bin" / "node",
                paths['node_dir'] / "bin" / "npm", 
                paths['adb_dir'] / "adb"
            ]
            appium_executable = paths['appium_dir'] / "node_modules" / ".bin" / "appium"
        
        # 기본 파일들 존재 확인
        basic_exists = all(file.exists() for file in required_files)
        
        # Appium 존재 확인 (별도)
        appium_exists = appium_executable.exists()
        
        if basic_exists and appium_exists:
            safe_print("✅ 포터블 실행환경이 이미 설치되어 있습니다.")
            return True
        elif basic_exists and not appium_exists:
            safe_print("⚠️  기본 환경은 있지만 Appium이 설치되지 않았습니다.")
            return False
        else:
            safe_print("❌ 포터블 실행환경이 설치되지 않았습니다.")
            return False
            
    except Exception as e:
        safe_print(f"❌ 실행환경 확인 중 오류: {e}")
        return False

def download_file_with_progress(url, filepath, description):
    """진행률 표시와 함께 파일 다운로드"""
    safe_print(f"📦 {description} 다운로드 중...")
    
    try:
        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                if block_num % 10 == 0:  # 10블록마다 출력
                    safe_print(f"   진행률: {percent}%")
        
        urllib.request.urlretrieve(url, filepath, reporthook=progress_hook)
        safe_print(f"✅ {description} 다운로드 완료")
        return True
        
    except urllib.error.URLError as e:
        safe_print(f"❌ {description} 다운로드 실패 (네트워크 오류): {e}")
        return False
    except Exception as e:
        safe_print(f"❌ {description} 다운로드 실패: {e}")
        return False

def extract_archive_safe(archive_path, extract_to, description):
    """안전한 압축 파일 해제"""
    safe_print(f"📂 {description} 압축 해제 중...")
    
    try:
        extract_to.mkdir(parents=True, exist_ok=True)
        
        if archive_path.suffix.lower() == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif archive_path.suffix.lower() in ['.tar', '.gz', '.tgz'] or '.tar.' in str(archive_path):
            with tarfile.open(archive_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_to)
        else:
            safe_print(f"❌ 지원하지 않는 압축 파일 형식: {archive_path.suffix}")
            return False
        
        safe_print(f"✅ {description} 압축 해제 완료")
        return True
        
    except Exception as e:
        safe_print(f"❌ {description} 압축 해제 실패: {e}")
        return False

def setup_nodejs():
    """Node.js 포터블 설치"""
    safe_print("\n=== Node.js 설치 ===")
    
    paths = get_runtime_paths()
    if not paths:
        return False
        
    system = paths['system']
    os_dir = paths['os_dir']
    node_dir = paths['node_dir']
    
    # 이미 존재하는지 확인
    node_exe = node_dir / ("node.exe" if system == "windows" else "bin/node")
    if node_exe.exists():
        safe_print("✅ Node.js가 이미 설치되어 있습니다.")
        return True
    
    # Node.js 다운로드 URL 설정
    node_version = "v18.17.1"  # 안정적인 버전 사용
    
    if system == "windows":
        node_url = f"https://nodejs.org/dist/{node_version}/node-{node_version}-win-x64.zip"
        filename = f"node-{node_version}-win-x64.zip"
        folder_name = f"node-{node_version}-win-x64"
    else:  # macOS
        # CPU 아키텍처 확인
        machine = platform.machine().lower()
        if 'arm' in machine or 'aarch64' in machine:
            arch = "arm64"
        else:
            arch = "x64"
        
        node_url = f"https://nodejs.org/dist/{node_version}/node-{node_version}-darwin-{arch}.tar.gz"
        filename = f"node-{node_version}-darwin-{arch}.tar.gz"
        folder_name = f"node-{node_version}-darwin-{arch}"
    
    # 다운로드
    download_path = os_dir / filename
    os_dir.mkdir(parents=True, exist_ok=True)
    
    if not download_file_with_progress(node_url, download_path, "Node.js"):
        return False
    
    # 압축 해제
    if not extract_archive_safe(download_path, os_dir, "Node.js"):
        download_path.unlink(missing_ok=True)
        return False
    
    # 폴더 이름 변경
    extracted_folder = os_dir / folder_name
    if extracted_folder.exists():
        if node_dir.exists():
            import shutil
            shutil.rmtree(node_dir)
        extracted_folder.rename(node_dir)
    
    # 다운로드 파일 정리
    download_path.unlink(missing_ok=True)
    
    # 설치 확인
    if node_exe.exists():
        safe_print("✅ Node.js 설치 완료")
        return True
    else:
        safe_print("❌ Node.js 설치 실패 - 실행 파일을 찾을 수 없습니다")
        return False

def setup_appium():
    """Appium 설치"""
    safe_print("\n=== Appium 설치 ===")
    
    paths = get_runtime_paths()
    if not paths:
        return False
        
    system = paths['system']
    node_dir = paths['node_dir']
    appium_dir = paths['appium_dir']
    
    # 이미 설치되어 있는지 확인
    appium_exe = appium_dir / "node_modules" / ".bin" / ("appium.cmd" if system == "windows" else "appium")
    if appium_exe.exists():
        safe_print("✅ Appium이 이미 설치되어 있습니다.")
        return True
    
    try:
        appium_dir.mkdir(parents=True, exist_ok=True)
        
        # npm 경로 설정
        if system == "windows":
            npm_cmd = str(node_dir / "npm.cmd")
            node_cmd = str(node_dir / "node.exe")
        else:  # macOS
            npm_cmd = str(node_dir / "bin" / "npm")
            node_cmd = str(node_dir / "bin" / "node")
        
        # Node.js가 있는지 확인
        if not Path(node_cmd).exists():
            safe_print("❌ Node.js가 설치되지 않았습니다. 먼저 Node.js를 설치하세요.")
            return False
        
        # package.json 생성
        package_json = {
            "name": "appium-portable",
            "version": "1.0.0",
            "description": "Portable Appium installation"
        }
        
        with open(appium_dir / "package.json", 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Appium 설치
        safe_print("📦 Appium 패키지 설치 중... (시간이 걸릴 수 있습니다)")
        
        env = os.environ.copy()
        env['PATH'] = str(node_dir / ("" if system == "windows" else "bin")) + os.pathsep + env.get('PATH', '')
        
        result = subprocess.run([
            npm_cmd, 'install', 'appium@2.0.0', '--save'
        ], cwd=str(appium_dir), timeout=300, env=env, 
           capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        if result.returncode != 0:
            safe_print(f"❌ Appium 설치 실패: {result.stderr}")
            return False
        
        # UiAutomator2 드라이버 설치
        safe_print("📦 UiAutomator2 드라이버 설치 중...")
        
        appium_cmd = str(appium_exe)
        driver_result = subprocess.run([
            node_cmd, appium_cmd, 'driver', 'install', 'uiautomator2'
        ], timeout=180, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        if driver_result.returncode != 0:
            safe_print(f"⚠️  UiAutomator2 드라이버 설치 실패 (나중에 수동 설치 가능): {driver_result.stderr}")
        else:
            safe_print("✅ UiAutomator2 드라이버 설치 완료")
        
        safe_print("✅ Appium 설치 완료")
        return True
        
    except subprocess.TimeoutExpired:
        safe_print("❌ Appium 설치 타임아웃 - 네트워크 연결을 확인하세요")
        return False
    except Exception as e:
        safe_print(f"❌ Appium 설치 실패: {e}")
        return False

def setup_adb():
    """ADB 포터블 설치"""
    safe_print("\n=== ADB 설치 ===")
    
    paths = get_runtime_paths()
    if not paths:
        return False
        
    system = paths['system']
    os_dir = paths['os_dir']
    adb_dir = paths['adb_dir']
    
    # 이미 존재하는지 확인
    adb_exe = adb_dir / ("adb.exe" if system == "windows" else "adb")
    if adb_exe.exists():
        safe_print("✅ ADB가 이미 설치되어 있습니다.")
        return True
    
    # ADB 다운로드 URL (최신 버전)
    if system == "windows":
        adb_url = "https://dl.google.com/android/repository/platform-tools_r34.0.5-windows.zip"
        filename = "platform-tools-windows.zip"
    else:  # macOS
        adb_url = "https://dl.google.com/android/repository/platform-tools_r34.0.5-darwin.zip"
        filename = "platform-tools-darwin.zip"
    
    download_path = os_dir / filename
    
    if not download_file_with_progress(adb_url, download_path, "ADB Platform Tools"):
        return False
    
    if not extract_archive_safe(download_path, os_dir, "ADB"):
        download_path.unlink(missing_ok=True)
        return False
    
    # platform-tools 폴더를 adb로 이름 변경
    platform_tools_dir = os_dir / "platform-tools"
    if platform_tools_dir.exists():
        if adb_dir.exists():
            import shutil
            shutil.rmtree(adb_dir)
        platform_tools_dir.rename(adb_dir)
    
    # 다운로드 파일 정리
    download_path.unlink(missing_ok=True)
    
    # macOS에서 실행 권한 추가
    if system == "darwin":
        try:
            os.chmod(adb_exe, 0o755)
            # fastboot도 권한 추가
            fastboot_exe = adb_dir / "fastboot"
            if fastboot_exe.exists():
                os.chmod(fastboot_exe, 0o755)
        except Exception as e:
            safe_print(f"⚠️  실행 권한 설정 실패: {e}")
    
    if adb_exe.exists():
        safe_print("✅ ADB 설치 완료")
        return True
    else:
        safe_print("❌ ADB 설치 실패")
        return False

def create_launcher_scripts():
    """실행 스크립트 생성"""
    safe_print("\n=== 실행 스크립트 생성 ===")
    
    paths = get_runtime_paths()
    if not paths:
        return False
        
    system = paths['system']
    base_dir = paths['base_dir']
    node_dir = paths['node_dir']
    appium_dir = paths['appium_dir']
    adb_dir = paths['adb_dir']
    
    if system == "windows":
        # Windows 배치 파일
        launcher_content = f'''@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8

set PATH={node_dir.absolute()};{adb_dir.absolute()};%PATH%
set APPIUM_HOME={appium_dir.absolute()}

echo Appium 포터블 환경 시작 중...
cd /d "{base_dir.absolute()}"

REM Appium 서버를 백그라운드에서 시작
echo Appium 서버를 시작합니다...
start /min "Appium Server" cmd /c "{appium_dir / "node_modules" / ".bin" / "appium.cmd"} --port 4723"

REM 잠시 대기
timeout /t 3 /nobreak > nul

REM Python GUI 실행
echo GUI 애플리케이션을 시작합니다...
python main.py

pause
'''
        launcher_path = base_dir / "start_appium_gui.bat"
        
    else:  # macOS
        # macOS 셸 스크립트
        launcher_content = f'''#!/bin/bash
export PYTHONIOENCODING=utf-8
export PATH="{node_dir.absolute() / "bin"}:{adb_dir.absolute()}:$PATH"
export APPIUM_HOME="{appium_dir.absolute()}"

echo "Appium 포터블 환경 시작 중..."
cd "{base_dir.absolute()}"

# Appium 서버를 백그라운드에서 시작
echo "Appium 서버를 시작합니다..."
"{appium_dir / "node_modules" / ".bin" / "appium"}" --port 4723 &
APPIUM_PID=$!

# 잠시 대기
sleep 3

# Python GUI 실행
echo "GUI 애플리케이션을 시작합니다..."
python3 main.py

# 종료 시 Appium 서버도 종료
kill $APPIUM_PID 2>/dev/null
'''
        launcher_path = base_dir / "start_appium_gui.sh"
    
    try:
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        # macOS에서 실행 권한 추가
        if system == "darwin":
            os.chmod(launcher_path, 0o755)
        
        safe_print(f"✅ 실행 스크립트 생성: {launcher_path.name}")
        return True
        
    except Exception as e:
        safe_print(f"❌ 실행 스크립트 생성 실패: {e}")
        return False

def install_runtime():
    """전체 실행환경 설치"""
    setup_unicode_environment()
    
    safe_print(f"🚀 {platform.system()} 포터블 실행환경 구성 시작")
    
    paths = get_runtime_paths()
    if not paths:
        return False
        
    safe_print(f"📁 설치 경로: {paths['os_dir']}")
    
    success_count = 0
    total_steps = 4
    
    try:
        # 1. Node.js 설치
        if setup_nodejs():
            success_count += 1
        else:
            safe_print("❌ Node.js 설치에 실패했습니다.")
            return False
        
        # 2. ADB 설치 (Appium보다 먼저 설치)
        if setup_adb():
            success_count += 1
        else:
            safe_print("❌ ADB 설치에 실패했습니다.")
        
        # 3. Appium 설치
        if setup_appium():
            success_count += 1
        else:
            safe_print("❌ Appium 설치에 실패했습니다.")
            return False
        
        # 4. 실행 스크립트 생성
        if create_launcher_scripts():
            success_count += 1
        
        if success_count == total_steps:
            safe_print(f"\n🎉 포터블 실행환경 구성 완료! ({success_count}/{total_steps})")
            safe_print("이제 start_appium_gui 파일을 실행하여 애플리케이션을 시작할 수 있습니다.")
            return True
        else:
            safe_print(f"\n⚠️  부분적으로 완료됨 ({success_count}/{total_steps})")
            return False
        
    except KeyboardInterrupt:
        safe_print("\n❌ 설치가 사용자에 의해 중단되었습니다.")
        return False
    except Exception as e:
        safe_print(f"❌ 실행환경 설치 중 예상치 못한 오류 발생: {e}")
        return False

def get_portable_executable_paths():
    """포터블 환경의 실행 파일 경로 반환"""
    paths = get_runtime_paths()
    if not paths:
        return {}
        
    system = paths['system']
    
    if system == "windows":
        return {
            'node': str(paths['node_dir'] / "node.exe"),
            'npm': str(paths['node_dir'] / "npm.cmd"),
            'appium': str(paths['appium_dir'] / "node_modules" / ".bin" / "appium.cmd"),
            'adb': str(paths['adb_dir'] / "adb.exe")
        }
    elif system == "darwin":
        return {
            'node': str(paths['node_dir'] / "bin" / "node"),
            'npm': str(paths['node_dir'] / "bin" / "npm"),
            'appium': str(paths['appium_dir'] / "node_modules" / ".bin" / "appium"),
            'adb': str(paths['adb_dir'] / "adb")
        }
    
    return {}

def setup_runtime_if_needed():
    """필요한 경우에만 실행환경 설치"""
    import tkinter as tk
    from tkinter import messagebox
    
    setup_unicode_environment()
    
    if check_runtime_exists():
        return True
    
    safe_print("포터블 실행환경이 필요합니다. 자동으로 설치를 시작합니다...")
    safe_print("⚠️  인터넷 연결이 필요하며, 설치에 수 분이 걸릴 수 있습니다.")
    
    # GUI 메시지 박스로 사용자 확인
    if messagebox.askyesno("환경 설정", 
                          "포터블 실행환경 설치가 필요합니다.\n" +
                          "인터넷 연결이 필요하며, 설치에 수 분이 걸릴 수 있습니다.\n\n" +
                          "지금 설치하시겠습니까?"):
        return install_runtime()
    else:
        safe_print("설치가 취소되었습니다.")
        return False

def test_runtime_environment():
    """런타임 환경 테스트"""
    safe_print("\n=== 런타임 환경 테스트 ===")
    
    paths = get_portable_executable_paths()
    if not paths:
        safe_print("❌ 런타임 경로를 가져올 수 없습니다.")
        return False
    
    tests_passed = 0
    total_tests = len(paths)
    
    for name, exe_path in paths.items():
        try:
            if Path(exe_path).exists():
                safe_print(f"✅ {name}: {exe_path}")
                tests_passed += 1
            else:
                safe_print(f"❌ {name}: 파일이 존재하지 않음 - {exe_path}")
        except Exception as e:
            safe_print(f"❌ {name}: 테스트 실패 - {e}")
    
    safe_print(f"\n테스트 결과: {tests_passed}/{total_tests} 통과")
    return tests_passed == total_tests

# 명령행 실행용
if __name__ == "__main__":
    setup_unicode_environment()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "setup":
            success = install_runtime()
            sys.exit(0 if success else 1)
        elif command == "check":
            exists = check_runtime_exists()
            if exists:
                test_runtime_environment()
            sys.exit(0 if exists else 1)
        elif command == "test":
            success = test_runtime_environment()
            sys.exit(0 if success else 1)
        else:
            safe_print(f"❌ 알 수 없는 명령어: {command}")
    
    safe_print("사용법:")
    safe_print("  python setup_runtime.py setup    # 실행환경 강제 설치")
    safe_print("  python setup_runtime.py check    # 실행환경 확인")
    safe_print("  python setup_runtime.py test     # 실행환경 테스트")
    safe_print("  또는 main.py에서 자동으로 호출됨")