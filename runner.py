import subprocess
import threading
import os
import sys
from pathlib import Path

# 스크립트 파일명과 GUI에 표시할 이름 매핑
SCRIPT_MAPPING = {
    "ixiO_add_spamList.py": "익시오 - 스팸 번호 추가",
    "mobileManager_add_spam_number.py": "모바일매니저 - 스팸 번호 추가", 
    "spamcallnoti_add_spam_number.py": "스팸전화알림 - 스팸 번호 추가",
    "mobileManager_add_spam_words.py": "모바일매니저 - 스팸 단어 추가"
}

def get_available_scripts():
    #"""사용 가능한 스크립트들을 찾아서 반환"""
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
   #"""디바이스 속성 값 가져오기"""
    try:
        result = subprocess.run(['adb', '-s', device_id, 'shell', 'getprop', prop_name],
                              capture_output=True, text=True, timeout=5)
        return result.stdout.strip() if result.returncode == 0 else "Unknown"
    except:
        return "Unknown"

def check_adb_connection():
    #"""ADB 디바이스 연결 확인 및 정보 수집"""
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

def execute_script(script_filename, device_name, platform_version, log_callback=None, finish_callback=None):
    # """스크립트를 별도 프로세스로 실행"""
    def run_in_thread():
        process = None
        try:
            script_path = os.path.join("scripts", script_filename)
            
            # 환경변수로 디바이스 정보 전달
            env = os.environ.copy()
            env['APPIUM_DEVICE_NAME'] = device_name
            env['APPIUM_PLATFORM_VERSION'] = platform_version
            
            # Python 스크립트 실행
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env
            )
            
            # 실시간 로그 출력
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output and log_callback:
                    log_callback(output.strip())
            
            # 프로세스 완료 대기
            return_code = process.wait()
            
            if log_callback:
                if return_code == 0:
                    log_callback("🎉 스크립트가 성공적으로 완료되었습니다!")
                else:
                    log_callback(f"❌ 스크립트가 오류로 종료되었습니다. (종료 코드: {return_code})")
            
        except Exception as e:
            if log_callback:
                log_callback(f"❌ 스크립트 실행 오류: {e}")
        
        finally:
            if finish_callback:
                finish_callback()
    
    # 별도 스레드에서 실행
    thread = threading.Thread(target=run_in_thread)
    thread.daemon = True
    thread.start()
    
    return thread