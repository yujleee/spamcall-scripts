import os
import subprocess
import sys
from pathlib import Path
from utils.safe_print import safe_print


def _is_portable_build():
    """portable.flag 파일 존재 여부로 포터블 빌드 감지"""
    if getattr(sys, 'frozen', False):
        base = Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
    else:
        base = Path(__file__).parent.parent.parent
    return (base / 'portable.flag').exists()


def _get_portable_bin_paths():
    """설치된 포터블 런타임의 bin 경로 목록 반환"""
    try:
        from src.core.runtime import get_runtime_paths
        paths = get_runtime_paths()
        if not paths:
            return []

        system = paths['system']
        if system == 'darwin':
            candidates = [
                paths['node_dir'] / 'bin',
                paths['appium_dir'] / 'node_modules' / '.bin',
                paths['adb_dir'],
            ]
        else:
            candidates = [
                paths['node_dir'],
                paths['appium_dir'] / 'node_modules' / '.bin',
                paths['adb_dir'],
            ]
        return [str(p) for p in candidates if p.exists()]
    except Exception:
        return []


def _get_env_with_full_path():
    """GUI/EXE 실행 시 shell PATH가 누락되는 문제를 보완"""
    env = os.environ.copy()

    if sys.platform == 'win32':
        appdata = os.environ.get('APPDATA', '')
        localappdata = os.environ.get('LOCALAPPDATA', '')
        android_home = (
            os.environ.get('ANDROID_HOME')
            or os.environ.get('ANDROID_SDK_ROOT')
            or os.path.join(localappdata, 'Android', 'Sdk')
        )
        common_paths = [
            os.path.join(appdata, 'npm'),                          # appium (npm global)
            r'C:\Program Files\nodejs',                            # Node.js
            os.path.join(android_home, 'platform-tools'),          # adb
            os.path.join(android_home, 'tools'),
        ]
        existing = env.get('PATH', '').split(os.pathsep)
        extra = [p for p in common_paths if p and p not in existing]
        if extra:
            env['PATH'] = os.pathsep.join(extra) + os.pathsep + env.get('PATH', '')
    else:
        # zsh -l 은 ~/.zshrc를 소싱하지 않으므로 공통 경로는 항상 직접 추가
        common_paths = [
            '/usr/local/bin',
            '/opt/homebrew/bin',
            '/opt/homebrew/sbin',
            '/usr/local/sbin',
            os.path.expanduser('~/Library/Android/sdk/platform-tools'),
            os.path.expanduser('~/Library/Android/sdk/tools'),
            os.path.expanduser('~/.nvm/versions/node/default/bin'),
        ]

        # shell에서 PATH도 가져와서 병합
        shell_path = ''
        try:
            shell = os.environ.get('SHELL', '/bin/zsh')
            result = subprocess.run(
                [shell, '-l', '-c', 'echo $PATH'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                shell_path = result.stdout.strip()
        except Exception:
            pass

        portable_paths = _get_portable_bin_paths()
        base_path = shell_path or env.get('PATH', '')
        env['PATH'] = ':'.join(portable_paths + common_paths) + ':' + base_path

    return env


def check_command_available(command, version_flag='--version', timeout=10):
    """명령어가 사용 가능한지 확인"""
    if sys.platform == 'win32':
        # .cmd를 먼저 시도해야 extension-less 스크립트로 인한 hang 방지
        commands_to_try = [
            f"{command}.cmd",
            f"{command}.exe",
            f"{command}.bat",
            command,
        ]
    else:
        commands_to_try = [command]

    env = _get_env_with_full_path()

    for cmd in commands_to_try:
        try:
            result = subprocess.run(
                [cmd, version_flag],
                capture_output=True,
                timeout=timeout,
                text=True,
                encoding='utf-8',
                errors='replace',
                shell=sys.platform == 'win32',
                env=env,
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            continue
        except Exception as e:
            safe_print(f"{cmd} 확인 중 오류: {e}")
            continue

    return False, None


def check_system_environment(get_versions=False):
    """시스템 실행환경 확인"""
    safe_print("🔍 시스템 실행환경 확인 중...")

    node_available, node_version = check_command_available('node', '--version')
    if node_available:
        safe_print(f"✅ Node.js: {node_version}")

    appium_available, appium_version = check_command_available('appium', '--version')
    if not appium_available:
        npm_available, npm_output = check_command_available('npm', 'list -g appium --depth=0')
        if npm_available and npm_output and 'appium@' in npm_output:
            appium_available = True
            appium_version = "(npm global)"
    if appium_available:
        safe_print(f"✅ Appium: {appium_version}")

    adb_available, adb_version = check_command_available('adb', 'version')
    if adb_available:
        safe_print(f"✅ ADB: {adb_version.split(chr(10))[0] if adb_version else 'Unknown'}")

    if get_versions:
        return {
            'node': {'available': node_available, 'version': node_version},
            'appium': {'available': appium_available, 'version': appium_version},
            'adb': {
                'available': adb_available,
                'version': adb_version.split('\n')[0] if adb_version else None,
            },
        }

    tools_status = {
        'node': node_available,
        'appium': appium_available,
        'adb': adb_available,
    }
    available_tools = [t for t, ok in tools_status.items() if ok]
    missing_tools = [t for t, ok in tools_status.items() if not ok]
    return tools_status, available_tools, missing_tools


def check_environment_and_setup(get_check_result=False):
    """환경 체크 및 필요시 설정 — 메인 함수"""
    from src.gui.dialogs import show_missing_tools_dialog

    check_result = {
        'node': {'available': False, 'version': None},
        'appium': {'available': False, 'version': None},
        'adb': {'available': False, 'version': None},
        'all_available': False,
    }

    tools_info = check_system_environment(get_versions=True)
    check_result.update(tools_info)
    missing_tools = [tool for tool, info in tools_info.items() if not info.get('available')]

    if not missing_tools:
        safe_print("🎉 모든 필수 도구가 설치되어 있습니다!")
        check_result['all_available'] = True
        if get_check_result:
            return True, check_result
        return True

    safe_print(f"⚠️ 누락된 도구: {', '.join(missing_tools)}")

    # 포터블 빌드인 경우 자동 설치 시도
    if _is_portable_build():
        from src.core.runtime import check_runtime_exists
        from src.gui.dialogs import show_runtime_install_dialog

        if not check_runtime_exists():
            safe_print("📦 포터블 런타임 설치 필요 — 다운로드 시작")
            installed = show_runtime_install_dialog()
            if not installed:
                check_result['all_available'] = False
                show_missing_tools_dialog(missing_tools)
                if get_check_result:
                    return False, check_result
                return False

        # 설치 후 재확인
        tools_info = check_system_environment(get_versions=True)
        check_result.update(tools_info)
        missing_tools = [tool for tool, info in tools_info.items() if not info.get('available')]

        if not missing_tools:
            safe_print("🎉 포터블 환경으로 모든 도구를 사용할 수 있습니다!")
            check_result['all_available'] = True
            if get_check_result:
                return True, check_result
            return True

    check_result['all_available'] = False
    show_missing_tools_dialog(missing_tools)

    if get_check_result:
        return False, check_result
    return False
