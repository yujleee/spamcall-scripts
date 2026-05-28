import importlib.util
import os
import platform
import subprocess
import sys
import threading
import builtins


def _find_system_python():
    """시스템에 설치된 Python 실행 파일 경로 반환"""
    creation_flags = subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
    candidates = ['py', 'python3', 'python']
    for cmd in candidates:
        try:
            result = subprocess.run(
                [cmd, '--version'],
                capture_output=True,
                timeout=5,
                creationflags=creation_flags,
            )
            if result.returncode == 0:
                return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
    return None

running_process = None
running_thread = None
script_should_stop = False


def stop_running_script():
    """실행 중인 스크립트 중지"""
    global running_process, running_thread, script_should_stop

    script_should_stop = True

    if running_process and running_process.poll() is None:
        try:
            running_process.terminate()
            try:
                running_process.wait(timeout=3)
                return True
            except subprocess.TimeoutExpired:
                running_process.kill()
                running_process.wait()
                return True
        except Exception as e:
            print(f"스크립트 중지 오류: {e}")
            return False

    if running_thread and running_thread.is_alive():
        try:
            import ctypes
            thread_id = running_thread.ident
            if thread_id is not None:
                exc = SystemExit
                res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(thread_id),
                    ctypes.py_object(exc),
                )
                if res == 0:
                    return False
                if res > 1:
                    ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, None)
                    return False
                return True
        except Exception as e:
            print(f"스레드 중지 오류: {e}")
            return False

    return False


def run_script_as_module(script_path, log_callback=None):
    """스크립트를 모듈로 로드하여 직접 실행 (EXE 환경용)"""
    global script_should_stop

    original_print = builtins.print

    def custom_print(*args, **kwargs):
        msg = ' '.join(str(arg) for arg in args)
        if log_callback:
            log_callback(msg)
        original_print(*args, **kwargs)

    builtins.print = custom_print
    try:
        spec = importlib.util.spec_from_file_location("script_module", script_path)
        script_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script_module)

        possible_names = ['add_spam_number', 'add_spam_words', 'main', 'run']
        main_function = next(
            (getattr(script_module, name) for name in possible_names if hasattr(script_module, name)),
            None,
        )

        if main_function and callable(main_function):
            if log_callback:
                log_callback(f"📞 메인 함수 '{main_function.__name__}' 실행 중...")
            main_function()
        else:
            if log_callback:
                log_callback("⚠️ 메인 함수를 찾을 수 없습니다. 스크립트 전체를 실행합니다.")
            script_module.__name__ = '__main__'
            code = compile(open(script_path, encoding='utf-8').read(), script_path, 'exec')
            exec(code, script_module.__dict__)

        if log_callback and not script_should_stop:
            log_callback("🎉 스크립트가 성공적으로 완료되었습니다!")

    except Exception as e:
        if log_callback:
            import traceback
            log_callback(f"❌ 스크립트 실행 오류: {e}")
            log_callback(traceback.format_exc())
    finally:
        builtins.print = original_print


