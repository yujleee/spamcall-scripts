"""
Appium 실행환경 체크
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

def show_environment_check_result(check_result, parent=None):
    """환경 체크 결과를 GUI 팝업으로 표시"""
    if parent is None:
        root = tk.Tk()
        root.withdraw()
        parent = root
        should_destroy_parent = True
    else:
        should_destroy_parent = False
    
    result_window = tk.Toplevel(parent)
    result_window.title("시스템 환경 체크 결과")
    result_window.geometry("500x400")
    result_window.resizable(False, False)
    result_window.transient(parent)  # 부모 창 위에 항상 표시
    result_window.grab_set()  # 모달 대화상자로 설정
    
    frame = tk.Frame(result_window, padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)
    
    # 제목
    title = tk.Label(frame, text="🔍 시스템 환경 체크 결과", font=(tk_font[0], 12, 'bold'))
    title.pack(pady=(0, 15))
    
    # 결과 표시 영역
    result_text = scrolledtext.ScrolledText(
        frame,
        width=50,
        height=15,
        font=tk_font,
        bg='#f8f8f8'
    )
    result_text.pack(pady=(0, 15))
    
    # 결과 출력
    def add_line(text, color='black'):
        result_text.insert(tk.END, text + '\n', color)
        
    # 태그 설정
    result_text.tag_configure('success', foreground='green')
    result_text.tag_configure('error', foreground='red')
    result_text.tag_configure('warning', foreground='orange')
    
    add_line("🔍 시스템 실행환경 확인 결과:")
    
    # Node.js 상태
    node_info = check_result.get('node', {})
    if node_info.get('available'):
        add_line(f"✅ Node.js: {node_info.get('version', 'Unknown')}", 'success')
    else:
        add_line("❌ Node.js: 설치되지 않음", 'error')
    
    # Appium 상태
    appium_info = check_result.get('appium', {})
    if appium_info.get('available'):
        add_line(f"✅ Appium: {appium_info.get('version', 'Unknown')}", 'success')
    else:
        add_line("❌ Appium: 설치되지 않음", 'error')
    
    # ADB 상태
    adb_info = check_result.get('adb', {})
    if adb_info.get('available'):
        add_line(f"✅ ADB: {adb_info.get('version', 'Unknown')}", 'success')
    else:
        add_line("❌ ADB: 설치되지 않음", 'error')
    
    result_text.configure(state='disabled')
    
    # 확인 버튼
    tk.Button(
        frame,
        text="확인",
        font=tk_font,
        command=result_window.destroy,
        width=20
    ).pack(pady=(10, 0))
    
    # 창이 닫힐 때까지 대기
    result_window.wait_window(result_window)
    
    # parent가 None이었던 경우에만 destroy
    if should_destroy_parent and hasattr(parent, 'destroy'):
        parent.destroy()

def check_system_environment(get_versions=False):
    """시스템 실행환경 확인"""
    # GUI 모드에서는 safe_print 사용 안 함
    if not hasattr(check_system_environment, 'gui_mode'):
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
    
    if get_versions:
        return {
            'node': {'available': node_available, 'version': node_version},
            'appium': {'available': appium_available, 'version': appium_version},
            'adb': {'available': adb_available, 'version': adb_version.split('\n')[0] if adb_version else None}
        }
    
    available_tools = [tool for tool, available in tools_status.items() if available]
    missing_tools = [tool for tool, available in tools_status.items() if not available]
    
    return tools_status, available_tools, missing_tools

def show_missing_tools_dialog(missing_tools):
    """누락된 도구를 표시하고 프로그램 종료"""
    
    # 도구 설명
    tool_descriptions = {
        'node': 'JavaScript 런타임 환경',
        'appium': '모바일 앱 자동화 프레임워크. node.js 선행 설치 필요.',
        'adb': 'Android Debug Bridge'
    }
    
    root = tk.Tk()
    root.title("실행환경 설정")
    root.geometry("450x400")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')
    
    main_frame = tk.Frame(root, padx=30, pady=30)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 제목
    title_label = tk.Label(
        main_frame,
        text="⚠️ 일부 도구가 누락됨",
        font=(tk_font[0], 14, 'bold'),
        fg='#FF9800'
    )
    title_label.pack(pady=(0, 15))

    # 누락된 도구 상세 정보 표시 영역
    details_frame = tk.LabelFrame(
        main_frame,
        text="누락된 도구 목록",
        font=tk_font,
        padx=10,
        pady=10
    )
    details_frame.pack(pady=(0, 15), fill=tk.BOTH, expand=True)
    
    details_text = scrolledtext.ScrolledText(
        details_frame,
        width=45,
        height=2,
        font=tk_font,
        bg='#fff5f5',
        wrap=tk.WORD
    )
    details_text.pack(fill=tk.BOTH, expand=True)
    
    # 누락된 도구 정보 추가
    for tool in missing_tools:
        details_text.insert(tk.END, f"❌ {tool.upper()}\n", 'tool_name')
        details_text.insert(tk.END, f"   상태: 설치되지 않음\n", 'status')
        if tool in tool_descriptions:
            details_text.insert(tk.END, f"   설명: {tool_descriptions[tool]}\n", 'desc')
        details_text.insert(tk.END, "\n")
    
    # 태그 설정
    details_text.tag_configure('tool_name', foreground='red', font=(tk_font[0], tk_font[1], 'bold'))
    details_text.tag_configure('status', foreground='#666666')
    details_text.tag_configure('desc', foreground='#888888')
    
    details_text.configure(state='disabled')
    
    # 안내 메시지
    info_label = tk.Label(
        main_frame,
        text="위 도구들을 시스템에 설치한 후\n다시 실행해주세요.",
        font=tk_font,
        fg='#555555',
        justify=tk.CENTER
    )
    info_label.pack(pady=(10, 20))
    
    # 프로그램 종료 버튼
    exit_btn = tk.Button(
        main_frame,
        text="🚪 프로그램 종료",
        font=tk_font,
        width=30,
        height=2,
        bg='#f44336',
        fg='white',
        relief='flat',
        borderwidth=0,
        command=root.quit
    )
    exit_btn.pack(pady=(5, 0))
    
    root.mainloop()
    root.destroy()
    
    # 종료
    safe_print("프로그램을 종료합니다.")
    sys.exit(0)

def check_environment_and_setup(get_check_result=False):
    """환경 체크 및 필요시 설정 - 메인 함수"""
    
    # 체크 결과 저장용 딕셔너리
    check_result = {
        'node': {'available': False, 'version': None},
        'appium': {'available': False, 'version': None},
        'adb': {'available': False, 'version': None},
        'all_available': False  # 모든 도구 사용 가능 여부 플래그 추가
    }
    
    # 시스템 환경 확인
    tools_info = check_system_environment(get_versions=True)
    check_result.update(tools_info)
    tools_status, available_tools, missing_tools = check_system_environment()
    
    if not missing_tools:
        # 모든 도구가 있으면 그냥 진행
        safe_print("🎉 모든 필수 도구가 설치되어 있습니다!")
        check_result['all_available'] = True
        if get_check_result:
            return True, check_result
        return True
    
    # 일부 도구가 누락된 경우
    safe_print(f"⚠️ 누락된 도구: {', '.join(missing_tools)}")
    check_result['all_available'] = False
    
    # GUI로 누락된 도구 표시 후 프로그램 종료
    show_missing_tools_dialog(missing_tools)
    
    # 여기까지 오지 않음 (show_missing_tools_dialog에서 sys.exit 호출)
    if get_check_result:
        return False, check_result
    return False

# 단독 실행용 (테스트)
if __name__ == "__main__":
    result = check_environment_and_setup()
    safe_print(f"결과: {'성공' if result else '실패'}")