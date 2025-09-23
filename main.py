import sys, os
import tkinter as tk
from tkinter import messagebox

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def check_requirements():
    """실행 전 필요한 요구사항들을 체크"""
    scripts_path = get_resource_path("scripts")
    
    # 1. scripts 폴더 존재 여부 확인
    if not os.path.exists(scripts_path):
        messagebox.showerror(
            "오류", 
            "scripts 폴더를 찾을 수 없습니다.\n"
            "프로그램과 같은 경로에 scripts 폴더가 있는지 확인해주세요."
        )
        return False
    
    # 2. scripts 폴더에 Python 파일이 있는지 확인
    script_files = [f for f in os.listdir(scripts_path) if f.endswith('.py')]
    if not script_files:
        messagebox.showwarning(
            "경고",
            "scripts 폴더에 Python 스크립트 파일(.py)이 없습니다.\n"
            "실행할 스크립트를 scripts 폴더에 넣어주세요."
        )
    
    return True

def check_and_setup_environment():
    """실행환경 체크 및 필요시 설정"""
    try:
        from src.environment_checker import check_environment_and_setup
        return check_environment_and_setup()
    except ImportError:
        # environment_checker가 없으면 그냥 진행
        print("환경 체크 모듈을 찾을 수 없습니다. 기본 환경으로 진행합니다.")
        return True
    except Exception as e:
        print(f"환경 체크 중 오류: {e}")
        # 오류가 있어도 일단 진행 (기존처럼)
        return True

def main():
    """메인 실행 함수"""
    
    # 콘솔창 숨기기 (exe 패키징 시 유용)
    if hasattr(sys, 'frozen'):
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 0
            )
        except:
            pass
    
    # tkinter 지원 확인
    try:
        root = tk.Tk()
        root.withdraw()  # 임시로 숨기기
    except Exception as e:
        print(f"tkinter 초기화 오류: {e}")
        print("GUI 라이브러리를 사용할 수 없습니다.")
        sys.exit(1)
    
    # 기본 요구사항 체크
    if not check_requirements():
        sys.exit(1)
    
    # 실행환경 체크 (포터블 환경 설치 등)
    if not check_and_setup_environment():
        sys.exit(1)
    
    # GUI 모듈 임포트 및 실행
    try:
        from src.gui import create_gui
        
        root.destroy()  # 임시 root 창 완전히 제거
        
        # GUI 실행
        create_gui()
        
    except ImportError as e:
        messagebox.showerror(
            "모듈 오류",
            f"gui.py 모듈을 불러올 수 없습니다: {e}\n"
            "gui.py 파일이 같은 폴더에 있는지 확인해주세요."
        )
        sys.exit(1)
    except Exception as e:
        messagebox.showerror("오류", f"프로그램 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()