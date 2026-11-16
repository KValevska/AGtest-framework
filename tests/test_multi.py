from __future__ import annotations

import json
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
from pymoo_gui.metrics import get_hv_ref_point


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
    assert headers[3:] == [
        "IGD",
        "GD",
        "IGD+",
        "GD+",
        "Pairwise objective-space spread",
        "Delta",
        "HV",
        "KKTPM",
    ]
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
    run_id = str(result["run_id"])
    assert run_id.endswith("_NSGA2_SCHAFFER_seed1")
    configuration_sheets: list[bytes] = []
    for path_key in ("metrics_path", "solutions_path"):
        path = Path(str(result[path_key]))
        assert path.is_file()
        assert path.stem == run_id
        with ZipFile(path) as workbook:
            assert "xl/workbook.xml" in workbook.namelist()
            workbook_xml = workbook.read("xl/workbook.xml").decode("utf-8")
            assert "Configuration" in workbook_xml
            configuration_xml = workbook.read("xl/worksheets/sheet2.xml")
            configuration_sheets.append(configuration_xml)
            configuration_text = configuration_xml.decode("utf-8")
            assert run_id in configuration_text
            assert "Random seed" in configuration_text
            assert "Problem parameter" in configuration_text
            assert "Algorithm parameter: pop_size" in configuration_text
            assert "Framework name" in configuration_text
            assert "Git commit" in configuration_text
            assert "Algorithm implementation type" in configuration_text
            assert "Final evaluations (n_eval)" in configuration_text
            assert "HV frozen ideal point" in configuration_text
            assert "pymoo version" in configuration_text
            assert "scikit-learn version" in configuration_text
            assert "Run status" in configuration_text
            if path_key == "metrics_path":
                assert "HV Configuration" in workbook_xml
    assert configuration_sheets[0] == configuration_sheets[1]
    manifest_path = Path(str(result["manifest_path"]))
    runs_path = Path(str(result["runs_path"]))
    assert manifest_path.is_file()
    assert runs_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["experiment"]["status"] == "completed"
    assert manifest["runs"][0]["run_id"] == run_id
    assert manifest["runs"][0]["configuration"]["final_evaluations"]
    assert manifest["runs"][0]["configuration"]["status"] == "completed"
    with ZipFile(runs_path) as workbook:
        workbook_xml = workbook.read("xl/workbook.xml").decode("utf-8")
        assert 'name="Runs"' in workbook_xml
        assert 'name="Configuration"' in workbook_xml


def test_multi_worker_skips_incompatible_algorithm_problem_pair(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    completed: list[list[dict[str, object]]] = []
    worker = MultiExperimentWorker(
        build_multi_run_specs(["schaffer"], ["diskplus"]),
        n_gen=1,
        seed=1,
        project_root=tmp_path,
    )
    worker.done.connect(completed.append)

    worker.run()

    assert app is not None
    assert completed[0][0]["status"] == "skipped"
    assert "requires a benchmark" in str(completed[0][0]["error"])
    assert completed[0][0]["metrics_path"] == ""
    assert completed[0][0]["solutions_path"] == ""


def test_cancelled_multi_writes_recoverable_manifest_and_run_summary(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    cancelled: list[list[dict[str, object]]] = []
    worker = MultiExperimentWorker(
        build_multi_run_specs(["schaffer"], ["nsga2"]),
        n_gen=2,
        seed=3,
        project_root=tmp_path,
    )
    worker.cancelled.connect(cancelled.append)
    worker.request_cancel()

    worker.run()

    assert app is not None
    assert cancelled == [[]]
    assert worker.manifest_path.is_file()
    assert worker.runs_path.is_file()
    manifest = json.loads(worker.manifest_path.read_text(encoding="utf-8"))
    assert manifest["experiment"]["status"] == "cancelled"
    assert manifest["runs"] == []


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


def test_hv_reference_point_is_scaled_from_the_known_front() -> None:
    front = np.array([[0.0, 4.0], [1.0, 1.0], [4.0, 0.0]])
    reference = get_hv_ref_point("Schaffer", 2, pareto_front=front)

    np.testing.assert_allclose(reference, [4.4, 4.4])
    assert np.all(front < reference)


def test_main_auto_hv_reference_uses_selected_problem_front() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.problem_combo.setCurrentIndex(window.problem_combo.findData("schaffer"))
    app.processEvents()

    reference = np.asarray(window._auto_hv_ref_point())
    assert np.all(reference > np.max(window._plot_known_pf, axis=0))
    np.testing.assert_allclose(reference, [4.4, 4.4], atol=1e-8)
    window.close()


def test_main_requires_manual_hv_point_when_known_front_is_unavailable() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.problem_combo.setCurrentIndex(window.problem_combo.findData("integer_portfolio"))
    app.processEvents()

    valid, values, mode, error = window._hv_ref_point_state()
    assert valid is False
    assert values is None
    assert mode == "AUTO"
    assert "manual" in str(error).lower()

    window.hv_manual_radio.setChecked(True)
    window.hv_manual_edit.setText("2 2")
    app.processEvents()
    valid, values, mode, error = window._hv_ref_point_state()
    assert valid is True
    assert values == [2.0, 2.0]
    assert mode == "MANUAL"
    assert error is None
    window.close()
