import subprocess
import platform

from src.core.environment import _get_env_with_full_path


def get_device_property(device_id, prop_name):
    """디바이스 속성 값 가져오기"""
    try:
        result = subprocess.run(
            ['adb', '-s', device_id, 'shell', 'getprop', prop_name],
            capture_output=True,
            text=True,
            timeout=5,
            env=_get_env_with_full_path(),
        )
        return result.stdout.strip() if result.returncode == 0 else "Unknown"
    except Exception:
        return "Unknown"


def check_adb_connection():
    """ADB 디바이스 연결 확인 및 정보 수집"""
    try:
        result = subprocess.run(
            ['adb', 'devices'],
            capture_output=True,
            text=True,
            timeout=10,
            env=_get_env_with_full_path(),
        )
        if result.returncode != 0:
            return None

        lines = result.stdout.strip().split('\n')[1:]
        devices = [line.split('\t')[0] for line in lines if 'device' in line and line.strip()]
        if not devices:
            return None

        device_id = devices[0]
        return {
            'deviceName': device_id,
            'platformVersion': get_device_property(device_id, 'ro.build.version.release'),
            'model': get_device_property(device_id, 'ro.product.model'),
        }
    except Exception:
        return None


def auto_open_appium_terminal():
    """GUI 시작 시 자동으로 터미널 열고 appium 실행"""
    system = platform.system()

    if system == 'Darwin':
        applescript = 'tell application "Terminal"\n    do script "appium"\nend tell'
        subprocess.run(['osascript', '-e', applescript])
    elif system == 'Windows':
        subprocess.Popen(['cmd', '/k', 'appium'], creationflags=subprocess.CREATE_NEW_CONSOLE)
