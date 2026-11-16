from __future__ import annotations

import os
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "pymoo_gui_mpl_cache"))

from PyQt5.QtWidgets import QApplication

from pymoo_gui.app import MainWindow
from pymoo_gui.problems import PROBLEMS


def _problem_keys(window: MainWindow) -> list[str]:
    return [str(window.problem_combo.itemData(index)) for index in range(window.problem_combo.count())]


def test_main_places_algorithm_selector_before_problem_selector() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    try:
        assert app is not None
        assert window._left.indexOf(window.alg_combo) < window._left.indexOf(window.problem_combo)
        assert window._left.indexOf(window.alg_form) < window._left.indexOf(window.problem_form)
    finally:
        window.close()


def test_constraint_required_algorithm_shows_only_constrained_problems() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    try:
        window.alg_combo.setCurrentIndex(window.alg_combo.findData("cmobr"))
        app.processEvents()

        keys = _problem_keys(window)
        assert keys
        assert "tanaka" in keys
        assert "schaffer" not in keys
        assert all(PROBLEMS[key]["capabilities"]["constrained"] for key in keys)
        assert "requires constraints" in window.problem_combo.toolTip()
    finally:
        window.close()


def test_problem_list_returns_to_all_problems_and_keeps_compatible_selection() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    try:
        window.alg_combo.setCurrentIndex(window.alg_combo.findData("cmobr"))
        window.problem_combo.setCurrentIndex(window.problem_combo.findData("tanaka"))
        app.processEvents()

        window.alg_combo.setCurrentIndex(window.alg_combo.findData("nsga2"))
        app.processEvents()

        assert window.problem_combo.count() == len(PROBLEMS)
        assert window.problem_combo.currentData() == "tanaka"
        assert "schaffer" in _problem_keys(window)
    finally:
        window.close()
