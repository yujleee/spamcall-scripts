import os
import queue
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from src.device.adb import auto_open_appium_terminal, check_adb_connection
from src.device.ios import check_ios_connection
from src.runner.config import get_available_scripts
from src.runner.executor import execute_script, stop_running_script
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
    root.geometry("900x780")

    device_info = {}
    current_thread = None
    platform_var = tk.StringVar(value="android")
    available_scripts = get_available_scripts(platform_var.get())
    tk_font = get_log_font()
    _log_queue = queue.Queue()

    def _process_log_queue():
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
        _log_queue.put(message)

    def on_platform_change():
        """플랫폼 변경 시 연결 상태 초기화 및 스크립트 목록 갱신"""
        nonlocal device_info
        device_info = {}
        device_label.config(text="연결된 디바이스: 없음", foreground="red")
        info_text.config(state='normal', font=tk_font)
        info_text.delete(1.0, tk.END)
        info_text.config(state='disabled')
        run_button.config(state='disabled')
        _refresh_script_list()
        platform = platform_var.get()
        log_message(f"{'🤖 Android' if platform == 'android' else '🍎 iOS'} 모드로 전환됨")

    def on_check_connection():
        nonlocal device_info
        platform = platform_var.get()

        if platform == "ios":
            log_message("🔍 iOS 디바이스 연결 확인 중...")
            result = check_ios_connection()
        else:
            log_message("🔍 ADB 연결 확인 중...")
            result = check_adb_connection()

        if not result:
            device_label.config(text="연결된 디바이스: ❌ 없음", foreground="red")
            info_text.config(state='normal', font=tk_font)
            info_text.delete(1.0, tk.END)
            if platform == "ios":
                info_text.insert(
                    1.0,
                    "연결된 iOS 디바이스가 없습니다.\n\n확인사항:\n"
                    "1. 케이블 연결 후 iPhone에서 '신뢰' 선택\n"
                    "2. iPhone에서 개발자 모드 활성화 (iOS 16+)\n"
                    "3. libimobiledevice 설치 여부 확인 (brew install libimobiledevice)",
                )
            else:
                info_text.insert(
                    1.0,
                    "연결된 디바이스가 없습니다.\n\n확인사항:\n"
                    "1. USB 디버깅이 활성화되어 있는지\n"
                    "2. ADB 드라이버가 설치되어 있는지\n"
                    "3. 디바이스가 올바르게 연결되어 있는지",
                )
            info_text.config(state='disabled')
            run_button.config(state='disabled')
            log_message("❌ 연결된 디바이스를 찾을 수 없습니다.")
            device_info = {}
            return

        device_info = result
        platform_tag = "🍎 iOS" if platform == "ios" else "🤖 Android"
        device_label.config(
            text=f"✅ 연결된 디바이스: {device_info['deviceName']}",
            foreground="green",
            font=tk_font,
        )
        info_text.config(state='normal', font=tk_font)
        info_text.delete(1.0, tk.END)
        info_text.insert(
            1.0,
            f"📱 모델: {device_info['model']}\n"
            f"⚙️  OS: {platform_tag} {device_info['platformVersion']}\n"
            f"🔗 디바이스 ID: {device_info['deviceName']}",
        )
        info_text.config(state='disabled')

        if available_scripts:
            run_button.config(state='normal')

        log_message(f"✅ 디바이스 연결 완료: {device_info['deviceName']}")
        log_message(f"   📱 {device_info['model']} ({platform_tag} {device_info['platformVersion']})")

    def on_run_script():
        nonlocal current_thread

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

        script_filename = available_scripts.get(selected_display_name)
        if not script_filename:
            messagebox.showerror("⛔️ 오류", "선택된 스크립트 파일을 찾을 수 없습니다.")
            return

        script_path = os.path.join("scripts", script_filename)
        if not os.path.exists(script_path):
            messagebox.showerror("⛔️ 오류", f"스크립트 파일이 존재하지 않습니다: {script_path}")
            return

        log_text.config(state='normal')
        log_text.delete(1.0, tk.END)
        log_text.config(state='disabled')

        run_button.config(state='disabled')
        stop_button.config(state='normal')
        script_combo.config(state='disabled')

        platform = platform_var.get()
        platform_tag = "🍎 iOS" if platform == "ios" else "🤖 Android"
        log_message("=" * 60)
        log_message(f"🚀 스크립트 실행 시작: {selected_display_name}")
        log_message(f"📁 파일: {script_filename}")
        log_message(f"📱 디바이스: {device_info['deviceName']}")
        log_message(f"{platform_tag} OS 버전: {device_info['platformVersion']}")
        log_message("=" * 60)

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
            platform_name=platform,
            start_num=start_num,
            end_num=end_num,
            word_count=word_count,
            log_callback=log_message,
            finish_callback=on_finish,
        )

    def on_stop_script():
        log_message("⏹️ 스크립트 중지 요청...")
        stop_running_script()
        messagebox.showinfo("⚠️ 알림", "스크립트가 중지 되었습니다.")
        run_button.config(state='normal')
        stop_button.config(state='disabled')
        script_combo.config(state='readonly')

    def _refresh_script_list():
        nonlocal available_scripts
        available_scripts = get_available_scripts(platform_var.get())
        script_combo['values'] = list(available_scripts.keys())
        script_var.set('')

    def refresh_scripts():
        _refresh_script_list()
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

    # 1. 디바이스 연결 섹션
    adb_frame = ttk.LabelFrame(main_frame, text="📱 디바이스 연결", padding="10")
    adb_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

    # 플랫폼 선택 행
    platform_frame = ttk.Frame(adb_frame)
    platform_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 6))

    ttk.Label(platform_frame, text="플랫폼:").grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
    ttk.Radiobutton(
        platform_frame, text="🤖 Android", variable=platform_var,
        value="android", command=on_platform_change,
    ).grid(row=0, column=1, padx=(0, 6))
    ttk.Radiobutton(
        platform_frame, text="🍎 iOS", variable=platform_var,
        value="ios", command=on_platform_change,
    ).grid(row=0, column=2)

    # 연결 버튼 / 상태 행
    connection_frame = ttk.Frame(adb_frame)
    connection_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))

    ttk.Button(connection_frame, text="디바이스 연결", command=on_check_connection).grid(
        row=0, column=0, padx=(0, 10)
    )

    device_label = ttk.Label(connection_frame, text="연결된 디바이스: 없음", foreground="red")
    device_label.grid(row=0, column=1, sticky=tk.W)

    info_text = tk.Text(adb_frame, height=3, width=70, state='disabled', font=tk_font, bg='#f8f8f8', fg='#000000')
    info_text.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))

    # 2. 스크립트 선택 섹션
    script_frame = ttk.LabelFrame(main_frame, text="📜 스크립트 선택", padding="10")
    script_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

    selection_frame = ttk.Frame(script_frame)
    selection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))

    ttk.Label(selection_frame, text="실행할 스크립트").grid(row=0, column=0, sticky=tk.W)

    script_var = tk.StringVar()
    script_combo = ttk.Combobox(
        selection_frame,
        textvariable=script_var,
        values=list(available_scripts.keys()),
        state="readonly",
        width=50,
    )
    script_combo.grid(row=0, column=1, padx=(10, 0), sticky=(tk.W, tk.E))

    ttk.Button(selection_frame, text="새로고침", command=refresh_scripts).grid(
        row=0, column=2, padx=(5, 0)
    )

    # 3. 번호/단어 범위 설정
    range_frame = ttk.LabelFrame(
        main_frame, text="🔢 번호 및 단어 추가 범위 설정 (1~999)", padding="10"
    )
    range_frame.grid(row=2, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(0, 10))

    ttk.Label(range_frame, text="시작 번호:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
    start_num_var = tk.StringVar(value="1")
    ttk.Entry(range_frame, textvariable=start_num_var, width=8).grid(row=0, column=1, padx=(0, 20))

    ttk.Label(range_frame, text="마지막 번호:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
    end_num_var = tk.StringVar(value="600")
    ttk.Entry(range_frame, textvariable=end_num_var, width=8).grid(row=0, column=3, padx=(0, 20))

    ttk.Label(range_frame, text="추가할 단어 갯수:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
    word_count_var = tk.StringVar(value="200")
    ttk.Entry(range_frame, textvariable=word_count_var, width=8).grid(row=0, column=5)

    # 4. 실행 버튼들
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 2))

    run_button = ttk.Button(button_frame, text="🚀 스크립트 실행", command=on_run_script, state='disabled')
    run_button.grid(row=0, column=0, padx=(0, 10))

    stop_button = ttk.Button(button_frame, text="⏹️ 실행 중지", command=on_stop_script, state='disabled')
    stop_button.grid(row=0, column=1)

    # 5. 로그 출력 섹션
    log_frame = ttk.LabelFrame(main_frame, text="📋 진행 로그", padding="20")
    log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

    log_text = scrolledtext.ScrolledText(
        log_frame,
        height=20,
        state='disabled',
        font=tk_font,
        bg="#2c2c2c",
        fg="#F1F1F1",
        insertbackground='#ffffff',
    )
    log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(4, weight=1)
    log_frame.columnconfigure(0, weight=1)
    log_frame.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    selection_frame.columnconfigure(1, weight=1)
    connection_frame.columnconfigure(1, weight=1)

    log_message("🚀 Appium Script Runner v1.0")
    log_message("   • 스팸 전화번호 및 차단 단어 자동 추가 프로그램 (Android / iOS)")
    log_message("   • 최대 등록 한도 팝업 확인용 (스크립트별 일정 시간 소요)")
    log_message("   • 실행 전 APPIUM 환경 설정이 필요합니다.")
    log_message("=" * 60)
    log_message("📋 사용방법:")
    log_message("   1. 플랫폼 선택 (Android / iOS)")
    log_message("   2. 디바이스 연결 확인")
    log_message("   3. 스크립트 선택")
    log_message("      ❗ 스크립트 실행 전, 연결한 단말에서 해당 기능 화면으로 진입해주세요.")
    log_message("      예) 익시오 스팸번호 추가 - 설정 > 스팸 알림 및 수신 차단 > 전화 차단 진입")
    log_message("   4. 스크립트 실행")
    log_message("=" * 60)

    refresh_scripts()

    root.after(50, _process_log_queue)
    root.after(1000, auto_open_appium_terminal)

    root.mainloop()
