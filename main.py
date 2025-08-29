"""
Appium Script Runner - Entry Point
GUI 기반 Appium 스크립트 실행기

사용법:
    python main.py
    또는 exe로 패키징 후 실행
"""

import sys, os
import tkinter as tk
from tkinter import messagebox

def check_requirements():
    """실행 전 필요한 요구사항들을 체크"""
    
    # 1. scripts 폴더 존재 여부 확인
    if not os.path.exists("scripts"):
        messagebox.showerror(
            "오류", 
            "scripts 폴더를 찾을 수 없습니다.\n"
            "프로그램과 같은 경로에 scripts 폴더가 있는지 확인해주세요."
        )
        return False
    
    # 2. scripts 폴더에 Python 파일이 있는지 확인
    script_files = [f for f in os.listdir("scripts") if f.endswith('.py')]
    if not script_files:
        messagebox.showwarning(
            "경고",
            "scripts 폴더에 Python 스크립트 파일(.py)이 없습니다.\n"
            "실행할 스크립트를 scripts 폴더에 넣어주세요."
        )
    
    # 3. ADB 설치 여부 확인 (선택적)
    try:
        import subprocess
        subprocess.run(['adb', 'version'], 
                      capture_output=True, timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        result = messagebox.askyesno(
            "ADB 확인",
            "ADB가 설치되어 있지 않거나 PATH에 설정되지 않았습니다.\n"
            "계속 진행하시겠습니까?\n\n"
            "(나중에 GUI에서 ADB 연결을 확인할 수 있습니다)"
        )
        if not result:
            return False
    
    return True

def main():
    """메인 실행 함수"""
    
    # 콘솔창 숨기기 (exe 패키징 시 유용)
    if hasattr(sys, 'frozen'):
        # PyInstaller로 패키징된 경우
        import ctypes
        ctypes.windll.user32.ShowWindow(
            ctypes.windll.kernel32.GetConsoleWindow(), 0
        )
    
    # tkinter 지원 확인
    try:
        root = tk.Tk()
        root.withdraw()  # 임시로 숨기기
    except Exception as e:
        print(f"tkinter 초기화 오류: {e}")
        print("GUI 라이브러리를 사용할 수 없습니다.")
        sys.exit(1)
    
    # 요구사항 체크
    if not check_requirements():
        sys.exit(1)
    
    # GUI 모듈 임포트 및 실행
    try:
        from gui import create_gui
        
        root.destroy()  # 임시 root 창 완전히 제거
        
        # GUI 실행
        create_gui()
        
    except ImportError as e:
        messagebox.showerror(
            "모듈 오류",
            f"runner.py 모듈을 불러올 수 없습니다: {e}\n"
            "runner.py 파일이 같은 폴더에 있는지 확인해주세요."
        )
        sys.exit(1)
    except Exception as e:
        messagebox.showerror("오류", f"프로그램 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()