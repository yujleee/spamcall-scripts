import subprocess
import os
import signal
import shutil
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

from src.core.environment import _get_env_with_full_path

_appium_process = None
_appium_starting = False
_appium_lock = threading.Lock()
_appium_log_path = None


def _appium_is_ready():
    """현재 Appium 서버가 4723 포트에서 준비됐는지 확인"""
    try:
        with urllib.request.urlopen('http://127.0.0.1:4723/status', timeout=1) as response:
            import json
            payload = json.loads(response.read().decode('utf-8'))
        return payload.get('value', {}).get('ready') is True
    except (OSError, ValueError, urllib.error.URLError):
        return False


def _resolve_appium_command(env):
    """포터블 런타임을 우선 사용하고, 없으면 시스템 Appium을 찾는다."""
    from src.core.environment import _is_portable_build

    if sys.platform == 'win32':
        if _is_portable_build():
            from src.core.runtime import get_runtime_paths
            paths = get_runtime_paths()
            paths['appium_dir'].mkdir(parents=True, exist_ok=True)
            env['APPIUM_HOME'] = str(paths['appium_dir'])
            appium_path = paths['appium_dir'] / 'node_modules' / '.bin' / 'appium.cmd'
            if appium_path.exists():
                return ['cmd', '/c', str(appium_path), '--port', '4723']
        appium_path = shutil.which('appium.cmd', path=env.get('PATH')) or shutil.which('appium', path=env.get('PATH'))
        return ['cmd', '/c', appium_path, '--port', '4723'] if appium_path else None

    if _is_portable_build():
        from src.core.runtime import get_runtime_paths
        paths = get_runtime_paths()
        paths['appium_dir'].mkdir(parents=True, exist_ok=True)
        env['APPIUM_HOME'] = str(paths['appium_dir'])
        appium_path = paths['appium_dir'] / 'node_modules' / '.bin' / 'appium'
        if appium_path.exists():
            return [str(appium_path), '--port', '4723']

    appium_path = shutil.which('appium', path=env.get('PATH'))
    return [appium_path, '--port', '4723'] if appium_path else None


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


def auto_open_appium_terminal(log_callback=None):
    """GUI 시작 시 Appium 서버를 백그라운드에서 시작하고 준비 상태를 로그로 알림"""
    global _appium_process, _appium_starting, _appium_log_path

    log = log_callback
    with _appium_lock:
        if _appium_starting:
            return
        if _appium_is_ready():
            if log:
                log('✅ Appium 서버가 이미 실행 중입니다 (http://127.0.0.1:4723).')
            return

        env = _get_env_with_full_path()
        try:
            command = _resolve_appium_command(env)
        except Exception as exc:
            if log:
                log(f'❌ Appium 런타임 경로를 준비하지 못했습니다: {exc}')
            return
        if not command:
            if log:
                log('❌ Appium 실행 파일을 찾지 못했습니다. 포터블 런타임 설치 상태를 확인해주세요.')
            return

        try:
            if env.get('APPIUM_HOME'):
                log_dir = Path(env['APPIUM_HOME'])
            else:
                log_dir = Path.home() / '.appium'
            log_dir.mkdir(parents=True, exist_ok=True)
            _appium_log_path = log_dir / 'appium-server.log'
            log_file = open(_appium_log_path, 'a', encoding='utf-8')
            popen_options = {
                'env': env,
                'stdin': subprocess.DEVNULL,
                'stdout': log_file,
                'stderr': subprocess.STDOUT,
            }
            if sys.platform == 'win32':
                popen_options['creationflags'] = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            else:
                popen_options['start_new_session'] = True

            try:
                _appium_process = subprocess.Popen(command, **popen_options)
            finally:
                log_file.close()
            _appium_starting = True
            if log:
                log('🚀 Appium 서버 시작 중...')
        except Exception as exc:
            if log:
                log(f'❌ Appium 서버 시작 실패: {exc}')
            return

    threading.Thread(target=_wait_for_appium, args=(log,), daemon=True).start()


def _wait_for_appium(log_callback):
    global _appium_starting
    deadline = time.monotonic() + 25
    while time.monotonic() < deadline:
        if _appium_is_ready():
            if log_callback:
                log_callback('✅ Appium 서버 준비 완료 (http://127.0.0.1:4723).')
            with _appium_lock:
                _appium_starting = False
            return

        with _appium_lock:
            process = _appium_process
            if process and process.poll() is not None:
                _appium_starting = False
                if log_callback:
                    details = _read_appium_log_tail()
                    log_callback(
                        f'❌ Appium 서버가 시작되지 않았습니다 (종료 코드: {process.returncode}).'
                        + (f' 로그: {details}' if details else '')
                    )
                return
        time.sleep(0.5)

    with _appium_lock:
        _appium_starting = False
    if log_callback:
        log_callback('❌ Appium 서버가 25초 안에 준비되지 않았습니다. 런타임과 Appium 로그를 확인해주세요.')


def _read_appium_log_tail():
    if not _appium_log_path:
        return ''
    try:
        lines = _appium_log_path.read_text(encoding='utf-8', errors='replace').splitlines()
        return ' | '.join(lines[-8:])[-1200:]
    except OSError:
        return ''


def stop_appium_server():
    """이 앱이 시작한 Appium 서버와 같은 프로세스 그룹의 자식들을 종료"""
    global _appium_process, _appium_starting
    with _appium_lock:
        process = _appium_process
        _appium_process = None
        _appium_starting = False

    if not process:
        return

    if sys.platform == 'win32':
        if process.poll() is None:
            subprocess.run(
                ['taskkill', '/PID', str(process.pid), '/T', '/F'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=5,
            )
        return

    # Appium이 띄운 xcodebuild/iproxy 같은 자식이 서버 종료 후에도 남으면
    # WDA의 8100 포트 포워딩이 계속 점유될 수 있다. 별도 세션으로 시작했으므로
    # 그 프로세스 그룹만 종료해 다른 터미널의 Appium에는 손대지 않는다.
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return

    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass

    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass

    if process.poll() is None:
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass
