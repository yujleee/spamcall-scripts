# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_all, collect_submodules
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

# appium 패키지 전체 수집
appium_datas, appium_binaries, appium_hiddenimports = collect_all('appium')
additional_binaries += appium_binaries

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=additional_binaries,
    datas=[
        ('scripts', 'scripts'),
        ('src', 'src'),
        ('utils', 'utils'),
        ('img', 'img'),
    ] + appium_datas,
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
    ] + appium_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure)

# ── Windows: one-dir 모드 ───────────────────────────────────────
if sys.platform == 'win32':
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='Appium Script Runner',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=os.path.join('img', 'icon.ico'),
    )

    COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=False,
        upx_exclude=[],
        name='Appium Script Runner',
    )

# ── macOS: .app 번들 ────────────────────────────────────────────
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='Appium Script Runner',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=os.path.join('img', 'icon.icns'),
    )

    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=False,
        upx_exclude=[],
        name='Appium Script Runner',
    )

    BUNDLE(
        coll,
        name='Appium Script Runner.app',
        icon=os.path.join('img', 'icon.icns'),
        bundle_identifier='com.spamcall.appiumscriptrunner',
        info_plist={
            'NSHighResolutionCapable': True,
            'LSBackgroundOnly': False,
        },
    )
