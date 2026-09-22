from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "pymoo_gui_mpl_cache"))

import numpy as np
import pytest
from PyQt5.QtGui import QImage
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from pymoo_gui.app import MainWindow, OptimizationWorker
from pymoo_gui.viz.pareto_dialogs import UnifiedParetoWidget


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def wait_until(app, predicate, timeout=10):
    deadline = time.monotonic() + timeout
    while not predicate() and time.monotonic() < deadline:
        app.processEvents()
        QTest.qWait(10)
    app.processEvents()
    assert predicate(), "Timed out waiting for the optimization worker"


def make_worker(*, step_mode=False, n_gen=3):
    return OptimizationWorker(
        "schaffer", "nsga2", {}, {"pop_size": 12}, n_gen, 7, False, None,
        step_mode=step_mode,
    )


def test_steps_match_continuous_run_and_do_not_advance_while_paused(app):
    continuous = make_worker()
    expected = []
    continuous.generation.connect(expected.append)
    continuous.run()
    worker = make_worker(step_mode=True)
    actual, done, failed = [], [], []
    worker.generation.connect(actual.append)
    worker.done.connect(done.append)
    worker.failed.connect(failed.append)
    worker.start()
    try:
        for epoch in (1, 2):
            wait_until(app, lambda: len(actual) == epoch)
            assert worker.waiting_for_step
            QTest.qWait(80)
            assert len(actual) == epoch
            assert worker.request_next_epoch()
            assert not worker.request_next_epoch()
        wait_until(app, lambda: bool(done) or bool(failed))
        assert not failed
        assert [payload["n_gen"] for payload in actual] == [1, 2, 3]
        assert done[0]["n_gen"] == 3
        for normal, stepped in zip(expected, actual):
            np.testing.assert_allclose(normal["population_F"], stepped["population_F"])
    finally:
        worker.request_cancel()
        assert worker.wait(5000)


def test_stop_wakes_unlimited_worker_paused_after_epoch_one(app):
    worker = make_worker(step_mode=True, n_gen=None)
    generations, cancelled = [], []
    worker.generation.connect(generations.append)
    worker.cancelled.connect(cancelled.append)
    worker.start()
    try:
        wait_until(app, lambda: bool(generations))
        worker.request_cancel()
        wait_until(app, lambda: bool(cancelled))
        assert cancelled[0]["n_gen"] == 1
        assert len(generations) == 1
    finally:
        worker.request_cancel()
        assert worker.wait(5000)


def test_browse_epochs_preserves_snapshots_and_keeps_metrics_history(app):
    window = MainWindow()
    try:
        points = np.array([[0.2, 0.7], [0.5, 0.4]])
        window._on_generation({"n_gen": 1, "population_F": points, "feasible_nd_F": points, "hv": 0.1})
        points[:] = 0.9
        window._on_generation({"n_gen": 2, "population_F": points, "feasible_nd_F": points, "hv": 0.2})
        window.previous_epoch_btn.click()
        assert window.epoch_spin.value() == 1
        np.testing.assert_allclose(window._plot_feasible_nd_F, [[0.2, 0.7], [0.5, 0.4]])
        window._on_generation({"n_gen": 3, "population_F": points, "hv": 0.3})
        assert window._plot_widget.render_snapshot()["gen"] == 1
        assert len(window.metric_trajectories.history()["hv"]) == 3
        window.next_epoch_btn.click()
        assert window._plot_generation == 2
        window.epoch_spin.setValue(1)
        assert window._plot_generation == 1
        window.latest_epoch_btn.click()
        assert window._plot_generation == 3
        window._prepare_run_visuals()
        assert window._epoch_history == {}
        assert not window.epoch_spin.isEnabled()
    finally:
        window.close()


