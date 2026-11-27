import atexit
import json
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
_appium_setup_process = None
_appium_pid = None
_appium_process_group_id = None
_appium_starting = False
_appium_start_attempted = False
_appium_start_cancelled = threading.Event()
_appium_lock = threading.Lock()
_appium_log_path = None
_appium_state_path = Path.home() / '.appium-script-runner' / 'appium-server.json'


def _appium_is_ready():
    """현재 Appium 서버가 4723 포트에서 준비됐는지 확인"""
    try:
        with urllib.request.urlopen('http://127.0.0.1:4723/status', timeout=1) as response:
            import json
            payload = json.loads(response.read().decode('utf-8'))
        return payload.get('value', {}).get('ready') is True
    except (OSError, ValueError, urllib.error.URLError):
        return False


def _write_appium_state(pid, process_group_id):
    """프로그램이 시작한 Appium의 소유 정보를 다음 실행에서도 확인할 수 있게 저장"""
    try:
        _appium_state_path.parent.mkdir(parents=True, exist_ok=True)
        _appium_state_path.write_text(
            json.dumps({
                'pid': pid,
                'process_group_id': process_group_id,
                'owner_pid': os.getpid(),
            }),
            encoding='utf-8',
        )
    except OSError:
        pass


def _remove_appium_state():
    try:
        _appium_state_path.unlink(missing_ok=True)
    except OSError:
        pass


