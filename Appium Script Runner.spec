# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_dynamic_libs
import os
import sys

python_path = os.path.dirname(sys.executable)
dll_path = os.path.join(python_path, 'DLLs')

# Additional DLLs to include
additional_dlls = []
for file in os.listdir(dll_path):
    if file.lower().endswith('.dll'):
        additional_dlls.append((os.path.join(dll_path, file), '.'))

a = Analysis(
    ['main.py'],
    pathex=[python_path, dll_path],
    binaries=additional_dlls + collect_dynamic_libs('tkinter') + collect_dynamic_libs('appium'),
    datas=[
        ('scripts', 'scripts'),
        ('src', 'src'),
        ('utils', 'utils'),
        ('img', 'img'),
    ],
    hiddenimports=[
        'appium',
        'appium.webdriver.common.appiumby',
        'appium.options.android',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        '_tkinter',
        'subprocess',
        'threading',
        'platform',
        'os',
        'sys',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

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
    icon='img\\icon.ico'
)
