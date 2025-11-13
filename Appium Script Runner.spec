# 빌드 명령어 pyinstaller "Appium Script Runner.spec" --clean

# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_dynamic_libs

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=collect_dynamic_libs('tkinter'),
    datas=[
        ('scripts', 'scripts'),
        ('src', 'src'),
        ('utils', 'utils'),
        ('img', 'img'),
    ],
    hiddenimports=[
        'appium',
        'appium.webdriver',
        'appium.webdriver.common.appiumby',
        'appium.options.android',
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.support',
        'selenium.webdriver.support.expected_conditions',
        'selenium.webdriver.support.wait',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.common.by',
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
        'importlib',
        'importlib.util',
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