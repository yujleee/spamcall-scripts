"""메인 GUI 모듈"""
import os
import tkinter as tk
from tkinter import ttk
from main import get_resource_path
from src.runner import get_available_scripts, auto_open_appium_terminal
from src.setup_runtime import setup_runtime_if_needed, set_log_callback as set_runtime_log_callback
from src.environment_checker import (
    set_log_callback as set_checker_log_callback,
    check_system_environment,
    safe_print
)
from utils.font import get_log_font
from .components import (
    create_connection_frame,
    create_script_frame,
    create_button_frame,
    create_log_frame
)
from .handlers import (
    create_connection_handler,
    create_script_handler,
    create_stop_handler,
    create_refresh_handler
)
from .state import GUIState, create_log_callback

def create_gui():
    """GUI 생성 및 실행"""
    # 기본 윈도우 설정
    root = tk.Tk()
    root.title("Appium Script Runner")
    icon_path = get_resource_path('img/icon.ico')
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    root.geometry("900x650")
    
    # 초기 상태 설정
    state = GUIState(
        root=root,
        available_scripts=get_available_scripts()
    )
    tk_font = get_log_font()
    
    # 메인 프레임 설정
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # 컴포넌트 생성
    adb_frame, device_label, info_text = create_connection_frame(main_frame, None, tk_font)
    adb_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
    
    script_frame, script_var, script_combo = create_script_frame(main_frame, state.available_scripts, None)
    script_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
    
    button_frame, run_button, stop_button = create_button_frame(main_frame, None, None)
    button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
    
    log_frame, log_text = create_log_frame(main_frame, tk_font)
    log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # 상태 업데이트
    state.device_label = device_label
    state.info_text = info_text
    state.script_combo = script_combo
    state.run_button = run_button
    state.stop_button = stop_button
    state.log_text = log_text
    
    # 로그 콜백 설정
    log_message = create_log_callback(log_text, root)
    state.log_callback = log_message
    
    # 이벤트 핸들러 설정
    on_check_connection = create_connection_handler(
        state.device_info, device_label, info_text, run_button,
        state.available_scripts, log_message, tk_font
    )
    
    on_run_script = create_script_handler(
        script_var, state.device_info, state.available_scripts,
        log_text, run_button, stop_button, script_combo, log_message
    )
    
    on_stop_script = create_stop_handler(
        run_button, stop_button, script_combo, log_message
    )
    
    refresh_scripts = create_refresh_handler(
        state.available_scripts, script_combo, log_message
    )
    
    # 버튼 커맨드 설정
    adb_frame.children['!frame'].children['!button'].configure(command=on_check_connection)
    run_button.configure(command=on_run_script)
    stop_button.configure(command=on_stop_script)
    script_frame.children['!frame'].children['!button'].configure(command=refresh_scripts)
    
    # 그리드 가중치 설정
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(3, weight=1)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    # 초기화
    log_message("🚀 Appium Script Runner v1.0.0 (AOS only)")
    
    # 로그 콜백 연결
    set_checker_log_callback(log_message)
    set_runtime_log_callback(log_message)
    
    # 시스템 환경 체크
    tools_status, available_tools, missing_tools = check_system_environment()
    if not missing_tools:
        # 모든 도구가 있으면 포터블 환경 체크는 건너뜀
        safe_print("✅ 시스템에 모든 필수 도구가 설치되어 있습니다.")
    else:
        # 누락된 도구가 있을 때만 setup_runtime 실행
        if not setup_runtime_if_needed():
            return
    
    log_message("=" * 60)
    log_message(f"   • 스팸 전화번호 및 차단 단어 자동 추가 프로그램")
    log_message(f"   • 최대 등록 한도 팝업 확인용 (스크립트별 일정 시간 소요)")   
    log_message("=" * 60)
    log_message("📋 사용방법:")
    log_message(f"   1. 디바이스 연결 확인")
    log_message(f"   2. 스크립트 선택")
    log_message(f"      ❗ 스크립트 실행 전, 연결한 단말에서 해당 앱에서 실행할 기능 화면으로 진입해주세요.")
    log_message(f"      예) 익시오 스팸번호 추가 - 설정 > 스팸 알림 및 수신 차단 > 전화 차단 진입") 
    log_message(f"   3. 스크립트 실행")
    
    refresh_scripts()
    
    root.after(1000, auto_open_appium_terminal)

    root.mainloop()