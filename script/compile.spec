# -*- mode: python ; coding: utf-8 -*-

import os
import importlib.util
from PyInstaller.utils.hooks import collect_all

PROJECT_DIR = os.getcwd()

CONFIG_PATH = os.path.join(PROJECT_DIR, "script", "config.py")
spec_config = importlib.util.spec_from_file_location("build_config", CONFIG_PATH)
config = importlib.util.module_from_spec(spec_config)
spec_config.loader.exec_module(config)

datas = [(config.RESOURCE_PATH, os.path.basename(config.RESOURCE_PATH))]
binaries = []
hiddenimports = []

for lib in config.EXTRA_LIBS:
	_datas, _bins, _hidden = collect_all(lib)
	datas+=_datas
	binaries+=_bins
	hiddenimports+=_hidden

a = Analysis(
    [config.MAIN_PYW],
    pathex=[PROJECT_DIR],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

if config.IS_SINGLE_FILE:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        name=config.NAME,
        console=False,
        icon=config.ICON_PATH,
        contents_directory="app",
    )
    app = exe
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=config.NAME,
        console=False,
        icon=config.ICON_PATH,
        contents_directory="app",
	)
    app = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        name=config.NAME,
    )