def execute_script(
    script_filename,
    device_name,
    platform_version,
    platform_name="android",
    start_num=1,
    end_num=600,
    word_count=200,
    log_callback=None,
    finish_callback=None,
):
    """스크립트를 별도 프로세스 또는 스레드로 실행"""
    global running_process, running_thread, script_should_stop

    script_should_stop = False

    def run_in_thread():
        global running_process, script_should_stop

        try:
            script_path = os.path.join("scripts", script_filename)

            os.environ['APPIUM_DEVICE_NAME'] = device_name
            os.environ['APPIUM_PLATFORM_VERSION'] = platform_version
            os.environ['APPIUM_PLATFORM_NAME'] = platform_name
            os.environ['START_NUM'] = str(start_num)
            os.environ['END_NUM'] = str(end_num)
            os.environ['WORD_COUNT'] = str(word_count)

            if log_callback:
                log_callback(f"🚀 스크립트 시작: {script_filename}")

            if getattr(sys, 'frozen', False):
                if log_callback:
                    log_callback("📦 EXE 환경에서 실행합니다. 시스템 Python을 탐색합니다...")

                python_cmd = _find_system_python()

                if python_cmd:
                    if log_callback:
                        log_callback(f"🐍 시스템 Python({python_cmd})으로 스크립트를 실행합니다.")

                    env = os.environ.copy()
                    env['PYTHONUNBUFFERED'] = '1'

                    # PyInstaller의 _MEIPASS 경로가 PATH/PYTHONPATH에 포함되면
                    # 시스템 Python이 frozen exe용 .pyd(Python 3.10 등)를 잘못 로드해 충돌 발생
                    # → _MEIPASS 관련 경로를 환경에서 제거
                    if hasattr(sys, '_MEIPASS'):
                        meipass = sys._MEIPASS
                        sep = os.pathsep
                        for key in ('PATH', 'PYTHONPATH'):
                            val = env.get(key, '')
                            cleaned = sep.join(p for p in val.split(sep) if p and p != meipass)
                            if cleaned:
                                env[key] = cleaned
                            elif key in env:
                                del env[key]

                    creation_flags = subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0

                    running_process = subprocess.Popen(
                        [python_cmd, '-u', script_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=0,
                        encoding='utf-8',
                        errors='replace',
                        universal_newlines=True,
                        env=env,
                        creationflags=creation_flags,
                    )

                    while True:
                        if running_process.poll() is not None:
                            remaining = running_process.stdout.read()
                            if remaining and log_callback:
                                for line in remaining.strip().split('\n'):
                                    if line.strip():
                                        log_callback(line.strip())
                            break
                        try:
                            output = running_process.stdout.readline()
                            if output and log_callback:
                                log_callback(output.strip())
                        except Exception as e:
                            if log_callback:
                                log_callback(f"로그 읽기 오류: {e}")
                            break

                    return_code = running_process.wait()
                    if log_callback:
                        if return_code == 0:
                            log_callback("🎉 스크립트가 성공적으로 완료되었습니다!")
                        elif return_code == -15:
                            log_callback("⏹️ 스크립트가 사용자에 의해 중지되었습니다.")
                        else:
                            log_callback(f"❌ 스크립트가 오류로 종료되었습니다. (종료 코드: {return_code})")

                else:
                    if log_callback:
                        log_callback("⚠️ 시스템 Python을 찾을 수 없습니다. 내부 실행을 시도합니다.")

                    original_print = builtins.print

                    def custom_print(*args, **kwargs):
                        msg = ' '.join(str(arg) for arg in args)
                        if log_callback:
                            log_callback(msg)
                        original_print(*args, **kwargs)

                    builtins.print = custom_print
                    try:
                        with open(script_path, 'r', encoding='utf-8') as f:
                            script_code = f.read()

                        script_globals = {
                            '__name__': '__main__',
                            '__file__': script_path,
                            'script_should_stop': lambda: script_should_stop,
                        }
                        exec(compile(script_code, script_path, 'exec'), script_globals)

                        if log_callback:
                            if script_should_stop:
                                log_callback("⏹️ 스크립트가 사용자에 의해 중지되었습니다.")
                            else:
                                log_callback("🎉 스크립트가 성공적으로 완료되었습니다!")

                    except SystemExit:
                        if log_callback:
                            msg = "⏹️ 스크립트가 사용자에 의해 중지되었습니다." if script_should_stop else "✅ 스크립트가 종료되었습니다."
                            log_callback(msg)
                    except KeyboardInterrupt:
                        if log_callback:
                            log_callback("⏹️ 스크립트가 중단되었습니다.")
                    except Exception as e:
                        if log_callback:
                            import traceback
                            log_callback(f"❌ 스크립트 실행 오류: {e}")
                            log_callback(traceback.format_exc())
                    finally:
                        builtins.print = original_print

            else:
                env = os.environ.copy()
                env['PYTHONUNBUFFERED'] = '1'

                creation_flags = 0
                if platform.system() == 'Windows':
                    creation_flags = subprocess.CREATE_NO_WINDOW

                running_process = subprocess.Popen(
                    [sys.executable, '-u', script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=0,
                    encoding='utf-8',
                    errors='replace',
                    universal_newlines=True,
                    env=env,
                    creationflags=creation_flags,
                )

                while True:
                    if running_process.poll() is not None:
                        remaining = running_process.stdout.read()
                        if remaining and log_callback:
                            for line in remaining.strip().split('\n'):
                                if line.strip():
                                    log_callback(line.strip())
                        break
                    try:
                        output = running_process.stdout.readline()
                        if output and log_callback:
                            log_callback(output.strip())
                    except Exception as e:
                        if log_callback:
                            log_callback(f"로그 읽기 오류: {e}")
                        break

                return_code = running_process.wait()
                if log_callback:
                    if return_code == 0:
                        log_callback("🎉 스크립트가 성공적으로 완료되었습니다!")
                    elif return_code == -15:
                        log_callback("⏹️ 스크립트가 사용자에 의해 중지되었습니다.")
                    else:
                        log_callback(f"❌ 스크립트가 오류로 종료되었습니다. (종료 코드: {return_code})")

        except Exception as e:
            if log_callback:
                log_callback(f"❌ 스크립트 실행 오류: {e}")
        finally:
            running_process = None
            script_should_stop = False
            if finish_callback:
                finish_callback()

    if running_process and running_process.poll() is None:
        if log_callback:
            log_callback("⚠️ 이전 스크립트를 중지하고 새 스크립트를 시작합니다.")
        stop_running_script()

    running_thread = threading.Thread(target=run_in_thread, daemon=True)
    running_thread.start()
    return running_thread


def is_script_running():
    """스크립트가 실행 중인지 확인"""
    if running_process is not None and running_process.poll() is None:
        return True
    if running_thread is not None and running_thread.is_alive():
        return True
    return False
