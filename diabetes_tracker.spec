# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['diabetes_tracker.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'sqlite3',
        'datetime',
        'json',
        'tkcalendar',
        'ttkbootstrap',
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.backends.backend_tkagg',
        'openpyxl',
        'reportlab',
        'requests',
        'subprocess',
        'threading',
        'os',
        'sys',
        'platform',
        'webbrowser'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'smartcard',
        'pyscard',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6'
    ],
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
    name='Diabetes_Tracker_v1.6.0',
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
    icon=None,
    version_file=None,
) 