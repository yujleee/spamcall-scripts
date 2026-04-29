# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_dynamic_libs
import os
import sys

# Windows 전용 DLL 수집 (macOS에서는 건너뜀)
additional_binaries = collect_dynamic_libs('tkinter')

if sys.platform == 'win32':
    python_path = os.path.dirname(sys.executable)
    dll_path = os.path.join(python_path, 'DLLs')
    if os.path.isdir(dll_path):
        for file in os.listdir(dll_path):
            if file.lower().endswith('.dll'):
                additional_binaries.append((os.path.join(dll_path, file), '.'))

try:
    additional_binaries += collect_dynamic_libs('appium')
except Exception:
    pass

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=additional_binaries,
    datas=[
        ('scripts', 'scripts'),
        ('src', 'src'),
        ('utils', 'utils'),
        ('img', 'img'),
    ],
    hiddenimports=[
        # 앱 서브모듈
        'src.core.environment',
        'src.core.runtime',
        'src.device.adb',
        'src.gui.app',
        'src.gui.dialogs',
        'src.runner',
        'src.runner.config',
        'src.runner.executor',
        'utils.safe_print',
        'utils.font',
        'utils.util',
        # Appium
        'appium',
        'appium.webdriver',
        'appium.webdriver.common.appiumby',
        'appium.options',
        'appium.options.android',
        # tkinter
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        '_tkinter',
        # 표준 라이브러리
        'queue',
        'importlib.util',
        'subprocess',
        'threading',
        'platform',
        'pathlib',
        'json',
        'zipfile',
        'tarfile',
        'urllib.request',
        'urllib.error',
        'ctypes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

icon_path = os.path.join('img', 'icon.ico')

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Appium Script Runner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)
