"""Opt-in integration check run inside the actual standalone executable."""

import json
from pathlib import Path
import socket
import sys
import traceback
from zipfile import ZipFile


def _offline_socket(*args, **kwargs):
    raise RuntimeError("Network access is disabled during the standalone self-test")


def main(args: list[str]) -> int:
    if len(args) != 1:
        return 2
    report_path = Path(args[0]).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {"ok": False, "frozen": bool(getattr(sys, "frozen", False))}
    # Verify that normal computations and reference data do not need downloads.
    socket.socket.connect = _offline_socket
    socket.socket.connect_ex = _offline_socket
    socket.create_connection = _offline_socket
    try:
        import numpy as np
        from PyQt5.QtWidgets import QApplication
        from pymoo_gui.algorithms import ALGORITHMS
        from pymoo_gui.app import MainWindow
        from pymoo_gui.multi import (
            MultiExperimentWorker, build_multi_run_specs,
            default_entry_params, filter_callable_kwargs,
        )
        from pymoo_gui.parallel import make_parallel_problem
        from pymoo_gui.problems import PROBLEMS
        from pymoo_gui.problems import registry
        from pymoo_gui.runtime import results_root

        app = QApplication.instance() or QApplication([])
        window = MainWindow()
        window.show()
        app.processEvents()
        assert window.tabs.count() == 3
        window.close()
        report["gui"] = "passed"
        report["results_root"] = str(results_root())
        if report["frozen"]:
            assert not results_root().is_relative_to(Path(sys._MEIPASS))
            assert results_root() == Path(sys.executable).resolve().parent

        fronts = list(Path(registry.__file__).parent.glob("*.pf"))
        assert fronts, "Reference fronts are missing from the bundle"
        for front in fronts:
            assert registry._load_pf_file(front.name) is not None, front.name
        report["reference_front_files"] = len(fronts)

        for key, entry in PROBLEMS.items():
            factory = entry["factory"]
            params = filter_callable_kwargs(factory, default_entry_params(entry))
            problem = factory(**params)
            x = np.random.default_rng(1).uniform(problem.xl, problem.xu, (3, problem.n_var))
            values = problem.evaluate(x)
            if isinstance(values, tuple):
                values = values[0]
            assert np.asarray(values).shape == (3, problem.n_obj), key
        report["problem_factories"] = len(PROBLEMS)

        problem = PROBLEMS["kursawe"]["factory"]()
        x = np.random.default_rng(2).uniform(problem.xl, problem.xu, (6, problem.n_var))
        expected = problem.evaluate(x)
        for backend in ("thread", "process"):
            parallel = make_parallel_problem(problem, workers=2, backend=backend)
            try:
                np.testing.assert_allclose(parallel.evaluate(x), expected)
            finally:
                parallel.close()
        report["parallel_evaluation"] = "thread and process passed"

        completed, failures = [], []
        worker = MultiExperimentWorker(
            build_multi_run_specs(["kursawe"], list(ALGORITHMS)),
            n_gen=2, seed=1,
            project_root=results_root() if report["frozen"] else report_path.parent / "exports",
        )
        worker.done.connect(completed.append)
        worker.failed.connect(failures.append)
        worker.run()
        assert not failures, failures
        assert len(completed) == 1
        report["runs"] = completed[0]
        assert len(completed[0]) == len(ALGORITHMS)
        for result in completed[0]:
            assert result["status"] == "completed", result
            assert result["n_gen"] == 2, result
            for key in ("metrics_path", "solutions_path"):
                with ZipFile(result[key]) as workbook:
                    assert "xl/workbook.xml" in workbook.namelist()
        report["ok"] = True
    except Exception:
        report["error"] = traceback.format_exc()
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0 if report["ok"] else 1
