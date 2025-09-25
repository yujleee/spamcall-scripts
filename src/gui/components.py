"""UI 컴포넌트 생성 함수들"""
import tkinter as tk
from tkinter import ttk, scrolledtext

from src.config import get_config

def create_connection_frame(parent, on_check_connection, font):
    """ADB 연결 프레임 생성"""
    adb_frame = ttk.LabelFrame(parent, text="📱 ADB 연결", 
                             padding=get_config('gui.padding.default'))
    
    connection_frame = ttk.Frame(adb_frame)
    connection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
    ttk.Button(connection_frame, text="디바이스 연결", 
              command=on_check_connection).grid(row=0, column=0, padx=(0, 10))
    
    device_label = ttk.Label(connection_frame, text="연결된 디바이스: 없음", foreground="red")
    device_label.grid(row=0, column=1, sticky=tk.W)
    
    info_text = tk.Text(adb_frame, height=4, width=70, state='disabled', 
                      font=font, bg='#f8f8f8')
    info_text.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))
    
    connection_frame.columnconfigure(1, weight=1)
    
    return adb_frame, device_label, info_text

def create_script_frame(parent, available_scripts, on_refresh):
    """스크립트 선택 프레임 생성"""
    script_frame = ttk.LabelFrame(parent, text="📜 스크립트 선택", padding="10")
    
    selection_frame = ttk.Frame(script_frame)
    selection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
    ttk.Label(selection_frame, text="실행할 스크립트").grid(row=0, column=0, sticky=tk.W)
    
    script_var = tk.StringVar()
    script_combo = ttk.Combobox(selection_frame, textvariable=script_var, 
                              values=list(available_scripts.keys()), 
                              state="readonly", width=50)
    script_combo.grid(row=0, column=1, padx=(10, 0), sticky=(tk.W, tk.E))
    
    ttk.Button(selection_frame, text="새로고침", 
              command=on_refresh).grid(row=0, column=2, padx=(5, 0))
    
    selection_frame.columnconfigure(1, weight=1)
    
    return script_frame, script_var, script_combo

def create_button_frame(parent, on_run, on_stop):
    """실행 버튼 프레임 생성"""
    button_frame = ttk.Frame(parent)
    
    run_button = ttk.Button(button_frame, text="🚀 스크립트 실행", 
                          command=on_run, state='disabled')
    run_button.grid(row=0, column=0, padx=(0, 10))
    
    stop_button = ttk.Button(button_frame, text="⏹️ 실행 중지", 
                           command=on_stop, state='disabled')
    stop_button.grid(row=0, column=1)
    
    return button_frame, run_button, stop_button

def create_log_frame(parent, font):
    """로그 출력 프레임 생성"""
    log_frame = ttk.LabelFrame(parent, text="📋 진행 로그", 
                             padding=get_config('gui.padding.log_frame'))
    
    log_config = get_config('gui.log_window')
    emoji_font = get_config('gui.fonts.emoji')
    
    log_text = scrolledtext.ScrolledText(
        log_frame, 
        height=log_config['height'],
        state='disabled',
        font=font,  # font는 get_log_font()에서 이미 OS에 맞게 설정됨
        bg=log_config['background_color'],
        fg=log_config['foreground_color'],
        insertbackground=log_config['cursor_color']
    )
    log_text.tag_configure(
        'emoji',
        font=(emoji_font['family'], emoji_font['size'])
    )
    log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    log_frame.columnconfigure(0, weight=1)
    log_frame.rowconfigure(0, weight=1)
    
    return log_frame, log_text