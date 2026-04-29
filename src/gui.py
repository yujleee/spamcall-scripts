import os
import queue
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from src.runner import get_available_scripts, check_adb_connection, execute_script, stop_running_script, auto_open_appium_terminal
from utils.font import get_log_font

os.environ['PYTHONIOENCODING'] = 'utf-8'

def create_gui():
    """GUI 생성 및 실행"""
    root = tk.Tk()
    root.title("Appium Script Runner")
    try:
        root.iconbitmap('./img/icon.ico')
    except Exception:
        pass
    root.geometry("900x750")


    # 상태 변수들
    device_info = {}
    current_thread = None
    available_scripts = get_available_scripts()
    tk_font = get_log_font()
    _log_queue = queue.Queue()

    def _process_log_queue():
        """메인 스레드에서 큐에 쌓인 로그를 처리"""
        while True:
            try:
                message = _log_queue.get_nowait()
                log_text.config(state='normal')
                log_text.insert(tk.END, f"{message}\n")
                log_text.see(tk.END)
                log_text.config(state='disabled')
            except queue.Empty:
                break
        root.after(50, _process_log_queue)

    def log_message(message):
        """로그 메시지를 큐에 추가 (스레드 안전)"""
        _log_queue.put(message)
    
    def on_check_connection():
        """ADB 연결 확인 버튼 핸들러"""
        nonlocal device_info
        
        log_message("🔍 ADB 연결 확인 중...")
        
        device_info = check_adb_connection()
        
        if not device_info:
            device_label.config(text="연결된 디바이스: ❌ 없음", foreground="red")
            info_text.config(state='normal', font=tk_font)
            info_text.delete(1.0, tk.END)
            info_text.insert(1.0, "연결된 디바이스가 없습니다.\n\n확인사항:\n1. USB 디버깅이 활성화되어 있는지\n2. ADB 드라이버가 설치되어 있는지\n3. 디바이스가 올바르게 연결되어 있는지")
            info_text.config(state='disabled')
            run_button.config(state='disabled')
            log_message("❌ 연결된 디바이스를 찾을 수 없습니다.")
            return
        
        # UI 업데이트
        device_label.config(text=f"✅ 연결된 디바이스: {device_info['deviceName']}", foreground="green", font=tk_font)
        
        info_content = f"📱 모델: {device_info['model']}\n🤖 안드로이드 버전: {device_info['platformVersion']}\n🔗 디바이스 ID: {device_info['deviceName']}"
        info_text.config(state='normal', font=tk_font)
        info_text.delete(1.0, tk.END)
        info_text.insert(1.0, info_content)
        info_text.config(state='disabled')
        
        # 스크립트 실행 버튼 활성화
        if available_scripts:
            run_button.config(state='normal')
        
        log_message(f"✅ 디바이스 연결 완료: {device_info['deviceName']}")
        log_message(f"   📱 {device_info['model']} (Android {device_info['platformVersion']})")
    
    def on_run_script():
        """스크립트 실행 버튼 핸들러"""
        nonlocal current_thread

        # 입력값 검증
        try:
            start_num = int(start_num_var.get())
            end_num = int(end_num_var.get())
            word_count = int(word_count_var.get())
            
            if start_num > end_num:
                messagebox.showwarning("⚠️ 경고", "시작 번호가 마지막 번호보다 큽니다.")
                return
            if start_num <= 0 or end_num <= 0:
                messagebox.showwarning("⚠️ 경고", "1 이상의 숫자를 입력해주세요.")
                return
            if word_count <= 0:
                messagebox.showwarning("⚠️ 경고", "추가할 단어 갯수는 1 이상의 숫자를 입력해주세요.")
                return
            if word_count > 300:
                messagebox.showwarning("⚠️ 경고", "추가할 단어 갯수는 최대 300개까지 가능합니다.")
                return
        except ValueError:
            messagebox.showwarning("⚠️ 경고", "올바른 숫자를 입력해주세요.")
            return
            
        selected_display_name = script_var.get()
        if not selected_display_name:
            messagebox.showwarning("⚠️ 경고", "실행할 스크립트를 선택해주세요.")
            return
        
        if not device_info:
            messagebox.showwarning("⚠️ 경고", "먼저 디바이스 연결을 확인해주세요.")
            return
        
        # 표시명으로 실제 파일명 찾기
        script_filename = available_scripts.get(selected_display_name)
        if not script_filename:
            messagebox.showerror("⛔️ 오류", "선택된 스크립트 파일을 찾을 수 없습니다.")
            return
        
        script_path = os.path.join("scripts", script_filename)
        if not os.path.exists(script_path):
            messagebox.showerror("⛔️ 오류", f"스크립트 파일이 존재하지 않습니다: {script_path}")
            return
        
        # 로그 클리어 및 UI 상태 변경
        log_text.config(state='normal')
        log_text.delete(1.0, tk.END)
        log_text.config(state='disabled')
        
        run_button.config(state='disabled')
        stop_button.config(state='normal')
        script_combo.config(state='disabled')
        
        log_message("=" * 60)
        log_message(f"🚀 스크립트 실행 시작: {selected_display_name}")
        log_message(f"📁 파일: {script_filename}")
        log_message(f"📱 디바이스: {device_info['deviceName']}")
        log_message(f"🤖 안드로이드 버전: {device_info['platformVersion']}")
        log_message("=" * 60)
        
        # 스크립트 실행
        def on_finish():
            def _on_finish_ui():
                run_button.config(state='normal')
                stop_button.config(state='disabled')
                script_combo.config(state='readonly')
                log_message("=" * 60)
            root.after(0, _on_finish_ui)
        
        current_thread = execute_script(
            script_filename,
            device_info['deviceName'], 
            device_info['platformVersion'],
            start_num=start_num,
            end_num=end_num,
            word_count=word_count,
            log_callback=log_message,
            finish_callback=on_finish
        )
    
    def on_stop_script():
        """스크립트 중지 버튼 핸들러"""
        # subprocess 중지는 runner.py에서 처리하도록 개선 필요
        log_message("⏹️ 스크립트 중지 요청...")
        stop_running_script()
        messagebox.showinfo("⚠️ 알림", "스크립트가 중지 되었습니다.")
        run_button.config(state='normal')
        stop_button.config(state='disabled')
        script_combo.config(state='readonly')
    
    def refresh_scripts():
        """스크립트 목록 새로고침"""
        nonlocal available_scripts
        available_scripts = get_available_scripts()
        script_combo['values'] = list(available_scripts.keys())
        
        if available_scripts:
            log_message(f"📝 발견된 스크립트: {len(available_scripts)}개")
            for display_name, filename in available_scripts.items():
                log_message(f"   • {display_name} ({filename})")
        else:
            log_message("⚠️ scripts 폴더에서 등록된 스크립트를 찾을 수 없습니다.")
            log_message("   SCRIPT_MAPPING에 스크립트를 추가해주세요.")
    

    # ===== UI 구성 =====
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # 1. ADB 연결 섹션
    adb_frame = ttk.LabelFrame(main_frame, text="📱 ADB 연결", padding="10")
    adb_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
    
    connection_frame = ttk.Frame(adb_frame)
    connection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
    ttk.Button(connection_frame, text="디바이스 연결", 
              command=on_check_connection).grid(row=0, column=0, padx=(0, 10))
    
    device_label = ttk.Label(connection_frame, text="연결된 디바이스: 없음", foreground="red")
    device_label.grid(row=0, column=1, sticky=tk.W)
    
    info_text = tk.Text(adb_frame, height=3, width=70, state='disabled', 
                        font= tk_font, bg='#f8f8f8')
    info_text.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
    
    # 2. 스크립트 선택 섹션
    script_frame = ttk.LabelFrame(main_frame, text="📜 스크립트 선택", padding="10")
    script_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
    
    selection_frame = ttk.Frame(script_frame)
    selection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
    ttk.Label(selection_frame, text="실행할 스크립트").grid(row=0, column=0, sticky=tk.W)
    
    script_var = tk.StringVar()
    script_combo = ttk.Combobox(selection_frame, textvariable=script_var, 
                                values=list(available_scripts.keys()), 
                                state="readonly", width=50)
    script_combo.grid(row=0, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
    
    ttk.Button(selection_frame, text="새로고침", 
              command=refresh_scripts).grid(row=0, column=2, padx=(5, 0))

    range_frame = ttk.LabelFrame(main_frame, text="🔢 번호 및 단어 추가 범위 설정 (1~999)", padding="10")
    range_frame.grid(row=2, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(0, 10))

    ttk.Label(range_frame, text="시작 번호:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
    start_num_var = tk.StringVar(value="1")
    start_entry = ttk.Entry(range_frame, textvariable=start_num_var, width=8)
    start_entry.grid(row=0, column=1, padx=(0, 20))

    ttk.Label(range_frame, text="마지막 번호:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
    end_num_var = tk.StringVar(value="600")
    end_entry = ttk.Entry(range_frame, textvariable=end_num_var, width=8)
    end_entry.grid(row=0, column=3,  padx=(0, 20))

    ttk.Label(range_frame, text="추가할 단어 갯수:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
    word_count_var = tk.StringVar(value="200")  
    word_count_entry = ttk.Entry(range_frame, textvariable=word_count_var, width=8) 
    word_count_entry.grid(row=0, column=5)
    
    # 3. 실행 버튼들
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 2))
    
    run_button = ttk.Button(button_frame, text="🚀 스크립트 실행", 
                            command=on_run_script, state='disabled')
    run_button.grid(row=0, column=0, padx=(0, 10))
    
    stop_button = ttk.Button(button_frame, text="⏹️ 실행 중지", 
                             command=on_stop_script, state='disabled')
    stop_button.grid(row=0, column=1)
    
    # 4. 로그 출력 섹션
    log_frame = ttk.LabelFrame(main_frame, text="📋 진행 로그", padding="20")
    log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    log_text = scrolledtext.ScrolledText(log_frame, height=20, state='disabled',
                                        font= tk_font, bg="#2c2c2c", fg="#F1F1F1",
                                        insertbackground='#ffffff')
    log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # 그리드 가중치 설정
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(3, weight=1)
    log_frame.columnconfigure(0, weight=1)
    log_frame.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    selection_frame.columnconfigure(1, weight=1)
    connection_frame.columnconfigure(1, weight=1)
    
    # 초기화
    log_message("🚀 Appium Script Runner v1.0 (AOS only)")
    log_message(f"   • 스팸 전화번호 및 차단 단어 자동 추가 프로그램")
    log_message(f"   • 최대 등록 한도 팝업 확인용 (스크립트별 일정 시간 소요)")  
    log_message(f"   • 실행 전 APPIUM 환경 설정이 필요합니다.")  
    log_message("=" * 60)
    log_message("📋 사용방법:")
    log_message(f"   1. 디바이스 연결 확인")
    log_message(f"   2. 스크립트 선택")
    log_message(f"      ❗ 스크립트 실행 전, 연결한 단말에서 해당 앱에서 실행할 기능 화면으로 진입해주세요.")
    log_message(f"      예) 익시오 스팸번호 추가 - 설정 > 스팸 알림 및 수신 차단 > 전화 차단 진입") 
    log_message(f"   3. 스크립트 실행")
    log_message("=" * 60)
    
    refresh_scripts()

    root.after(50, _process_log_queue)
    root.after(1000, auto_open_appium_terminal)

    root.mainloop()
        