# -*- mode: python ; coding: utf-8 -*-
# Windows用PyInstaller設定ファイル
# Windows環境で以下のコマンドを実行してください:
# pyinstaller build_windows.spec

import sys
import os

# パス設定
script_dir = os.path.dirname(os.path.abspath(SPEC))

block_cipher = None

a = Analysis(
    ['main.py'],  # 元のメインファイルを使用（修正済み）
    pathex=[script_dir],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('components', 'components'),
        ('layouts', 'layouts'),
        ('callbacks', 'callbacks'),
        ('utils', 'utils'),
        ('images', 'images'),
        ('pdca_2025.xlsx', '.'),
    ],
    hiddenimports=[
        'dash',
        'dash_bootstrap_components',
        'plotly',
        'plotly.graph_objects',
        'plotly.express',
        'pandas',
        'openpyxl',
        'numpy',
        'dash.dependencies',
        'dash.exceptions',
        'werkzeug',
        'flask',
        'jinja2',
        'markupsafe',
        'itsdangerous',
        'click',
        'blinker',
        'six',
        'pytz',
        'dateutil',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'tkinter',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'jupyter',
        'IPython',
        'sphinx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SFA-CRM-Dashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # デバッグのためコンソール表示（問題解決後はFalseに）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Icon removed - Windows requires .ico format
)