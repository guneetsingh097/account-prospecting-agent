# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Account Prospecting Agent (x64 Windows Store)."""

import os
SRC = os.path.dirname(os.path.abspath(SPEC))

# Build datas list, skipping files that don't exist (e.g. .env in CI)
_datas = [
    (os.path.join(SRC, 'app.py'), '.'),
    (os.path.join(SRC, 'analyzer.py'), '.'),
    (os.path.join(SRC, 'collector.py'), '.'),
    (os.path.join(SRC, 'companies.py'), '.'),
    (os.path.join(SRC, 'evaluator.py'), '.'),
    (os.path.join(SRC, 'tickers.py'), '.'),
    (os.path.join(SRC, 'workiq.py'), '.'),
    (os.path.join(SRC, '.env'), '.'),
    (os.path.join(SRC, 'templates'), 'templates'),
    (os.path.join(SRC, 'static'), 'static'),
]
datas = [(src, dst) for src, dst in _datas if os.path.exists(src)]

a = Analysis(
    [os.path.join(SRC, 'launcher.py')],
    pathex=[SRC],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'flask', 'werkzeug', 'jinja2', 'markupsafe', 'click', 'blinker', 'itsdangerous',
        'requests', 'urllib3', 'charset_normalizer', 'certifi', 'idna',
        'openai', 'httpx', 'httpcore', 'anyio', 'sniffio', 'h11', 'socksio',
        'dotenv', 'pypdf',
        'foundry_local',
        'webview', 'webview.platforms.edgechromium', 'clr_loader', 'pythonnet',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AccountProspecting',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    target_arch=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='AccountProspecting',
)

