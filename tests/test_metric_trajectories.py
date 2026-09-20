from __future__ import annotations

import os
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "pymoo_gui_mpl_cache"))

from PyQt5.QtWidgets import QApplication

from pymoo_gui.app import MainWindow
from pymoo_gui.metrics import is_delta_supported
from pymoo_gui.viz.metric_trajectories import MetricTrajectoriesWidget


def test_metric_trajectories_store_finite_generation_values() -> None:
    app = QApplication.instance() or QApplication([])
    widget = MetricTrajectoriesWidget()
    widget.reset("NSGA-II", "Schaffer")

    widget.append_payload({"n_gen": 1, "hv": 0.25, "igd": 0.5, "gd": None})
    widget.append_payload({"n_gen": 2, "hv": 0.4, "igd": float("nan")})
    widget.append_payload({"n_gen": 2, "hv": 0.45})

    history = widget.history()
    assert app is not None
    assert history["hv"] == [(1, 0.25), (2, 0.45)]
    assert history["igd"] == [(1, 0.5)]
    assert history["gd"] == []
    assert widget._plots["hv"].getPlotItem().getAxis("bottom").labelText == "Generation"
    assert widget._plots["kktpm"].getPlotItem().titleLabel.text == "KKTPM (mean)"
    assert widget._empty_labels["hv"].isHidden()
    assert not widget._empty_labels["gd"].isHidden()
    assert not widget._empty_labels["delta"].isHidden()
    assert "NSGA-II on Schaffer" in widget.context_label.text()
    widget.close()


def test_main_run_updates_and_resets_metric_trajectories() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window._run_algorithm_key = "nsga2"
    window._run_algorithm_name = "NSGA-II"
    window._run_problem_name = "Schaffer"
    window._prepare_run_visuals()

    window._on_generation({"n_gen": 1, "n_eval": 100, "n_nds": 5, "hv": 0.3, "igd": 0.4})
    before_multi_progress = window.metric_trajectories.history()
    window._on_multi_run_progress(
        {
            "run_index": 1,
            "total_runs": 1,
            "problem_key": "schaffer",
            "algorithm_key": "nsga2",
            "n_gen": 2,
            "n_eval": 200,
            "n_nds": 7,
            "hv": 0.9,
        }
    )

    assert app is not None
    assert before_multi_progress["hv"] == [(1, 0.3)]
    assert window.metric_trajectories.history() == before_multi_progress

    window._run_algorithm_name = "SPEA2"
    window._run_algorithm_key = "spea2"
    window._run_problem_name = "Kursawe"
    window._prepare_run_visuals()
    assert all(not values for values in window.metric_trajectories.history().values())
    assert not window.metric_trajectories.is_metric_visible("delta")
    assert window.metric_trajectories._chart_containers["delta"].isHidden()
    assert all(
        not label.isHidden()
        for metric_key, label in window.metric_trajectories._empty_labels.items()
        if metric_key != "delta"
    )
    assert "SPEA2 on Kursawe" in window.metric_trajectories.context_label.text()
    window.close()


def test_delta_support_matches_metric_implementation_and_chart_visibility() -> None:
    app = QApplication.instance() or QApplication([])
    widget = MetricTrajectoriesWidget()

    assert is_delta_supported("nsga2", 2)
    assert not is_delta_supported("gde3", 2)
    assert not is_delta_supported("nsga2", 3)

    widget.reset("GDE3", "Kursawe", delta_supported=False)
    widget.append_payload({"n_gen": 1, "delta": 0.25, "hv": 0.5})
    assert not widget.is_metric_visible("delta")
    assert widget._chart_containers["delta"].isHidden()
    assert widget.history()["delta"] == []
    assert widget.history()["hv"] == [(1, 0.5)]

    widget.reset("NSGA-II", "Schaffer", delta_supported=True)
    assert widget.is_metric_visible("delta")
    assert not widget._chart_containers["delta"].isHidden()
    assert app is not None
    widget.close()


def test_clear_button_clears_console_and_visual_charts() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.text_out.append("Temporary console output")
    window._plot_known_pf = [[0.0, 1.0], [1.0, 0.0]]
    window._plot_population_F = [[0.4, 0.8]]
    window._plot_feasible_nd_F = [[0.2, 0.7]]
    window._plot_generation = 3
    window.metric_trajectories.reset("NSGA-II", "Schaffer")
    window.metric_trajectories.append_payload({"n_gen": 3, "hv": 0.5})

    window.clear_btn.click()

    assert app is not None
    assert window.text_out.toPlainText() == ""
    assert window._plot_known_pf is None
    assert window._plot_population_F is None
    assert window._plot_feasible_nd_F is None
    assert window._plot_generation is None
    assert all(not values for values in window.metric_trajectories.history().values())
    assert "No Main run is active" in window.metric_trajectories.context_label.text()
    assert window._plot_placeholder.text() == "No plot available. Start an optimization run."
    window.close()
