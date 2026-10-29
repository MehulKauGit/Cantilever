# debug_build.spec — temporary console build for crash diagnosis
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

hidden_imports = [
    "customtkinter",
    *collect_submodules("customtkinter"),
    "matplotlib",
    "matplotlib.backends.backend_tkagg",
    "matplotlib.backends._backend_tk",
    *collect_submodules("matplotlib"),
    "sqlite3",
    "_sqlite3",
    "PIL",
    "PIL._tkinter_finder",
    *collect_submodules("PIL"),
    "src",
    "src.config",
    "src.database",
    "src.database.db_manager",
    "src.database.schema",
    "src.database.dao",
    "src.gui",
    "src.gui.app",
    "src.gui.components",
    "src.gui.pages",
    "src.models",
    "src.services",
    "src.services.finance_service",
    "src.services.budget_service",
    "src.services.savings_service",
    "src.services.settings_service",
    "src.utils",
    "src.utils.helpers",
    "tkinter",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "tkinter.ttk",
]

datas = []
datas += collect_data_files("customtkinter", include_py_files=False)
datas += collect_data_files("PIL")
datas += collect_data_files("matplotlib")
datas += [("assets", "assets")]

a = Analysis(
    ["src/main.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
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
    [],
    exclude_binaries=True,
    name="PFS_debug",
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    console=True,   # <-- console ON so we see the traceback
    icon="assets/icons/app.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="PFS_debug",
)
