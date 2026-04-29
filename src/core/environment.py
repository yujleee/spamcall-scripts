import subprocess
import sys
from utils.safe_print import safe_print


def check_command_available(command, version_flag='--version', timeout=5):
    """명령어가 사용 가능한지 확인"""
    commands_to_try = [command]

    if sys.platform == 'win32':
        commands_to_try.extend([
            f"{command}.exe",
            f"{command}.cmd",
            f"{command}.bat",
        ])

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
    check_result['all_available'] = False
    show_missing_tools_dialog(missing_tools)

    if get_check_result:
        return False, check_result
    return False
