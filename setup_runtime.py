import os
import sys
import platform
import subprocess
import zipfile
import tarfile
import urllib.request
from pathlib import Path

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
        raise Exception("지원하지 않는 OS입니다.")
    
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
        system = paths['system']
        
        # 필수 파일들 확인
        if system == "windows":
            required_files = [
                paths['node_dir'] / "node.exe",
                paths['node_dir'] / "npm.cmd",
                paths['adb_dir'] / "adb.exe",
                paths['appium_dir'] / "node_modules" / ".bin" / "appium.cmd"
            ]
        else:  # macOS
            required_files = [
                paths['node_dir'] / "bin" / "node",
                paths['node_dir'] / "bin" / "npm",
                paths['adb_dir'] / "adb",
                paths['appium_dir'] / "node_modules" / ".bin" / "appium"
            ]
        
        # 모든 필수 파일이 존재하는지 확인
        all_exist = all(file.exists() for file in required_files)
        
        if all_exist:
            print("✅ 포터블 실행환경이 이미 설치되어 있습니다.")
            return True
        else:
            print("❌ 포터블 실행환경이 설치되지 않았습니다.")
            return False
            
    except Exception as e:
        print(f"❌ 실행환경 확인 중 오류: {e}")
        return False

def download_file(url, filepath, description):
    """파일 다운로드"""
    print(f"📦 {description} 다운로드 중...")
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"✅ {description} 다운로드 완료")
        return True
    except Exception as e:
        print(f"❌ {description} 다운로드 실패: {e}")
        return False

def extract_archive(archive_path, extract_to, description):
    """압축 파일 해제"""
    print(f"📂 {description} 압축 해제 중...")
    try:
        if archive_path.suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif archive_path.suffix in ['.tar', '.gz', '.tgz']:
            with tarfile.open(archive_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_to)
        
        print(f"✅ {description} 압축 해제 완료")
        return True
    except Exception as e:
        print(f"❌ {description} 압축 해제 실패: {e}")
        return False

def setup_nodejs():
    """Node.js 포터블 설치"""
    print("\n=== Node.js 설치 ===")
    
    paths = get_runtime_paths()
    system = paths['system']
    os_dir = paths['os_dir']
    node_dir = paths['node_dir']
    
    if system == "windows":
        node_url = "https://nodejs.org/dist/v18.17.0/node-v18.17.0-win-x64.zip"
        filename = "node-v18.17.0-win-x64.zip"
        folder_name = "node-v18.17.0-win-x64"
    else:  # macOS
        node_url = "https://nodejs.org/dist/v18.17.0/node-v18.17.0-darwin-x64.tar.gz"
        filename = "node-v18.17.0-darwin-x64.tar.gz"
        folder_name = "node-v18.17.0-darwin-x64"
    
    # 다운로드
    download_path = os_dir / filename
    os_dir.mkdir(parents=True, exist_ok=True)
    
    if not download_file(node_url, download_path, "Node.js"):
        return False
    
    # 압축 해제
    if not extract_archive(download_path, os_dir, "Node.js"):
        return False
    
    # 폴더 이름 변경
    (os_dir / folder_name).rename(node_dir)
    download_path.unlink()  # 압축 파일 삭제
    
    return True

def setup_appium():
    """Appium 설치"""
    print("\n=== Appium 설치 ===")
    
    paths = get_runtime_paths()
    system = paths['system']
    node_dir = paths['node_dir']
    appium_dir = paths['appium_dir']
    
    try:
        appium_dir.mkdir(parents=True, exist_ok=True)
        
        # npm 경로 설정
        if system == "windows":
            npm_cmd = str(node_dir / "npm.cmd")
            node_cmd = str(node_dir / "node.exe")
        else:  # macOS
            npm_cmd = str(node_dir / "bin" / "npm")
            node_cmd = str(node_dir / "bin" / "node")
        
        # Appium 설치
        print("📦 Appium 패키지 설치 중...")
        result = subprocess.run([
            npm_cmd, 'install', 'appium@latest', '--prefix', str(appium_dir)
        ], cwd=str(appium_dir), timeout=180)
        
        if result.returncode != 0:
            print("❌ Appium 설치 실패")
            return False
        
        # UiAutomator2 드라이버 설치
        print("📦 UiAutomator2 드라이버 설치 중...")
        if system == "windows":
            appium_cmd = str(appium_dir / "node_modules" / ".bin" / "appium.cmd")
        else:
            appium_cmd = str(appium_dir / "node_modules" / ".bin" / "appium")
        
        subprocess.run([
            node_cmd, appium_cmd, 'driver', 'install', 'uiautomator2'
        ], timeout=120)
        
        print("✅ Appium 설치 완료")
        return True
        
    except Exception as e:
        print(f"❌ Appium 설치 실패: {e}")
        return False

