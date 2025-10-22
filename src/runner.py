import subprocess
import threading
import platform
import os
import sys
from pathlib import Path

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
    global running_process, running_thread
    
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
    
    return False

def execute_script(script_filename, device_name, platform_version, start_num=1, end_num=600, log_callback=None, finish_callback=None):
    """스크립트를 별도 프로세스로 실행"""
    global running_process, running_thread
    
    def run_in_thread():
        global running_process
        
        try:
            script_path = os.path.join("scripts", script_filename)
            
            # 환경변수로 디바이스 정보 전달
            env = os.environ.copy()
            env['APPIUM_DEVICE_NAME'] = device_name
            env['APPIUM_PLATFORM_VERSION'] = platform_version
            env['PYTHONUNBUFFERED'] = '1'  # Python 출력 버퍼링 비활성화
            env['START_NUM'] = str(start_num)
            env['END_NUM'] = str(end_num)
            
            if log_callback:
                log_callback(f"🚀 스크립트 시작: {script_filename}")
            
            # Python 스크립트 실행 (실시간 출력을 위한 설정)
            running_process = subprocess.Popen(
                [sys.executable, '-u', script_path],  # -u 옵션으로 버퍼링 비활성화
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,  # 버퍼 크기를 0으로 설정
                encoding='utf-8',  # UTF-8 인코딩 명시
                errors='replace',
                universal_newlines=True,
                env=env
            )
            
            # 실시간 로그 출력
            while True:
                # 프로세스가 종료되었는지 체크
                if running_process.poll() is not None:
                    # 남은 출력이 있는지 확인
                    remaining_output = running_process.stdout.read()
                    if remaining_output and log_callback:
                        for line in remaining_output.strip().split('\n'):
                            if line.strip():
                                log_callback(line.strip())
                    break
                
                # 한 줄씩 읽기
                try:
                    output = running_process.stdout.readline()
                    if output and log_callback:
                        log_callback(output.strip())
                except Exception as e:
                    if log_callback:
                        log_callback(f"로그 읽기 오류: {e}")
                    break
            
            # 프로세스 완료 대기
            return_code = running_process.wait()
            
            if log_callback:
                if return_code == 0:
                    log_callback("🎉 스크립트가 성공적으로 완료되었습니다!")
                elif return_code == -15:  # SIGTERM (정상적인 중지)
                    log_callback("⏹️ 스크립트가 사용자에 의해 중지되었습니다.")
                else:
                    log_callback(f"❌ 스크립트가 오류로 종료되었습니다. (종료 코드: {return_code})")
            
        except Exception as e:
            if log_callback:
                log_callback(f"❌ 스크립트 실행 오류: {e}")
        
        finally:
            running_process = None
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
    global running_process
    return running_process is not None and running_process.poll() is None





