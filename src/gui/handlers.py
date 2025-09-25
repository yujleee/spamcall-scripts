"""이벤트 핸들러 함수들"""
import os
import tkinter as tk
from tkinter import messagebox
from main import get_resource_path
from src.runner import check_adb_connection, execute_script, stop_running_script, get_available_scripts
from src.errors import (
    create_error_handler,
    create_device_error,
    create_script_error,
    safe_execute
)
from src.logging import LogLevel, create_logger

def create_connection_handler(device_info, device_label, info_text, run_button, available_scripts, log_message, font):
    """연결 확인 핸들러 생성"""
    error_handler = create_error_handler(log_message)
    logger = create_logger(log_message)
    
    def on_check_connection():
        nonlocal device_info
        
        logger[LogLevel.INFO]("ADB 연결 확인 중...")
        
        device_info.clear()
        result = safe_execute(check_adb_connection, error_handler)
        if result:
            device_info.update(result)
        
        if not device_info:
            error = create_device_error("not_found")
            error_handler(error)
            device_label.config(text="연결된 디바이스: ❌ 없음", foreground="red")
            info_text.config(state='normal', font=font)
            info_text.delete(1.0, tk.END)
            info_text.insert(1.0, "연결된 디바이스가 없습니다.\n\n확인사항:\n1. USB 디버깅이 활성화되어 있는지\n2. ADB 드라이버가 설치되어 있는지\n3. 디바이스가 올바르게 연결되어 있는지")
            info_text.config(state='disabled')
            run_button.config(state='disabled')
            logger[LogLevel.ERROR]("연결된 디바이스를 찾을 수 없습니다.")
            return
        
        device_label.config(text=f"✅ 연결된 디바이스: {device_info['deviceName']}", foreground="green", font=font)
        
        info_content = f"📱 모델: {device_info['model']}\n🤖 안드로이드 버전: {device_info['platformVersion']}\n🔗 디바이스 ID: {device_info['deviceName']}"
        info_text.config(state='normal', font=font)
        info_text.delete(1.0, tk.END)
        info_text.insert(1.0, info_content)
        info_text.config(state='disabled')
        
        if available_scripts:
            run_button.config(state='normal')
        
        logger[LogLevel.SUCCESS](f"디바이스 연결 완료: {device_info['deviceName']}")
        log_message(f"📱 {device_info['model']} (Android {device_info['platformVersion']})")
    
    return on_check_connection

def create_script_handler(script_var, device_info, available_scripts, log_text, 
                        run_button, stop_button, script_combo, log_message):
    """스크립트 실행 핸들러 생성"""
    error_handler = create_error_handler(log_message)
    logger = create_logger(log_message)
    
    def on_run_script():
        selected_display_name = script_var.get()
        if not selected_display_name:
            error = create_script_error("not_found", path="스크립트가 선택되지 않음")
            error_handler(error)
            return
        
        if not device_info:
            error = create_device_error("not_found")
            error_handler(error)
            return
        
        script_filename = available_scripts.get(selected_display_name)
        if not script_filename:
            error = create_script_error("not_found", path=selected_display_name)
            error_handler(error)
            return
        
        script_path = os.path.join(get_resource_path("scripts"), script_filename)
        if not os.path.exists(script_path):
            error = create_script_error("not_found", path=script_path)
            error_handler(error)
            return
        
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
        
        def on_finish():
            run_button.config(state='normal')
            stop_button.config(state='disabled')
            script_combo.config(state='readonly')
            log_message("=" * 60)
        
        return safe_execute(
            execute_script,
            error_handler,
            script_filename=script_filename,
            device_name=device_info['deviceName'],
            platform_version=device_info['platformVersion'],
            log_callback=log_message,
            finish_callback=on_finish
        )
    
    return on_run_script

def create_stop_handler(run_button, stop_button, script_combo, log_message):
    """스크립트 중지 핸들러 생성"""
    logger = create_logger(log_message)
    
    def on_stop_script():
        logger[LogLevel.WARNING]("스크립트 중지 요청...")
        stop_running_script()
        messagebox.showinfo("⚠️ 알림", "스크립트가 중지 되었습니다.")
        run_button.config(state='normal')
        stop_button.config(state='disabled')
        script_combo.config(state='readonly')
    
    return on_stop_script

def create_refresh_handler(available_scripts, script_combo, log_message):
    """스크립트 목록 새로고침 핸들러 생성"""
    logger = create_logger(log_message)
    
    def refresh_scripts():
        available_scripts.clear()
        available_scripts.update(get_available_scripts())
        script_combo['values'] = list(available_scripts.keys())
        
        log_message("=" * 60)
        if available_scripts:
            logger[LogLevel.SUCCESS](f"📝 발견된 스크립트: {len(available_scripts)}개")
            for display_name, filename in available_scripts.items():
                log_message(f"   • {display_name} ({filename})")
        else:
            logger[LogLevel.WARNING]("scripts 폴더에서 등록된 스크립트를 찾을 수 없습니다.")
            logger[LogLevel.INFO]("   SCRIPT_MAPPING에 스크립트를 추가해주세요.")
    
    return refresh_scripts