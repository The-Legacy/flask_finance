# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the directory where this spec file is located
spec_root = Path(__file__).parent

block_cipher = None

# Data files to include
datas = [
    (str(spec_root / 'templates'), 'templates'),
    (str(spec_root / 'static'), 'static'),
]

# Hidden imports needed for Flask app
hiddenimports = [
    'flask',
    'flask.templating',
    'flask.json.tag',
    'sqlalchemy',
    'sqlalchemy.ext.baked',
    'werkzeug',
    'werkzeug.security',
    'jinja2',
    'click',
    'itsdangerous',
    'markupsafe',
    'flask_sqlalchemy',
    'datetime',
    'os',
    'models.transaction',
    'models.loan',
    'models.investment',
    'models.account',
    'models.budget',
    'database',
    'utils.tax_calculator'
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='flask-finance',
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
