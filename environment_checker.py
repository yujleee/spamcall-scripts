"""
Appium 실행환경 체크 및 설정
포터블 환경이 필요한지 판단하고 필요시 설치
"""

import subprocess
import os
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext  
from utils.font import get_log_font

tk_font = get_log_font()
log_widget = None   # GUI 로그 창(Text 위젯) 참조용

def set_log_widget(widget):
    """GUI 로그 출력용 Text 위젯을 safe_print에 등록"""
    global log_widget
    log_widget = widget

def safe_print(text):
    """안전한 출력 함수"""
    try:
        print(text)
    except UnicodeEncodeError:
        try:
            safe_text = str(text).encode('cp949', errors='replace').decode('cp949')
            print(safe_text)
            text = safe_text
        except:
            print("[출력 오류: 특수문자 포함]")
            text = "[출력 오류: 특수문자 포함]"

    if log_widget is not None:
        log_widget.insert(tk.END, str(text) + "\n")
        log_widget.see(tk.END)  # 자동 스크롤

def check_command_available(command, version_flag='--version', timeout=5):
    """명령어가 사용 가능한지 확인 (윈도우 호환)"""
    
    # 윈도우에서 시도할 명령어들 (확장자 포함)
    commands_to_try = [command]
    
    if sys.platform == 'win32':
        commands_to_try.extend([
            f"{command}.exe",
            f"{command}.cmd", 
            f"{command}.bat"
        ])
    
    for cmd in commands_to_try:
        try:
            # 윈도우에서는 shell=True가 필요한 경우가 많음
            result = subprocess.run(
                [cmd, version_flag], 
                capture_output=True, 
                timeout=timeout,
                text=True, 
                encoding='utf-8', 
                errors='replace',
                shell=sys.platform == 'win32'  # 윈도우에서만 shell=True
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

def check_system_environment():
    """시스템 실행환경 확인"""
    safe_print("🔍 시스템 실행환경 확인 중...")
    
    # Node.js 확인
    node_available, node_version = check_command_available('node', '--version')
    if node_available:
        safe_print(f"✅ Node.js: {node_version}")
    
    # Appium 확인 (여러 방법으로 시도)
    appium_available = False
    appium_version = None
    
    # 방법 1: appium --version
    appium_available, appium_version = check_command_available('appium', '--version')
    
    # 방법 2: npm list -g appium (글로벌 설치 확인)
    if not appium_available:
        npm_available, npm_output = check_command_available('npm', 'list -g appium --depth=0')
        if npm_available and 'appium@' in npm_output:
            appium_available = True
            appium_version = "(npm global)"
    
    if appium_available:
        safe_print(f"✅ Appium: {appium_version}")
    
    # ADB 확인
    adb_available, adb_version = check_command_available('adb', 'version')
    if adb_available:
        adb_version_line = adb_version.split('\n')[0] if adb_version else 'Unknown'
        safe_print(f"✅ ADB: {adb_version_line}")
    
    # 결과 정리
    tools_status = {
        'node': node_available,
        'appium': appium_available,
        'adb': adb_available
    }
    
    available_tools = [tool for tool, available in tools_status.items() if available]
    missing_tools = [tool for tool, available in tools_status.items() if not available]
    
    return tools_status, available_tools, missing_tools

def check_portable_runtime():
    """포터블 런타임 환경 확인"""
    try:
        from setup_runtime import check_runtime_exists
        return check_runtime_exists()
    except ImportError:
        return False
    except Exception as e:
        safe_print(f"⚠️ 포터블 환경 확인 중 오류: {e}")
        return False

def ask_user_choice(missing_tools):
    """사용자에게 환경 설정 방법 선택 요청"""
    
    if not missing_tools:
        # 모든 도구가 있는 경우 - 그냥 진행
        safe_print("🎉 모든 필수 도구가 설치되어 있습니다!")
        return 'system'
    
    # 일부 도구가 누락된 경우만 사용자에게 묻기
    root = tk.Tk()
    root.title("실행환경 설정")
    root.geometry("400x250")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')
    
    choice = {"value": None}
    
    def setup_ui():
        main_frame = tk.Frame(root, padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목
        title_label = tk.Label(
            main_frame,
            text="⚠️ 일부 도구가 누락됨",
            font=tk_font,
            fg='orange'
        )
        title_label.pack(pady=(0, 15))

        log_area = scrolledtext.ScrolledText(
        main_frame,
        width=50,
        height=10,
        font=tk_font
    )
        log_area.pack(pady=(0, 15), fill=tk.BOTH, expand=True)

        # safe_print가 log_area도 쓰도록 연결
        set_log_widget(log_area)
        
        # 누락된 도구 표시
        missing_text = f"누락된 도구: {', '.join(missing_tools)}"
        missing_label = tk.Label(
            main_frame,
            text=missing_text,
            font=tk_font,
            fg='red'
        )
        missing_label.pack(pady=(0, 20))
        
        # 버튼들
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        # 포터블 설치 (권장)
        portable_btn = tk.Button(
            btn_frame,
            text="🚀 포터블 환경 설치 (권장)",
            font=tk_font,
            width=25,
            height=2,
            bg='#4CAF50',
            fg='white',
            command=lambda: set_choice('portable')
        )
        portable_btn.pack(pady=5)
        
        # 그냥 진행
        continue_btn = tk.Button(
            btn_frame,
            text="⚠️ 그냥 진행 (일부 기능 제한)",
            font=tk_font,
            width=25,
            height=10,
            bg='#FF9800',
            fg='white',
            command=lambda: set_choice('system')
        )
        continue_btn.pack(pady=5)
        
        # 취소
        cancel_btn = tk.Button(
            btn_frame,
            text="❌ 취소",
            font=tk_font,
            width=25,
            height=10,
            command=lambda: set_choice('cancel')
        )
        cancel_btn.pack(pady=(10, 0))
    
    def set_choice(value):
        choice["value"] = value
        root.destroy()
    
    setup_ui()
    root.mainloop()
    
    return choice["value"]

def install_portable_environment():
    """포터블 환경 설치"""
    try:
        # 간단한 설치 진행 다이얼로그
        from tkinter import ttk
        
        progress_root = tk.Tk()
        progress_root.title("포터블 환경 설치 중...")
        progress_root.geometry("400x150")
        progress_root.resizable(False, False)
        progress_root.eval('tk::PlaceWindow . center')
        
        main_frame = tk.Frame(progress_root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        status_label = tk.Label(
            main_frame,
            text="포터블 환경을 설치하고 있습니다...",
            font=tk_font        )
        status_label.pack(pady=(0, 15))
        
        progress = ttk.Progressbar(main_frame, mode='indeterminate', length=300)
        progress.pack(pady=(0, 15))
        progress.start(10)
        
        detail_label = tk.Label(
            main_frame,
            text="잠시만 기다려주세요...",
            font=tk_font,
            fg='gray'
        )
        detail_label.pack()
        
        progress_root.update()
        
        # 실제 설치 실행
        from setup_runtime import install_runtime
        success = install_runtime()
        
        progress.stop()
        progress_root.destroy()
        
        if success:
            messagebox.showinfo("설치 완료", "포터블 환경 설치가 완료되었습니다!")
            return True
        else:
            messagebox.showerror("설치 실패", "포터블 환경 설치에 실패했습니다.")
            return False
            
    except Exception as e:
        safe_print(f"설치 중 오류: {e}")
        messagebox.showerror("오류", f"설치 중 오류가 발생했습니다: {e}")
        return False

def check_environment_and_setup():
    """환경 체크 및 필요시 설정 - 메인 함수"""
    
    # 1. 포터블 환경이 이미 있는지 확인
    if check_portable_runtime():
        safe_print("✅ 포터블 환경이 이미 설치되어 있습니다.")
        # 포터블 환경 경로 설정
        try:
            from setup_runtime import get_portable_executable_paths
            from pathlib import Path
            exe_paths = get_portable_executable_paths()
            if exe_paths:
                node_dir = Path(exe_paths['node']).parent
                adb_dir = Path(exe_paths['adb']).parent
                current_path = os.environ.get('PATH', '')
                os.environ['PATH'] = f"{node_dir}{os.pathsep}{adb_dir}{os.pathsep}{current_path}"
                safe_print("📁 포터블 환경 경로가 설정되었습니다.")
        except Exception as e:
            safe_print(f"⚠️ 포터블 환경 경로 설정 실패: {e}")
        
        return True
    
    # 2. 시스템 환경 확인
    tools_status, available_tools, missing_tools = check_system_environment()
    
    if not missing_tools:
        # 모든 도구가 있으면 그냥 진행
        return True
    
    # 3. 일부 도구가 누락된 경우 사용자에게 선택 요청
    safe_print(f"⚠️ 누락된 도구: {', '.join(missing_tools)}")
    
    choice = ask_user_choice(missing_tools)
    
    if choice == 'cancel':
        safe_print("사용자가 취소했습니다.")
        return False
    
    elif choice == 'portable':
        safe_print("🚀 포터블 환경을 설치합니다...")
        return install_portable_environment()
    
    elif choice == 'system':
        safe_print("⚠️ 누락된 도구가 있지만 계속 진행합니다.")
        safe_print("💡 일부 기능이 제한될 수 있습니다.")
        return True
    
    else:
        safe_print("❌ 잘못된 선택입니다.")
        return False

# 단독 실행용 (테스트)
if __name__ == "__main__":
    result = check_environment_and_setup()
    safe_print(f"결과: {'성공' if result else '실패'}")