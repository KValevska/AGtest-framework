from __future__ import annotations

import os
import tempfile
from pathlib import Path
from zipfile import ZipFile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "pymoo_gui_mpl_cache"))

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from pymoo_gui.app import MainWindow
from pymoo_gui.multi import (
    MultiExperimentWorker,
    build_multi_run_specs,
    default_entry_params,
    metrics_table_data,
    solution_table_data,
)


def test_default_entry_params_returns_independent_values() -> None:
    source = {
        "form_fields": {
            "population_size": {"default": 100},
            "weights": {"default": [0.25, 0.75]},
            "without_default": {"kind": "str"},
        }
    }

    first = default_entry_params(source)
    second = default_entry_params(source)

    assert first == {"population_size": 100, "weights": [0.25, 0.75]}
    first["weights"].append(1.0)
    assert second["weights"] == [0.25, 0.75]


def test_build_multi_run_specs_creates_problem_major_cartesian_product() -> None:
    specs = build_multi_run_specs(
        problem_keys=["schaffer", "kursawe"],
        algorithm_keys=["nsga2", "spea2"],
    )

    assert [(spec.problem_key, spec.algorithm_key) for spec in specs] == [
        ("schaffer", "nsga2"),
        ("schaffer", "spea2"),
        ("kursawe", "nsga2"),
        ("kursawe", "spea2"),
    ]


def test_metrics_table_data_preserves_generation_history() -> None:
    headers, rows = metrics_table_data(
        [
            {"n_gen": 1, "n_eval": 100, "n_nds": 4, "igd": 0.5, "hv": 0.25},
            {"n_gen": 2, "n_eval": 200, "n_nds": 6, "igd": 0.2, "hv": 0.5},
        ]
    )

    assert headers[:3] == ["n_gen", "n_eval", "n_nds"]
    assert headers[3:] == ["IGD", "GD", "IGD+", "GD+", "Spread", "Delta", "HV", "KKTPM"]
    assert rows[0][:4] == [1, 100, 4, 0.5]
    assert rows[1][9] == 0.5


def test_solution_table_data_exports_objectives_and_decisions() -> None:
    headers, rows = solution_table_data(
        {
            "feasible_nd_F": np.array([[0.1, 0.9], [0.3, 0.7]]),
            "feasible_nd_X": np.array([[1.0, 2.0], [3.0, 4.0]]),
        },
        n_obj=2,
    )

    assert headers == ["id", "f1", "f2", "x1", "x2"]
    assert rows == [[1, 0.1, 0.9, 1.0, 2.0], [2, 0.3, 0.7, 3.0, 4.0]]


def test_solution_table_data_keeps_headers_for_an_empty_front() -> None:
    headers, rows = solution_table_data({"feasible_nd_F": []}, n_obj=3)

    assert headers == ["id", "f1", "f2", "f3"]
    assert rows == []


def test_multi_worker_runs_and_exports_each_result(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    completed: list[list[dict[str, object]]] = []
    failures: list[str] = []
    worker = MultiExperimentWorker(
        build_multi_run_specs(["schaffer"], ["nsga2"]),
        n_gen=2,
        seed=1,
        project_root=tmp_path,
    )
    worker.done.connect(completed.append)
    worker.failed.connect(failures.append)

    worker.run()

    assert app is not None
    assert failures == []
    assert len(completed) == 1
    assert len(completed[0]) == 1
    result = completed[0][0]
    assert result["status"] == "completed"
    assert result["n_gen"] == 2
    for path_key in ("metrics_path", "solutions_path"):
        path = Path(str(result[path_key]))
        assert path.is_file()
        with ZipFile(path) as workbook:
            assert "xl/workbook.xml" in workbook.namelist()


def test_main_window_exposes_main_and_multi_tabs() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()

    assert window.tabs.count() == 3
    assert [window.tabs.tabText(index) for index in range(window.tabs.count())] == [
        "Main",
        "Multi",
        "Metric trajectories",
    ]
    assert window.multi_start_btn.isEnabled() is False

    window.multi_algorithm_list.item(0).setCheckState(Qt.Checked)
    window.multi_problem_list.item(0).setCheckState(Qt.Checked)
    app.processEvents()

    assert window.multi_selection_lbl.text() == "1 algorithms × 1 problems = 1 runs"
    assert window.multi_start_btn.isEnabled() is True
    window.close()
