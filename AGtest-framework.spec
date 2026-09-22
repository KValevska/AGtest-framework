# Build a single Windows executable, including the interpreter and reference fronts.
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

root = Path(SPECPATH)
version_info = root / "windows-version-info.txt"
datas = [(str(path), "pymoo_gui/problems") for path in (root / "src/pymoo_gui/problems").glob("*.pf")]
datas += collect_data_files("pymoo")
datas += copy_metadata("pymoo") + copy_metadata("platypus-opt")
datas += copy_metadata("moocore")
datas += [(str(root / "LICENSE"), ".")]

a = Analysis(
    [str(root / "run_gui.py")],
    pathex=[str(root / "src")],
    binaries=[],
    datas=datas,
    # pymoo loads compiled implementations and problem modules dynamically.
    hiddenimports=collect_submodules(
        "pymoo",
        # toolbox is an alias for numpy/autograd, not a real subpackage.
        filter=lambda name: not name.startswith("pymoo.gradient.toolbox")
        and ".tests" not in name,
    ),
    hookspath=[],
    hooksconfig={"matplotlib": {"backends": ["QtAgg"]}},
    runtime_hooks=[],
    excludes=["PySide2", "PySide6", "PyQt6", "tkinter", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="AGtest-framework",
    version=str(version_info),
    debug=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)