def _adopt_previous_appium():
    """이전 GUI가 비정상 종료해 남긴 Appium만 다시 소유권을 가져온다."""
    global _appium_pid, _appium_process_group_id

    try:
        state = json.loads(_appium_state_path.read_text(encoding='utf-8'))
        pid = int(state['pid'])
        owner_pid = int(state['owner_pid'])
        process_group_id = state.get('process_group_id')
        process_group_id = int(process_group_id) if process_group_id else None
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        _remove_appium_state()
        return False

    # 이전 GUI가 아직 실행 중이면 다른 GUI가 해당 Appium을 가로채지 않는다.
    try:
        os.kill(owner_pid, 0)
        return False
    except ProcessLookupError:
        pass
    except PermissionError:
        return False

    try:
        os.kill(pid, 0)
    except (ProcessLookupError, PermissionError):
        _remove_appium_state()
        return False

    # PID가 재사용된 경우 엉뚱한 프로세스를 종료하지 않도록 Appium인지 검증한다.
    if sys.platform != 'win32':
        result = subprocess.run(
            ['ps', '-p', str(pid), '-o', 'command='],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode != 0 or 'appium' not in result.stdout.lower():
            _remove_appium_state()
            return False

    _appium_pid = pid
    _appium_process_group_id = process_group_id
    return True


def _adopt_appium_listener():
    """4723을 쓰는 기존 Appium도 GUI가 사용하면 종료 대상에 등록한다."""
    global _appium_pid, _appium_process_group_id

    if sys.platform == 'win32':
        return False

    # 이미 다른 GUI 인스턴스가 관리 중인 서버는 가로채지 않는다.
    try:
        state = json.loads(_appium_state_path.read_text(encoding='utf-8'))
        owner_pid = int(state['owner_pid'])
        os.kill(owner_pid, 0)
        return False
    except ProcessLookupError:
        pass
    except PermissionError:
        return False
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        pass

    try:
        result = subprocess.run(
            ['lsof', '-nP', '-t', '-iTCP:4723', '-sTCP:LISTEN'],
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return False

    for line in result.stdout.splitlines():
        try:
            pid = int(line.strip())
            command = subprocess.run(
                ['ps', '-p', str(pid), '-o', 'command='],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if command.returncode != 0 or 'appium' not in command.stdout.lower():
                continue

            # 새 세션으로 띄운 Appium(이전 GUI 포함)은 그룹째 정리할 수 있다.
            # 터미널에서 실행된 서버는 해당 터미널의 프로세스 그룹을 건드리지 않는다.
            process_group_id = os.getpgid(pid)
            if process_group_id != pid:
                process_group_id = None
            _appium_pid = pid
            _appium_process_group_id = process_group_id
            _write_appium_state(pid, process_group_id)
            return True
        except (ValueError, ProcessLookupError, PermissionError, OSError, subprocess.SubprocessError):
            continue
    return False


def _get_process_tree_pids(root_pid):
    """특정 서버의 자식 PID만 조회해 터미널 프로세스 그룹은 건드리지 않는다."""
    result = subprocess.run(
        ['ps', '-axo', 'pid=,ppid='],
        capture_output=True,
        text=True,
        timeout=2,
    )
    children = {}
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        try:
            pid, parent_pid = map(int, parts)
        except ValueError:
            continue
        children.setdefault(parent_pid, []).append(pid)

    ordered = []
    pending = [root_pid]
    while pending:
        parent_pid = pending.pop()
        descendants = children.get(parent_pid, [])
        ordered.extend(descendants)
        pending.extend(descendants)
    return ordered + [root_pid]


def _terminate_appium_process(process, pid, process_group_id):
    if not pid:
        return

    if sys.platform == 'win32':
        subprocess.run(
            ['taskkill', '/PID', str(pid), '/T', '/F'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=5,
        )
        return

    target_pids = [] if process_group_id else _get_process_tree_pids(pid)

    def target_exists():
        if process_group_id:
            try:
                os.killpg(process_group_id, 0)
                return True
            except ProcessLookupError:
                return False
            except PermissionError:
                return True

        for target_pid in target_pids:
            try:
                os.kill(target_pid, 0)
                return True
            except ProcessLookupError:
                continue
            except PermissionError:
                return True
        return False

    if process_group_id:
        try:
            os.killpg(process_group_id, signal.SIGTERM)
        except ProcessLookupError:
            _remove_appium_state()
            return
    else:
        for target_pid in target_pids:
            try:
                os.kill(target_pid, signal.SIGTERM)
            except ProcessLookupError:
                continue

    deadline = time.monotonic() + 5
    while target_exists() and time.monotonic() < deadline:
        time.sleep(0.1)

    if target_exists():
        try:
            if process_group_id:
                os.killpg(process_group_id, signal.SIGKILL)
            else:
                for target_pid in target_pids:
                    try:
                        os.kill(target_pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
        except ProcessLookupError:
            pass

    if process and process.poll() is None:
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            pass


def _appium_cli_prefix(command):
    if len(command) >= 3 and command[0].lower() == 'cmd' and command[1].lower() == '/c':
        return command[:3]
    return command[:1]


def _uiautomator2_install_spec(command, env):
    result = subprocess.run(
        _appium_cli_prefix(command) + ['--version'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        env=env,
        timeout=25,
    )
    version_text = (result.stdout or result.stderr).strip()
    version_parts = version_text.split('.', 2)
    try:
        major = int(version_parts[0])
        minor = int(version_parts[1]) if len(version_parts) > 1 else 0
    except (ValueError, IndexError):
        raise RuntimeError(f'Appium 버전을 확인하지 못했습니다: {version_text}')

    if major == 2:
        # Appium 2.0의 peer dependency는 UiAutomator2 2.x를 요구한다.
        return 'uiautomator2@^2.0.0' if minor < 4 else 'uiautomator2@4.2.9'
    if major == 3:
        return 'uiautomator2@8.7.3'
    if major >= 4:
        return 'uiautomator2'
    raise RuntimeError(f'Appium {version_text}에서는 UiAutomator2 드라이버 자동 설치를 지원하지 않습니다.')


def _uiautomator2_is_installed(command, env):
    result = subprocess.run(
        _appium_cli_prefix(command) + ['driver', 'list', '--installed', '--json'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        env=env,
        timeout=30,
    )
    output = f'{result.stdout}\n{result.stderr}'.lower()
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip() or 'Appium driver list 실패')
    try:
        drivers = json.loads(result.stdout)
        return 'uiautomator2' in json.dumps(drivers).lower()
    except json.JSONDecodeError:
        return 'uiautomator2' in output


def _install_uiautomator2_driver(command, env, log_callback):
    global _appium_setup_process

    if _uiautomator2_is_installed(command, env):
        if log_callback:
            log_callback('✅ UiAutomator2 드라이버가 이미 설치되어 있습니다.')
        return True
    if _appium_start_cancelled.is_set():
        return False

    spec = _uiautomator2_install_spec(command, env)
    if log_callback:
        log_callback(f'📦 Android 자동화 드라이버 설치 중 ({spec}). 첫 설치에는 인터넷 연결이 필요합니다...')

    appium_home = env.get('APPIUM_HOME') or str(Path.home() / '.appium')
    log_path = Path(appium_home) / 'appium-server.log'
    log_path.parent.mkdir(parents=True, exist_ok=True)
    popen_options = {
        'env': env,
        'stdin': subprocess.DEVNULL,
        'stdout': open(log_path, 'a', encoding='utf-8'),
        'stderr': subprocess.STDOUT,
    }
    if sys.platform == 'win32':
        popen_options['creationflags'] = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
    else:
        popen_options['start_new_session'] = True

    try:
        process = subprocess.Popen(
            _appium_cli_prefix(command) + ['driver', 'install', spec],
            **popen_options,
        )
    finally:
        popen_options['stdout'].close()

    with _appium_lock:
        _appium_setup_process = process

    deadline = time.monotonic() + 300
    try:
        while process.poll() is None:
            if _appium_start_cancelled.is_set():
                _terminate_appium_process(
                    process,
                    process.pid,
                    process.pid if sys.platform != 'win32' else None,
                )
                return False
            if time.monotonic() >= deadline:
                _terminate_appium_process(
                    process,
                    process.pid,
                    process.pid if sys.platform != 'win32' else None,
                )
                if log_callback:
                    log_callback('❌ UiAutomator2 드라이버 설치 시간이 초과되었습니다.')
                return False
            time.sleep(0.2)
    finally:
        with _appium_lock:
            if _appium_setup_process is process:
                _appium_setup_process = None

    if process.returncode != 0:
        details = _read_appium_log_tail()
        if log_callback:
            log_callback('❌ UiAutomator2 드라이버 설치 실패.' + (f' 로그: {details}' if details else ''))
        return False

    if log_callback:
        log_callback('✅ UiAutomator2 드라이버 설치 완료.')
    return _uiautomator2_is_installed(command, env)


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
    """필수 드라이버를 확인한 뒤 Appium 서버를 백그라운드에서 시작"""
    global _appium_start_attempted, _appium_starting, _appium_log_path

    log = log_callback
    with _appium_lock:
        if _appium_starting:
            return
        _appium_start_attempted = True

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

        log_dir = Path(env.get('APPIUM_HOME') or (Path.home() / '.appium'))
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            if log:
                log(f'❌ Appium 데이터 폴더를 준비하지 못했습니다: {exc}')
            return
        _appium_log_path = log_dir / 'appium-server.log'
        _appium_start_cancelled.clear()
        _appium_starting = True

    threading.Thread(
        target=_prepare_and_start_appium,
        args=(command, env, log),
        daemon=True,
    ).start()


def wait_for_appium_ready(timeout=300, should_cancel=None):
    """서버/드라이버 첫 설치가 끝날 때까지 스크립트 실행 스레드에서 대기"""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if should_cancel and should_cancel():
            return False
        if _appium_start_cancelled.is_set():
            return False

        with _appium_lock:
            start_attempted = _appium_start_attempted
            starting = _appium_starting
            failed = (
                start_attempted
                and not starting
                and _appium_process is None
                and _appium_setup_process is None
            )
        # Wait for auto_open_appium_terminal to finish driver verification too;
        # /status can respond while that preparation is still in progress.
        if start_attempted and not starting and _appium_is_ready():
            return True
        if failed:
            return False
        time.sleep(0.25)
    return False


def _prepare_and_start_appium(command, env, log_callback):
    global _appium_process, _appium_pid, _appium_process_group_id, _appium_starting

    try:
        driver_installed = _uiautomator2_is_installed(command, env)
        server_ready = _appium_is_ready()

        if server_ready and driver_installed:
            if not _adopt_previous_appium():
                _adopt_appium_listener()
            if log_callback:
                log_callback('✅ Appium 서버와 UiAutomator2 드라이버가 준비되어 있습니다.')
            with _appium_lock:
                _appium_starting = False
            return

        if server_ready and not driver_installed:
            if not _adopt_previous_appium() and not _adopt_appium_listener():
                raise RuntimeError(
                    '기존 Appium 서버에 UiAutomator2 드라이버가 없습니다. '
                    '다른 Appium 인스턴스를 종료한 뒤 다시 실행해주세요.'
                )
            if log_callback:
                log_callback('⚠️ 기존 Appium 서버를 드라이버 설치를 위해 재시작합니다...')
            stop_appium_server()
            _appium_start_cancelled.clear()

        # 이전 GUI가 비정상 종료해 Appium/WDA 자식이 남아 있으면 새 서버 전에 정리한다.
        elif _adopt_previous_appium():
            stop_appium_server()
            _appium_start_cancelled.clear()

        if not driver_installed:
            if not _install_uiautomator2_driver(command, env, log_callback):
                raise RuntimeError('UiAutomator2 드라이버를 설치하지 못했습니다. 인터넷 연결과 Appium 로그를 확인해주세요.')

        if _appium_start_cancelled.is_set():
            return

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
            process = subprocess.Popen(command, **popen_options)
        finally:
            log_file.close()

        with _appium_lock:
            if _appium_start_cancelled.is_set():
                should_stop = True
            else:
                _appium_process = process
                _appium_pid = process.pid
                _appium_process_group_id = process.pid if sys.platform != 'win32' else None
                _write_appium_state(_appium_pid, _appium_process_group_id)
                should_stop = False

        if should_stop:
            _terminate_appium_process(
                process,
                process.pid,
                process.pid if sys.platform != 'win32' else None,
            )
            return

        if log_callback:
            log_callback('🚀 Appium 서버 시작 중...')
        threading.Thread(target=_wait_for_appium, args=(log_callback,), daemon=True).start()
    except Exception as exc:
        if log_callback and not _appium_start_cancelled.is_set():
            log_callback(f'❌ Appium 서버 준비 실패: {exc}')
        with _appium_lock:
            _appium_starting = False


def _wait_for_appium(log_callback):
    global _appium_process, _appium_starting, _appium_pid, _appium_process_group_id
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
                _appium_process = None
                _appium_starting = False
                _appium_pid = None
                _appium_process_group_id = None
                _remove_appium_state()
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
    """이 앱이 시작한 Appium 서버와 자식 프로세스들을 종료"""
    global _appium_process, _appium_setup_process, _appium_pid, _appium_process_group_id
    global _appium_starting
    with _appium_lock:
        process = _appium_process
        setup_process = _appium_setup_process
        pid = _appium_pid
        if pid is None and process and process.poll() is None:
            pid = process.pid
        process_group_id = _appium_process_group_id
        _appium_process = None
        _appium_setup_process = None
        _appium_pid = None
        _appium_process_group_id = None
        _appium_starting = False
        _appium_start_cancelled.set()

    if setup_process and setup_process.poll() is None:
        try:
            _terminate_appium_process(
                setup_process,
                setup_process.pid,
                setup_process.pid if sys.platform != 'win32' else None,
            )
        except (OSError, subprocess.SubprocessError):
            setup_process.kill()

    if not pid:
        _remove_appium_state()
        return

    try:
        # Appium이 띄운 xcodebuild/iproxy 등 자식도 종료해 WDA 포워딩 포트를
        # 해제한다. 기존 실행에서 저장해 둔 PID/그룹도 같은 경로로 정리한다.
        _terminate_appium_process(process, pid, process_group_id)
    except (OSError, subprocess.SubprocessError):
        if process and process.poll() is None:
            process.kill()
    finally:
        _remove_appium_state()


atexit.register(stop_appium_server)


def _handle_app_termination(signum, _frame):
    stop_appium_server()
    raise SystemExit(128 + signum)


for _termination_signal in (signal.SIGTERM, signal.SIGINT):
    try:
        signal.signal(_termination_signal, _handle_app_termination)
    except ValueError:
        # 이 모듈이 메인 스레드가 아닌 곳에서 import된 경우에는 등록할 수 없다.
        pass