@pytest.mark.parametrize("dim", [2, 3])
def test_grid_and_complete_png_export_preserve_current_view(app, tmp_path, dim):
    points = np.array([[0.2, 0.7, 0.5], [0.5, 0.4, 0.1]])[:, :dim]
    widget = UnifiedParetoWidget(points)
    widget.resize(800, 650)
    widget.show()
    try:
        widget.update_points(points, points, points, 2)
        widget.set_auto_scale(False)
        widget.set_grid(True, 2)
        dialog = widget._dialog
        if dim == 2:
            ticks = dialog.plot.getAxis("bottom").tickValues(0, 6, 600)
            assert ticks == [(2, [0.0, 2.0, 4.0, 6.0])]
            dialog.plot.setRange(xRange=(-2, 4), yRange=(-1, 3), padding=0)
            before = dialog.plot.viewRange()
            assert dialog.scatter_front.opts["size"] > dialog.scatter_pop.opts["size"]
        else:
            np.testing.assert_allclose(np.diff(dialog.ax.xaxis.get_major_locator().tick_values(0, 6)), 2)
            dialog.ax.set_xlim(-2, 4)
            dialog.ax.view_init(elev=30, azim=60)
            before = dialog.get_axis_limits()
            assert dialog.scatter_front.get_sizes()[0] > dialog.scatter_pop.get_sizes()[0]
        widget.set_grid(False, 2)
        app.processEvents()
        path = tmp_path / f"pareto_{dim}d.png"
        widget.export_png(str(path))
        image = QImage(str(path))
        assert not image.isNull()
        assert image.width() >= 1000
        if dim == 2:
            assert not dialog.plot.getAxis("bottom").grid
            assert dialog.plot.viewRange() == before
        else:
            assert not dialog.ax._draw_grid
            assert dialog.get_axis_limits() == before
            assert (dialog.ax.elev, dialog.ax.azim) == (30, 60)
        widget.set_grid(True, 0)
        with pytest.raises(OSError):
            widget.export_png(str(tmp_path / "missing" / "plot.png"))
    finally:
        widget.close()


def test_step_button_advances_from_history_and_stop_exports(app, tmp_path, monkeypatch):
    monkeypatch.setattr("pymoo_gui.app.results_root", lambda: tmp_path)
    window = MainWindow()
    window.problem_combo.setCurrentIndex(window.problem_combo.findData("schaffer"))
    window.alg_combo.setCurrentIndex(window.alg_combo.findData("nsga2"))
    window.alg_form.binding("pop_size").widget.setValue(12)
    worker = None
    try:
        window.step_run_btn.click()
        worker = window._thread
        wait_until(app, lambda: window._plot_generation == 1)
        window.step_run_btn.click()
        wait_until(app, lambda: window._plot_generation == 2)
        window.previous_epoch_btn.click()
        window.step_run_btn.click()
        wait_until(app, lambda: window._plot_generation == 3)
        window.stop_btn.click()
        wait_until(app, lambda: window._thread is None)
        assert window.step_run_btn.isEnabled()
        assert list(tmp_path.glob("metrics_tables/*.xlsx"))
        assert list(tmp_path.glob("solution_tables/*.xlsx"))
    finally:
        if worker is not None:
            worker.request_cancel()
            assert worker.wait(5000)
        app.processEvents()
        window.close()


def test_closing_window_wakes_paused_worker(app, tmp_path, monkeypatch):
    monkeypatch.setattr("pymoo_gui.app.results_root", lambda: tmp_path)
    window = MainWindow()
    window.problem_combo.setCurrentIndex(window.problem_combo.findData("schaffer"))
    window.alg_combo.setCurrentIndex(window.alg_combo.findData("nsga2"))
    window.alg_form.binding("pop_size").widget.setValue(12)
    window.step_run_btn.click()
    worker = window._thread
    try:
        wait_until(app, lambda: window._plot_generation == 1)
        window.close()
        wait_until(app, lambda: not worker.isRunning() and window._thread is None)
        assert worker._cancel_pending()
    finally:
        worker.request_cancel()
        assert worker.wait(5000)
        app.processEvents()
        window.close()


def test_default_window_is_square_and_console_is_shallow(app):
    window = MainWindow()
    window.show()
    try:
        app.processEvents()
        assert window.width() == window.height()
        assert window.console_dock.height() <= 160
        assert window.console_dock.height() < window.height() * 0.15
    finally:
        window.close()
