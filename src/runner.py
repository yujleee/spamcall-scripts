import subprocess
import threading
import platform
import os
import sys
from pathlib import Path
import importlib.util

# 스크립트 파일명과 GUI에 표시할 이름 매핑
SCRIPT_MAPPING = {
    "ixiO_add_spamList.py": "익시오 - 스팸 번호 추가",
    "ixiO_add_spam_words.py": "익시오 - 스팸 단어 추가",
    "mobileManager_add_spam_number.py": "모바일매니저 - 스팸 번호 추가", 
    "spamcallnoti_add_spam_number.py": "스팸전화알림 - 스팸 번호 추가",
    "mobileManager_add_spam_words.py": "모바일매니저 - 스팸 단어 추가"
}

# 실행 중인 프로세스를 관리하는 전역 변수
running_process = None
running_thread = None
script_should_stop = False

def auto_open_appium_terminal():
    """GUI 시작 시 자동으로 터미널 열고 appium 실행"""
    system = platform.system()
    
    if system == 'Darwin':  # macOS
        applescript = '''tell application "Terminal"
            do script "appium"
        end tell'''
        subprocess.run(['osascript', '-e', applescript])
        
    elif system == 'Windows':  # Windows
        subprocess.Popen(['cmd', '/k', 'appium'], creationflags=subprocess.CREATE_NEW_CONSOLE)

def get_available_scripts():
    """사용 가능한 스크립트들을 찾아서 반환"""
    scripts_dir = Path("scripts")
    if not scripts_dir.exists():
        return {}
    
    available_scripts = {}
    for filename, display_name in SCRIPT_MAPPING.items():
        script_path = scripts_dir / filename
        if script_path.exists():
            available_scripts[display_name] = filename
    
    return available_scripts

def get_device_property(device_id, prop_name):
    """디바이스 속성 값 가져오기"""
    try:
        result = subprocess.run(['adb', '-s', device_id, 'shell', 'getprop', prop_name],
                              capture_output=True, text=True, timeout=5)
        return result.stdout.strip() if result.returncode == 0 else "Unknown"
    except:
        return "Unknown"

def check_adb_connection():
    """ADB 디바이스 연결 확인 및 정보 수집"""
    try:
        result = subprocess.run(['adb', 'devices'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            return None
        
        # 연결된 디바이스 파싱
        lines = result.stdout.strip().split('\n')[1:]
        devices = [line.split('\t')[0] for line in lines if 'device' in line and line.strip()]
        
        if not devices:
            return None
        
        # 첫 번째 디바이스 정보 수집
        device_id = devices[0]
        device_model = get_device_property(device_id, 'ro.product.model')
        android_version = get_device_property(device_id, 'ro.build.version.release')
        
        return {
            'deviceName': device_id,
            'platformVersion': android_version,
            'model': device_model
        }
        
    except Exception:
        return None

def stop_running_script():
    """실행 중인 스크립트 중지"""
    global running_process, running_thread, script_should_stop
    
    script_should_stop = True
    
    # subprocess로 실행 중인 경우 (일반 Python 환경)
    if running_process and running_process.poll() is None:
        try:
            running_process.terminate()
            # 강제 종료가 필요한 경우
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
    
    # 스레드로 실행 중인 경우 (EXE 환경)
    if running_thread and running_thread.is_alive():
        try:
            # Python 스레드는 안전하게 강제 종료할 수 없으므로
            # 프로세스 자체를 종료하는 방법 사용
            import ctypes
            
            # 스레드 ID 가져오기
            thread_id = running_thread.ident
            
            if thread_id is not None:
                # 스레드에 SystemExit 예외 발생시키기 (Python 3.7+)
                exc = SystemExit
                res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(thread_id), 
                    ctypes.py_object(exc)
                )
                
                if res == 0:
                    # 스레드 ID가 유효하지 않음
                    print("스레드를 찾을 수 없습니다.")
                    return False
                elif res > 1:
                    # 여러 스레드에 영향을 줬다면 되돌리기
                    ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, None)
                    print("스레드 중지 실패")
                    return False
                
                print("스레드 중지 요청 완료")
                return True
        except Exception as e:
            print(f"스레드 중지 오류: {e}")
            return False
    
    return False

