# Command-line bootstrap for launching the PyQt optimization GUI from a source checkout.

# ------------------------------------------------------------------------------------
# Module: run_gui.py
# Summary: command-line entry point and import-path bootstrap helper.
# Implementation: the local src directory is added to sys.path and the Qt GUI main function is launched.
# Responsibility: starts the dissertation framework from a source checkout without package installation.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import sys
from multiprocessing import freeze_support
from pathlib import Path


def _ensure_src_on_path() -> None:
    # Add the local `src` directory to `sys.path` so package imports work in-place.
    # Returns:
    # None: The interpreter import path is updated in-place.
    root = Path(__file__).resolve().parent
    src = root / "src"
    if src.is_dir():
        sys.path.insert(0, str(src))


def main() -> None:
    # Start the GUI application after preparing imports for a local source tree.
    # Returns:
    # None: Control is passed to the Qt application entry point.
    freeze_support()
    _ensure_src_on_path()
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        from pymoo_gui.packaging_smoke import main as smoke_main

        sys.exit(smoke_main(sys.argv[2:]))
    from pymoo_gui.app import main as gui_main

    gui_main()


if __name__ == "__main__":
    main()
