# PyInstaller spec for JARVIS Windows EXE
# Install: pip install pyinstaller
# Build: pyinstaller jarvis.spec

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['/workspaces/jarvis-ai'],
    binaries=[],
    datas=[
        ('web', 'web'),
        ('core', 'core'),
    ],
    hiddenimports=['core.agent', 'core.memory', 'core.brain', 'optimizer', 'psutil', 'speech_recognition', 'pyttsx3'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='JARVIS_AI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='JARVIS_AI'
)