def run_script_as_module(script_path, log_callback=None):
    """스크립트를 모듈로 로드하여 직접 실행 (EXE 환경용)"""
    global script_should_stop
    
    try:
        # 스크립트를 모듈로 로드
        spec = importlib.util.spec_from_file_location("script_module", script_path)
        script_module = importlib.util.module_from_spec(spec)
        
        # 원래의 print 함수를 저장
        original_print = print
        
        # 커스텀 print 함수
        def custom_print(*args, **kwargs):
            msg = ' '.join(str(arg) for arg in args)
            if log_callback:
                log_callback(msg)
            # 원본 print도 호출 (디버깅용)
            original_print(*args, **kwargs)
        
        # print 함수를 커스텀 함수로 교체
        import builtins
        builtins.print = custom_print
        
        try:
            # 모듈 로드 (import 실행)
            spec.loader.exec_module(script_module)
            
            # 스크립트의 메인 함수 찾아서 실행
            # 대부분의 스크립트가 add_spam_number, add_spam_words 등의 함수를 가지고 있음
            main_function = None
            
            # 가능한 메인 함수 이름들
            possible_names = ['add_spam_number', 'add_spam_words', 'main', 'run']
            
            for name in possible_names:
                if hasattr(script_module, name):
                    main_function = getattr(script_module, name)
                    break
            
            if main_function and callable(main_function):
                if log_callback:
                    log_callback(f"📞 메인 함수 '{main_function.__name__}' 실행 중...")
                main_function()
            else:
                # 메인 함수를 못 찾으면 __main__ 블록 실행을 시도
                if log_callback:
                    log_callback("⚠️ 메인 함수를 찾을 수 없습니다. 스크립트 전체를 실행합니다.")
                
                # __name__을 '__main__'으로 설정하고 다시 실행
                script_module.__name__ = '__main__'
                code = compile(open(script_path, encoding='utf-8').read(), script_path, 'exec')
                exec(code, script_module.__dict__)
            
            if log_callback and not script_should_stop:
                log_callback("🎉 스크립트가 성공적으로 완료되었습니다!")
            
        finally:
            # 원래 print 함수로 복원
            builtins.print = original_print
            
    except Exception as e:
        if log_callback:
            log_callback(f"❌ 스크립트 실행 오류: {e}")
            import traceback
            log_callback(traceback.format_exc())

def execute_script(script_filename, device_name, platform_version, start_num=1, end_num=600, log_callback=None, finish_callback=None):
    """스크립트를 별도 프로세스 또는 스레드로 실행"""
    global running_process, running_thread, script_should_stop
    
    script_should_stop = False
    
    def run_in_thread():
        global running_process, script_should_stop
        
        try:
            script_path = os.path.join("scripts", script_filename)
            
            # 환경변수로 디바이스 정보 전달
            os.environ['APPIUM_DEVICE_NAME'] = device_name
            os.environ['APPIUM_PLATFORM_VERSION'] = platform_version
            os.environ['START_NUM'] = str(start_num)
            os.environ['END_NUM'] = str(end_num)
            
            if log_callback:
                log_callback(f"🚀 스크립트 시작: {script_filename}")
            
            # EXE 패키징 환경에서는 스크립트를 직접 실행
            if getattr(sys, 'frozen', False):
                if log_callback:
                    log_callback("📦 EXE 환경에서 스크립트를 직접 실행합니다.")
                
                # 원래의 print 함수를 저장
                original_print = print
                
                # 커스텀 print 함수 - GUI로 로그 전달
                def custom_print(*args, **kwargs):
                    msg = ' '.join(str(arg) for arg in args)
                    if log_callback:
                        log_callback(msg)
                    original_print(*args, **kwargs)
                
                # print 함수를 커스텀 함수로 교체
                import builtins
                builtins.print = custom_print
                
                try:
                    # 스크립트 파일을 직접 실행
                    with open(script_path, 'r', encoding='utf-8') as f:
                        script_code = f.read()
                    
                    # 실행 컨텍스트 생성
                    script_globals = {
                        '__name__': '__main__',
                        '__file__': script_path,
                        'script_should_stop': lambda: script_should_stop,  # 중지 플래그 체크 함수
                    }
                    
                    # 스크립트 실행
                    exec(compile(script_code, script_path, 'exec'), script_globals)
                    
                    if log_callback:
                        if script_should_stop:
                            log_callback("⏹️ 스크립트가 사용자에 의해 중지되었습니다.")
                        else:
                            log_callback("🎉 스크립트가 성공적으로 완료되었습니다!")
                    
                except SystemExit:
                    # 스크립트에서 sys.exit() 호출 시
                    if log_callback:
                        if script_should_stop:
                            log_callback("⏹️ 스크립트가 사용자에 의해 중지되었습니다.")
                        else:
                            log_callback("✅ 스크립트가 종료되었습니다.")
                
                except KeyboardInterrupt:
                    # Ctrl+C 또는 중단
                    if log_callback:
                        log_callback("⏹️ 스크립트가 중단되었습니다.")
                
                except Exception as e:
                    if log_callback:
                        log_callback(f"❌ 스크립트 실행 오류: {e}")
                        import traceback
                        log_callback(traceback.format_exc())
                
                finally:
                    # 원래 print 함수로 복원
                    builtins.print = original_print
                
            else:
                # 일반 Python 환경에서는 subprocess 사용
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
                    creationflags=creation_flags
                )
                
                # 실시간 로그 출력
                while True:
                    if running_process.poll() is not None:
                        remaining_output = running_process.stdout.read()
                        if remaining_output and log_callback:
                            for line in remaining_output.strip().split('\n'):
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
    
    # 이미 실행 중인 스크립트가 있으면 중지
    if running_process and running_process.poll() is None:
        if log_callback:
            log_callback("⚠️ 이전 스크립트를 중지하고 새 스크립트를 시작합니다.")
        stop_running_script()
    
    # 별도 스레드에서 실행
    running_thread = threading.Thread(target=run_in_thread)
    running_thread.daemon = True
    running_thread.start()
    
    return running_thread

def is_script_running():
    """스크립트가 실행 중인지 확인"""
    global running_process, running_thread
    
    # subprocess로 실행 중인 경우
    if running_process is not None and running_process.poll() is None:
        return True
    
    # 스레드로 실행 중인 경우
    if running_thread is not None and running_thread.is_alive():
        return True
    
    return False