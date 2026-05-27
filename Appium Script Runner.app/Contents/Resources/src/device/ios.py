import subprocess


def _ideviceinfo(udid, key):
    """ideviceinfo로 특정 속성 값 가져오기"""
    try:
        result = subprocess.run(
            ['ideviceinfo', '-u', udid, '-k', key],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else "Unknown"
    except Exception:
        return "Unknown"


def check_ios_connection():
    """libimobiledevice로 연결된 iOS 디바이스 확인 및 정보 수집"""
    try:
        result = subprocess.run(
            ['idevice_id', '-l'],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return None

        udids = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        if not udids:
            return None

        udid = udids[0]
        device_name = _ideviceinfo(udid, 'DeviceName')
        ios_version = _ideviceinfo(udid, 'ProductVersion')
        model = _ideviceinfo(udid, 'ProductType')

        return {
            'deviceName': udid,
            'platformVersion': ios_version,
            'model': device_name if device_name != "Unknown" else model,
            'platform': 'ios',
        }

    except FileNotFoundError:
        return None
    except Exception:
        return None
