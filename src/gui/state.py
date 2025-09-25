"""상태 관리 함수들"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable
import tkinter as tk
from tkinter import scrolledtext, ttk

@dataclass
class GUIState:
    """GUI 상태를 저장하는 데이터 클래스"""
    root: tk.Tk
    device_info: Dict[str, str] = field(default_factory=dict)
    available_scripts: Dict[str, str] = field(default_factory=dict)
    current_thread: Optional[Any] = None
    
    # UI 컴포넌트들
    device_label: Optional[ttk.Label] = None
    info_text: Optional[tk.Text] = None
    script_combo: Optional[ttk.Combobox] = None
    run_button: Optional[ttk.Button] = None
    stop_button: Optional[ttk.Button] = None
    log_text: Optional[scrolledtext.ScrolledText] = None
    
    # 콜백 함수들
    log_callback: Optional[Callable[[str], None]] = None

def create_log_callback(log_text: scrolledtext.ScrolledText, root: tk.Tk) -> Callable[[str], None]:
    """로그 콜백 함수 생성"""
    def log_message(message: str) -> None:
        log_text.config(state='normal')
        
        start_idx = log_text.index("end-1c")
        log_text.insert(tk.END, f"{message}\n")
        
        for idx in range(len(message)):
            char = message[idx]
            if ord(char) > 0x1F000:  # 이모지 범위 확인
                char_start = f"{start_idx}+{idx}c"
                char_end = f"{start_idx}+{idx+1}c"
                log_text.tag_add('emoji', char_start, char_end)
        
        log_text.see(tk.END)
        log_text.config(state='disabled')
        root.update()
    
    return log_message

def update_device_info(state: GUIState, new_device_info: Dict[str, str]) -> None:
    """디바이스 정보 업데이트"""
    state.device_info.clear()
    state.device_info.update(new_device_info or {})