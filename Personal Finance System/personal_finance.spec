# -*- mode: python ; coding: utf-8 -*-
# personal_finance.spec — PyInstaller build spec for Personal Finance System
#
# Build command:
#   .venv\Scripts\pyinstaller.exe --noconfirm --clean personal_finance.spec
#
# Output: dist\PersonalFinanceSystem\PersonalFinanceSystem.exe

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# ── Hidden imports ─────────────────────────────────────────────────────────────
hidden_imports = [
    # CustomTkinter
    "customtkinter",
    *collect_submodules("customtkinter"),
    # Matplotlib backends
    "matplotlib",
    "matplotlib.backends.backend_tkagg",
    "matplotlib.backends._backend_tk",
    *collect_submodules("matplotlib"),
    # SQLite / stdlib
    "sqlite3",
    "_sqlite3",
    # PIL / Pillow
    "PIL",
    "PIL._tkinter_finder",
    *collect_submodules("PIL"),
    # Project packages
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
    # tkinter
    "tkinter",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "tkinter.ttk",
]

# ── Data files to bundle ───────────────────────────────────────────────────────
datas = []

# CustomTkinter theme assets (REQUIRED — contains .json theme files and images)
datas += collect_data_files("customtkinter", include_py_files=False)

# PIL data
datas += collect_data_files("PIL")

# Matplotlib data (fonts, style sheets, etc.)
datas += collect_data_files("matplotlib")

# App assets (icon, screenshot)
datas += [
    ("assets", "assets"),
]

# ── Analysis ───────────────────────────────────────────────────────────────────
a = Analysis(
    ["src/main.py"],
    pathex=[],            # INTENTIONALLY EMPTY: do NOT add project root to avoid
                          # frozen exe finding source .py files on disk when run
                          # from the project directory during development tests.
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter.test",
        "unittest",
        "test",
        "distutils",
        "setuptools",
        "email",
        "html",
        "http",
        "urllib",
        "xml",
        "xmlrpc",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ── PYZ archive ───────────────────────────────────────────────────────────────
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── EXE ───────────────────────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,       # use COLLECT (folder build, not onefile)
    name="PersonalFinanceSystem",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,               # no console window (windowed mode)
    icon="assets/icons/app.ico",
)

# ── COLLECT (folder layout) ───────────────────────────────────────────────────
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PersonalFinanceSystem",  # dist\PersonalFinanceSystem\
)