def setup_adb():
    """ADB 포터블 설치"""
    print("\n=== ADB 설치 ===")
    
    paths = get_runtime_paths()
    system = paths['system']
    os_dir = paths['os_dir']
    adb_dir = paths['adb_dir']
    
    if system == "windows":
        # Windows용 ADB
        adb_url = "https://dl.google.com/android/repository/platform-tools_r34.0.4-windows.zip"
        filename = "platform-tools-windows.zip"
    else:  # macOS
        adb_url = "https://dl.google.com/android/repository/platform-tools_r34.0.4-darwin.zip"
        filename = "platform-tools-darwin.zip"
    
    download_path = os_dir / filename
    
    if not download_file(adb_url, download_path, "ADB Platform Tools"):
        return False
    
    if not extract_archive(download_path, os_dir, "ADB"):
        return False
    
    # platform-tools 폴더를 adb로 이름 변경
    (os_dir / "platform-tools").rename(adb_dir)
    download_path.unlink()
    
    return True

def create_launcher_scripts():
    """실행 스크립트 생성"""
    print("\n=== 실행 스크립트 생성 ===")
    
    paths = get_runtime_paths()
    system = paths['system']
    base_dir = paths['base_dir']
    node_dir = paths['node_dir']
    appium_dir = paths['appium_dir']
    adb_dir = paths['adb_dir']
    
    if system == "windows":
        # Windows 배치 파일
        launcher_content = f'''@echo off
set PATH={node_dir.absolute()};{adb_dir.absolute()};%PATH%
set APPIUM_HOME={appium_dir.absolute()}
cd /d "{base_dir.absolute()}"
start "Appium Server" cmd /k "echo Appium 서버 시작 중... && {appium_dir / "node_modules" / ".bin" / "appium.cmd"}"
timeout /t 3
AppiumScriptRunner.exe
'''
        launcher_path = base_dir / "start_appium_runner.bat"
        
    else:  # macOS
        # macOS 쉘 스크립트
        launcher_content = f'''#!/bin/bash
export PATH="{node_dir.absolute() / "bin"}:{adb_dir.absolute()}:$PATH"
export APPIUM_HOME="{appium_dir.absolute()}"
cd "{base_dir.absolute()}"

# 터미널에서 Appium 서버 시작
osascript -e 'tell application "Terminal" to do script "cd \\"{base_dir.absolute()}\\" && {appium_dir / "node_modules" / ".bin" / "appium"}"'

sleep 3
./AppiumScriptRunner
'''
        launcher_path = base_dir / "start_appium_runner.sh"
    
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    # macOS에서 실행 권한 추가
    if system == "darwin":
        os.chmod(launcher_path, 0o755)
    
    print(f"✅ 실행 스크립트 생성: {launcher_path.name}")

def install_runtime():
    """전체 실행환경 설치"""
    print(f"🚀 {platform.system()} 포터블 실행환경 구성 시작")
    
    paths = get_runtime_paths()
    print(f"📁 설치 경로: {paths['os_dir']}")
    
    try:
        # 1. Node.js 설치
        if not setup_nodejs():
            return False
        
        # 2. Appium 설치
        if not setup_appium():
            return False
        
        # 3. ADB 설치
        if not setup_adb():
            return False
        
        # 4. 실행 스크립트 생성
        create_launcher_scripts()
        
        print("\n🎉 포터블 실행환경 구성 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 실행환경 설치 중 오류 발생: {e}")
        return False

def get_portable_executable_paths():
    """포터블 환경의 실행 파일 경로 반환"""
    paths = get_runtime_paths()
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
    if check_runtime_exists():
        return True
    
    print("포터블 실행환경이 필요합니다. 자동으로 설치를 시작합니다...")
    return install_runtime()

# 명령행 실행용
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        success = install_runtime()
        sys.exit(0 if success else 1)
    else:
        print("사용법:")
        print("  python setup_runtime.py setup     # 실행환경 강제 설치")
        print("  또는 main.py에서 자동으로 호출됨")