# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

# Collect all NLTK data
nltk_datas = collect_data_files('nltk')

# Collect BeautifulSoup4 and related packages
bs4_datas, bs4_binaries, bs4_hiddenimports = collect_all('bs4')
requests_datas, requests_binaries, requests_hiddenimports = collect_all('requests')
urllib3_datas, urllib3_binaries, urllib3_hiddenimports = collect_all('urllib3')

# Additional hidden imports for common issues
additional_hiddenimports = [
    'bs4',
    'bs4.builder',
    'bs4.builder._htmlparser',
    'bs4.builder._lxml',
    'bs4.dammit',
    'beautifulsoup4',
    'requests',
    'requests.packages',
    'requests.packages.urllib3',
    'urllib3',
    'urllib3.util',
    'urllib3.util.retry',
    'urllib3.packages',
    'urllib3.packages.six',
    'lxml',
    'lxml.etree',
    'lxml.html',
    'nltk',
    'nltk.data',
    'nltk.corpus',
    'nltk.tokenize',
    'nltk.stem',
    'nltk.chunk',
    'nltk.tag',
    'pandas',
    'numpy',
    'reportlab',
    'reportlab.pdfgen',
    'reportlab.lib',
    'reportlab.platypus',
    'openpyxl',
    'collections.abc',
    'pkg_resources',
    'pkg_resources.py2_warn'
]

# Combine all hidden imports
all_hiddenimports = (
    additional_hiddenimports + 
    bs4_hiddenimports + 
    requests_hiddenimports + 
    urllib3_hiddenimports
)

# Data files to include
datas = [
    ('config.py', '.'),
    ('analyzer.py', '.'),
    ('scraper.py', '.'),
    ('gap_finder.py', '.'),
    ('exporter.py', '.'),
]

# Add collected data files
datas.extend(nltk_datas)
datas.extend(bs4_datas)
datas.extend(requests_datas)
datas.extend(urllib3_datas)

# Binaries
binaries = []
binaries.extend(bs4_binaries)
binaries.extend(requests_binaries)
binaries.extend(urllib3_binaries)

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],
    binaries=binaries,
    datas=datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'tkinter.test',
        'test',
        'unittest',
        'pydoc',
        'doctest'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SEO_Analyzer_Pro',
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
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)