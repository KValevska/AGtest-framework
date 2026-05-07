"""
EN:
Command-line bootstrap for launching the PyQt optimization GUI from a source checkout.

PL:
Ten plik uruchamia aplikacje z katalogu projektu, nawet gdy pakiet nie zostal
zainstalowany w systemie.
"""

# ------------------------------------------------------------------------------------
# File: run_gui.py
# Contents: command-line entry point and import-path bootstrap helper.
# What happens here: the local src directory is added to sys.path and the Qt GUI main function is launched.
# Role in the framework: starts the dissertation framework from a source checkout without package installation.
# Author: mgr inż. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    """
    EN:
    Add the local `src` directory to `sys.path` so package imports work in-place.

    PL:
    Dodaje lokalny katalog `src` do sciezki Pythona, aby aplikacje mozna bylo
    uruchomic bez instalowania pakietu.

    Returns:
        None: EN: The interpreter import path is updated in-place.
              PL: Funkcja nic nie zwraca, tylko zmienia sciezke importu.
    """
    root = Path(__file__).resolve().parent
    src = root / "src"
    if src.is_dir():
        sys.path.insert(0, str(src))


def main() -> None:
    """
    EN:
    Start the GUI application after preparing imports for a local source tree.

    PL:
    Przygotowuje importy i wlacza glowne okno programu.

    Returns:
        None: EN: Control is passed to the Qt application entry point.
              PL: Funkcja nie zwraca danych, tylko startuje program.
    """
    _ensure_src_on_path()
    from pymoo_gui.app import main as gui_main

    gui_main()


if __name__ == "__main__":
    main()
