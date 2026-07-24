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

# appium/selenium 및 이들의 런타임 의존 패키지 전체 수집
# (scripts/*.py는 importlib로 동적 로드되어 PyInstaller 정적 분석 대상에 안 잡히므로
#  런타임에 필요한 서드파티 패키지를 여기서 명시적으로 모두 수집해야 함)
_runtime_packages = [
    'appium', 'selenium',
    'urllib3', 'certifi', 'idna',
    'trio', 'trio_websocket', 'wsproto', 'outcome', 'sniffio',
    'attr', 'attrs', 'cffi', 'pycparser',
    'h11', 'websocket', 'socks', 'sortedcontainers',
    'exceptiongroup', 'typing_extensions',
]

extra_datas = []
extra_hiddenimports = []
for _pkg in _runtime_packages:
    _datas, _binaries, _hiddenimports = collect_all(_pkg)
    extra_datas += _datas
    additional_binaries += _binaries
    extra_hiddenimports += _hiddenimports

# collect_all()은 "패키지"(디렉터리+__init__.py)가 아닌 단일 .py 모듈은
# 데이터 파일로 추출해주지 않는다 (PYZ 안에 바이트코드로만 들어감).
# 외부 시스템 Python이 BASE_DIR 경유로 이 파일들을 직접 찾아 읽어야 하므로
# loose 파일로도 명시적으로 복사해 둔다.
import importlib.util as _ilu
for _mod in ('typing_extensions', 'socks', 'sockshandler'):
    _spec = _ilu.find_spec(_mod)
    if _spec and _spec.origin:
        extra_datas.append((_spec.origin, '.'))

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=additional_binaries,
    datas=[
        ('scripts', 'scripts'),
        ('src', 'src'),
        ('utils', 'utils'),
        ('img', 'img'),
        ('portable.flag', '.'),   # 포터블 빌드 식별자
    ] + extra_datas,
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
    ] + extra_hiddenimports,
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
        name='Appium Script Runner Portable',
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
        name='Appium Script Runner Portable',
    )

# ── macOS: .app 번들 ────────────────────────────────────────────
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='Appium Script Runner Portable',
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
        name='Appium Script Runner Portable',
    )

    BUNDLE(
        coll,
        name='Appium Script Runner Portable.app',
        icon=os.path.join('img', 'icon.icns'),
        bundle_identifier='com.spamcall.appiumscriptrunner.portable',
        info_plist={
            'NSHighResolutionCapable': True,
            'LSBackgroundOnly': False,
        },
    )
