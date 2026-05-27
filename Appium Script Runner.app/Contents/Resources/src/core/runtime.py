import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

from utils.safe_print import safe_print


def setup_unicode_environment():
    """유니코드 환경 설정"""
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if sys.platform == 'win32':
        try:
            subprocess.run(['chcp', '65001'], shell=True, capture_output=True, timeout=5)
        except Exception:
            pass


def get_runtime_paths():
    """OS별 런타임 경로 반환"""
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).parent.parent.parent

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
        'system': system,
    }


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
            'adb': str(paths['adb_dir'] / "adb.exe"),
        }
    elif system == "darwin":
        return {
            'node': str(paths['node_dir'] / "bin" / "node"),
            'npm': str(paths['node_dir'] / "bin" / "npm"),
            'appium': str(paths['appium_dir'] / "node_modules" / ".bin" / "appium"),
            'adb': str(paths['adb_dir'] / "adb"),
        }
    return {}


def check_runtime_exists():
    """포터블 실행환경이 이미 설치되어 있는지 확인"""
    try:
        paths = get_runtime_paths()
        if not paths:
            return False

        system = paths['system']
        if system == "windows":
            required_files = [
                paths['node_dir'] / "node.exe",
                paths['node_dir'] / "npm.cmd",
                paths['adb_dir'] / "adb.exe",
            ]
            appium_executable = paths['appium_dir'] / "node_modules" / ".bin" / "appium.cmd"
        else:
            required_files = [
                paths['node_dir'] / "bin" / "node",
                paths['node_dir'] / "bin" / "npm",
                paths['adb_dir'] / "adb",
            ]
            appium_executable = paths['appium_dir'] / "node_modules" / ".bin" / "appium"

        basic_exists = all(f.exists() for f in required_files)
        appium_exists = appium_executable.exists()

        if basic_exists and appium_exists:
            safe_print("✅ 포터블 실행환경이 이미 설치되어 있습니다.")
            return True
        elif basic_exists:
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
            if total_size > 0 and block_num % 10 == 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
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
    """압축 파일 해제"""
    safe_print(f"📂 {description} 압축 해제 중...")
    try:
        extract_to.mkdir(parents=True, exist_ok=True)
        suffix = archive_path.suffix.lower()
        if suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(extract_to)
        elif suffix in ['.tar', '.gz', '.tgz'] or '.tar.' in str(archive_path):
            with tarfile.open(archive_path, 'r:*') as tf:
                tf.extractall(extract_to)
        else:
            safe_print(f"❌ 지원하지 않는 압축 파일 형식: {suffix}")
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
    node_dir = paths['node_dir']
    os_dir = paths['os_dir']

    node_exe = node_dir / ("node.exe" if system == "windows" else "bin/node")
    if node_exe.exists():
        safe_print("✅ Node.js가 이미 설치되어 있습니다.")
        return True

    node_version = "v18.17.1"
    if system == "windows":
        node_url = f"https://nodejs.org/dist/{node_version}/node-{node_version}-win-x64.zip"
        filename = f"node-{node_version}-win-x64.zip"
        folder_name = f"node-{node_version}-win-x64"
    else:
        arch = "arm64" if 'arm' in platform.machine().lower() else "x64"
        node_url = f"https://nodejs.org/dist/{node_version}/node-{node_version}-darwin-{arch}.tar.gz"
        filename = f"node-{node_version}-darwin-{arch}.tar.gz"
        folder_name = f"node-{node_version}-darwin-{arch}"

    download_path = os_dir / filename
    os_dir.mkdir(parents=True, exist_ok=True)

    if not download_file_with_progress(node_url, download_path, "Node.js"):
        return False
    if not extract_archive_safe(download_path, os_dir, "Node.js"):
        download_path.unlink(missing_ok=True)
        return False

    extracted_folder = os_dir / folder_name
    if extracted_folder.exists():
        if node_dir.exists():
            shutil.rmtree(node_dir)
        extracted_folder.rename(node_dir)

    download_path.unlink(missing_ok=True)

    if node_exe.exists():
        safe_print("✅ Node.js 설치 완료")
        return True
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

    appium_exe = appium_dir / "node_modules" / ".bin" / ("appium.cmd" if system == "windows" else "appium")
    if appium_exe.exists():
        safe_print("✅ Appium이 이미 설치되어 있습니다.")
        return True

    try:
        appium_dir.mkdir(parents=True, exist_ok=True)

        if system == "windows":
            npm_cmd = str(node_dir / "npm.cmd")
            node_cmd = str(node_dir / "node.exe")
        else:
            npm_cmd = str(node_dir / "bin" / "npm")
            node_cmd = str(node_dir / "bin" / "node")

        if not Path(node_cmd).exists():
            safe_print("❌ Node.js가 설치되지 않았습니다. 먼저 Node.js를 설치하세요.")
            return False

        with open(appium_dir / "package.json", 'w') as f:
            json.dump({"name": "appium-portable", "version": "1.0.0"}, f, indent=2)

        safe_print("📦 Appium 패키지 설치 중... (시간이 걸릴 수 있습니다)")
        env = os.environ.copy()
        env['PATH'] = str(node_dir / ("" if system == "windows" else "bin")) + os.pathsep + env.get('PATH', '')

        result = subprocess.run(
            [npm_cmd, 'install', 'appium@2.0.0', '--save'],
            cwd=str(appium_dir),
            timeout=300,
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        if result.returncode != 0:
            safe_print(f"❌ Appium 설치 실패: {result.stderr}")
            return False

        safe_print("📦 UiAutomator2 드라이버 설치 중...")
        driver_result = subprocess.run(
            [node_cmd, str(appium_exe), 'driver', 'install', 'uiautomator2'],
            timeout=180,
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        if driver_result.returncode != 0:
            safe_print(f"⚠️  UiAutomator2 드라이버 설치 실패: {driver_result.stderr}")
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

    adb_exe = adb_dir / ("adb.exe" if system == "windows" else "adb")
    if adb_exe.exists():
        safe_print("✅ ADB가 이미 설치되어 있습니다.")
        return True

    if system == "windows":
        adb_url = "https://dl.google.com/android/repository/platform-tools_r34.0.5-windows.zip"
        filename = "platform-tools-windows.zip"
    else:
        adb_url = "https://dl.google.com/android/repository/platform-tools_r34.0.5-darwin.zip"
        filename = "platform-tools-darwin.zip"

    download_path = os_dir / filename

    if not download_file_with_progress(adb_url, download_path, "ADB Platform Tools"):
        return False
    if not extract_archive_safe(download_path, os_dir, "ADB"):
        download_path.unlink(missing_ok=True)
        return False

    platform_tools_dir = os_dir / "platform-tools"
    if platform_tools_dir.exists():
        if adb_dir.exists():
            shutil.rmtree(adb_dir)
        platform_tools_dir.rename(adb_dir)

    download_path.unlink(missing_ok=True)

    if system == "darwin":
        try:
            os.chmod(adb_exe, 0o755)
            fastboot_exe = adb_dir / "fastboot"
            if fastboot_exe.exists():
                os.chmod(fastboot_exe, 0o755)
        except Exception as e:
            safe_print(f"⚠️  실행 권한 설정 실패: {e}")

    if adb_exe.exists():
        safe_print("✅ ADB 설치 완료")
        return True
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
        appium_bin = appium_dir / "node_modules" / ".bin" / "appium.cmd"
        content = (
            f'@echo off\nchcp 65001 > nul\nset PYTHONIOENCODING=utf-8\n\n'
            f'set PATH={node_dir.absolute()};{adb_dir.absolute()};%PATH%\n'
            f'set APPIUM_HOME={appium_dir.absolute()}\n\n'
            f'echo Appium 포터블 환경 시작 중...\ncd /d "{base_dir.absolute()}"\n\n'
            f'echo Appium 서버를 시작합니다...\n'
            f'start /min "Appium Server" cmd /c "{appium_bin} --port 4723"\n\n'
            f'timeout /t 3 /nobreak > nul\n\necho GUI 애플리케이션을 시작합니다...\npython main.py\n\npause\n'
        )
        launcher_path = base_dir / "start_appium_gui.bat"
    else:
        appium_bin = appium_dir / "node_modules" / ".bin" / "appium"
        content = (
            f'#!/bin/bash\nexport PYTHONIOENCODING=utf-8\n'
            f'export PATH="{node_dir.absolute() / "bin"}:{adb_dir.absolute()}:$PATH"\n'
            f'export APPIUM_HOME="{appium_dir.absolute()}"\n\n'
            f'echo "Appium 포터블 환경 시작 중..."\ncd "{base_dir.absolute()}"\n\n'
            f'echo "Appium 서버를 시작합니다..."\n"{appium_bin}" --port 4723 &\nAPPIUM_PID=$!\n\n'
            f'sleep 3\n\necho "GUI 애플리케이션을 시작합니다..."\npython3 main.py\n\n'
            f'kill $APPIUM_PID 2>/dev/null\n'
        )
        launcher_path = base_dir / "start_appium_gui.sh"

    try:
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(content)
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
    try:
        if not setup_nodejs():
            safe_print("❌ Node.js 설치에 실패했습니다.")
            return False
        success_count += 1

        if setup_adb():
            success_count += 1
        else:
            safe_print("❌ ADB 설치에 실패했습니다.")

        if not setup_appium():
            safe_print("❌ Appium 설치에 실패했습니다.")
            return False
        success_count += 1

        if create_launcher_scripts():
            success_count += 1

        if success_count == 4:
            safe_print(f"\n🎉 포터블 실행환경 구성 완료! ({success_count}/4)")
            return True
        else:
            safe_print(f"\n⚠️  부분적으로 완료됨 ({success_count}/4)")
            return False

    except KeyboardInterrupt:
        safe_print("\n❌ 설치가 사용자에 의해 중단되었습니다.")
        return False
    except Exception as e:
        safe_print(f"❌ 실행환경 설치 중 예상치 못한 오류 발생: {e}")
        return False


def setup_runtime_if_needed():
    """필요한 경우에만 실행환경 설치"""
    setup_unicode_environment()
    if check_runtime_exists():
        return True

    safe_print("포터블 실행환경이 필요합니다. 자동으로 설치를 시작합니다...")
    safe_print("⚠️  인터넷 연결이 필요하며, 설치에 수 분이 걸릴 수 있습니다.")

    if input("계속 진행하시겠습니까? (y/n): ").lower() != 'y':
        safe_print("설치가 취소되었습니다.")
        return False
    return install_runtime()


def test_runtime_environment():
    """런타임 환경 테스트"""
    safe_print("\n=== 런타임 환경 테스트 ===")
    paths = get_portable_executable_paths()
    if not paths:
        safe_print("❌ 런타임 경로를 가져올 수 없습니다.")
        return False

    tests_passed = sum(
        1 for name, exe_path in paths.items()
        if _test_executable(name, exe_path)
    )
    safe_print(f"\n테스트 결과: {tests_passed}/{len(paths)} 통과")
    return tests_passed == len(paths)


def _test_executable(name, exe_path):
    if Path(exe_path).exists():
        safe_print(f"✅ {name}: {exe_path}")
        return True
    safe_print(f"❌ {name}: 파일이 존재하지 않음 - {exe_path}")
    return False
