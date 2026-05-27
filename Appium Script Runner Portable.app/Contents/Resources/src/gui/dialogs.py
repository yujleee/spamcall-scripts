import queue
import sys
import threading
import tkinter as tk
from tkinter import scrolledtext
from utils.font import get_log_font

tk_font = get_log_font()


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
    result_window.transient(parent)
    result_window.grab_set()

    frame = tk.Frame(result_window, padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(frame, text="🔍 시스템 환경 체크 결과", font=(tk_font[0], 12, 'bold')).pack(pady=(0, 15))

    result_text = scrolledtext.ScrolledText(frame, width=50, height=15, font=tk_font, bg='#f8f8f8')
    result_text.pack(pady=(0, 15))

    result_text.tag_configure('success', foreground='green')
    result_text.tag_configure('error', foreground='red')

    def add_line(text, tag=''):
        result_text.insert(tk.END, text + '\n', tag)

    add_line("🔍 시스템 실행환경 확인 결과:")

    for tool, label in [('node', 'Node.js'), ('appium', 'Appium'), ('adb', 'ADB')]:
        info = check_result.get(tool, {})
        if info.get('available'):
            add_line(f"✅ {label}: {info.get('version', 'Unknown')}", 'success')
        else:
            add_line(f"❌ {label}: 설치되지 않음", 'error')

    result_text.configure(state='disabled')

    tk.Button(frame, text="확인", font=tk_font, command=result_window.destroy, width=20).pack(pady=(10, 0))

    result_window.wait_window(result_window)

    if should_destroy_parent and hasattr(parent, 'destroy'):
        parent.destroy()


def show_missing_tools_dialog(missing_tools):
    """누락된 도구를 표시하고 프로그램 종료"""
    tool_descriptions = {
        'node': 'JavaScript 런타임 환경',
        'appium': '모바일 앱 자동화 프레임워크. node.js 선행 설치 필요.',
        'adb': 'Android Debug Bridge',
    }

    root = tk.Tk()
    root.title("실행환경 설정")
    root.geometry("450x400")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')

    main_frame = tk.Frame(root, padx=30, pady=30)
    main_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(
        main_frame,
        text="⚠️ 일부 도구가 누락됨",
        font=(tk_font[0], 14, 'bold'),
        fg='#FF9800',
    ).pack(pady=(0, 15))

    details_frame = tk.LabelFrame(main_frame, text="누락된 도구 목록", font=tk_font, padx=10, pady=10)
    details_frame.pack(pady=(0, 15), fill=tk.BOTH, expand=True)

    details_text = scrolledtext.ScrolledText(
        details_frame, width=45, height=2, font=tk_font, bg='#fff5f5', wrap=tk.WORD
    )
    details_text.pack(fill=tk.BOTH, expand=True)
    details_text.tag_configure('tool_name', foreground='red', font=(tk_font[0], tk_font[1], 'bold'))
    details_text.tag_configure('status', foreground='#666666')
    details_text.tag_configure('desc', foreground='#888888')

    for tool in missing_tools:
        details_text.insert(tk.END, f"❌ {tool.upper()}\n", 'tool_name')
        details_text.insert(tk.END, "   상태: 설치되지 않음\n", 'status')
        if tool in tool_descriptions:
            details_text.insert(tk.END, f"   설명: {tool_descriptions[tool]}\n", 'desc')
        details_text.insert(tk.END, "\n")

    details_text.configure(state='disabled')

    tk.Label(
        main_frame,
        text="위 도구들을 시스템에 설치한 후\n다시 실행해주세요.",
        font=tk_font,
        fg='#555555',
        justify=tk.CENTER,
    ).pack(pady=(10, 20))

    btn_frame = tk.Frame(main_frame, bg='#f44336', cursor='hand2')
    btn_frame.pack(pady=(5, 0))

    btn_label = tk.Label(
        btn_frame,
        text="🚪 프로그램 종료",
        font=(tk_font[0], tk_font[1], 'bold'),
        bg='#f44336',
        fg='white',
        padx=40,
        pady=12,
        cursor='hand2',
    )
    btn_label.pack()

    def on_btn_click(e=None):
        root.quit()

    def on_btn_enter(e):
        btn_frame.config(bg='#d32f2f')
        btn_label.config(bg='#d32f2f')

    def on_btn_leave(e):
        btn_frame.config(bg='#f44336')
        btn_label.config(bg='#f44336')

    for widget in (btn_frame, btn_label):
        widget.bind('<Button-1>', on_btn_click)
        widget.bind('<Enter>', on_btn_enter)
        widget.bind('<Leave>', on_btn_leave)

    root.mainloop()
    root.destroy()
    sys.exit(0)


def show_runtime_install_dialog():
    """포터블 런타임 다운로드/설치 진행 다이얼로그. 설치 성공 여부 반환."""
    result = [False]
    log_queue = queue.Queue()

    dialog = tk.Tk()
    dialog.title("포터블 환경 설치")
    dialog.geometry("520x430")
    dialog.resizable(False, False)
    dialog.eval('tk::PlaceWindow . center')

    main_frame = tk.Frame(dialog, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(
        main_frame,
        text="📦 포터블 실행환경 설치",
        font=(tk_font[0], 14, 'bold'),
    ).pack(pady=(0, 8))

    tk.Label(
        main_frame,
        text="Node.js · Appium · ADB를 자동으로 다운로드합니다.\n인터넷 연결이 필요하며 수 분이 소요될 수 있습니다.",
        font=tk_font,
        fg='#555555',
        justify=tk.CENTER,
    ).pack(pady=(0, 12))

    log_text = scrolledtext.ScrolledText(
        main_frame, height=12, font=tk_font,
        bg='#2c2c2c', fg='#f1f1f1', state='disabled',
    )
    log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

    status_label = tk.Label(main_frame, text="설치 준비 중...", font=tk_font, fg='#FF9800')
    status_label.pack()

    close_btn_frame = tk.Frame(main_frame, bg='#888888', cursor='hand2')
    close_btn_frame.pack(pady=(8, 0))
    close_btn_label = tk.Label(
        close_btn_frame, text="닫기", font=(tk_font[0], tk_font[1], 'bold'),
        bg='#888888', fg='white', padx=40, pady=10, cursor='hand2',
    )
    close_btn_label.pack()

    def _close(e=None):
        dialog.destroy()

    for w in (close_btn_frame, close_btn_label):
        w.bind('<Button-1>', _close)

    def _process_queue():
        while True:
            try:
                msg = log_queue.get_nowait()
                log_text.config(state='normal')
                log_text.insert(tk.END, msg + '\n')
                log_text.see(tk.END)
                log_text.config(state='disabled')
            except queue.Empty:
                break
        if dialog.winfo_exists():
            dialog.after(100, _process_queue)

    def _run_install():
        import utils.safe_print as sp
        original_safe_print = sp.safe_print
        sp.safe_print = log_queue.put
        try:
            from src.core.runtime import install_runtime
            result[0] = install_runtime()
        finally:
            sp.safe_print = original_safe_print

        if not dialog.winfo_exists():
            return
        if result[0]:
            dialog.after(0, lambda: status_label.config(text="✅ 설치 완료!", fg='green'))
            dialog.after(0, lambda: close_btn_frame.config(bg='#4CAF50'))
            dialog.after(0, lambda: close_btn_label.config(bg='#4CAF50', text="완료 — 닫기"))
        else:
            dialog.after(0, lambda: status_label.config(
                text="❌ 설치 실패. 인터넷 연결을 확인하세요.", fg='red'))
            dialog.after(0, lambda: close_btn_frame.config(bg='#f44336'))
            dialog.after(0, lambda: close_btn_label.config(bg='#f44336', text="닫기"))

    dialog.after(100, _process_queue)
    threading.Thread(target=_run_install, daemon=True).start()

    dialog.mainloop()
    return result[0]
