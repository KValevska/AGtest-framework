# Batch execution support for Cartesian algorithm/problem experiments.

from __future__ import annotations

import inspect
import json
import math
import threading
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

from . import __version__
from .algorithms import (
    ALGORITHMS,
    AlgorithmProblemCompatibilityError,
    make_generation_callback,
    minimize,
    validate_algorithm_problem,
)
from .metrics import (
    METRIC_LABELS,
    METRIC_TABLE_ORDER,
    build_run_id,
    experiment_configuration_table_data,
    git_commit_for_path,
    resolve_hv_config,
    metrics_export_path,
    next_available_export_path,
    runtime_dependency_versions,
    solutions_export_path,
    write_xlsx_workbook,
)
from .problems import PROBLEMS


@dataclass(frozen=True)
class MultiRunSpec:
    # Describe one item in a Cartesian Multi experiment.

    problem_key: str
    algorithm_key: str
    problem_name: str
    algorithm_name: str


class MultiExperimentCancelled(Exception):
    # Signal cooperative cancellation of a Multi experiment.

    pass


def default_entry_params(entry: Mapping[str, Any]) -> dict[str, Any]:
    # Resolve independent copies of callable defaults and registry form-field overrides.
    params: dict[str, Any] = {}
    factory = entry.get("factory")
    if callable(factory):
        try:
            signature = inspect.signature(factory)
        except (TypeError, ValueError):
            signature = None
        if signature is not None:
            for parameter in signature.parameters.values():
                if parameter.name in {"self", "problem"}:
                    continue
                if parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
                    continue
                if parameter.default is not inspect.Signature.empty:
                    params[parameter.name] = deepcopy(parameter.default)
    raw_fields = entry.get("form_fields") or {}
    if not isinstance(raw_fields, Mapping):
        return params
    for name, raw_spec in raw_fields.items():
        if isinstance(raw_spec, Mapping) and "default" in raw_spec:
            params[str(name)] = deepcopy(raw_spec.get("default"))
        elif isinstance(raw_spec, tuple) and raw_spec:
            params[str(name)] = deepcopy(raw_spec[0])
    return params


def filter_callable_kwargs(fn: Any, params: Mapping[str, Any]) -> dict[str, Any]:
    # Keep only keyword arguments explicitly accepted by a callable.
    signature = inspect.signature(fn)
    accepted: dict[str, Any] = {}
    for param in signature.parameters.values():
        if param.name == "self" or param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue
        if param.name in params:
            accepted[param.name] = params[param.name]
    return accepted


def build_multi_run_specs(
    problem_keys: Sequence[str],
    algorithm_keys: Sequence[str],
) -> list[MultiRunSpec]:
    # Build the problem-major Cartesian product selected in the Multi tab.
    specs: list[MultiRunSpec] = []
    for problem_key in problem_keys:
        if problem_key not in PROBLEMS:
            raise KeyError(f"Unknown problem key: {problem_key}")
        problem_entry = PROBLEMS[problem_key]
        for algorithm_key in algorithm_keys:
            if algorithm_key not in ALGORITHMS:
                raise KeyError(f"Unknown algorithm key: {algorithm_key}")
            algorithm_entry = ALGORITHMS[algorithm_key]
            specs.append(
                MultiRunSpec(
                    problem_key=str(problem_key),
                    algorithm_key=str(algorithm_key),
                    problem_name=str(problem_entry.get("label", problem_key)),
                    algorithm_name=str(algorithm_entry.get("label", algorithm_key)),
                )
            )
    return specs


def metrics_table_data(history: Sequence[Mapping[str, Any]]) -> tuple[list[str], list[list[object]]]:
    # Convert generation payloads into the standard metrics workbook table.
    headers = ["n_gen", "n_eval", "n_nds", *[METRIC_LABELS[key] for key in METRIC_TABLE_ORDER]]
    rows = [
        [
            payload.get("n_gen"),
            payload.get("n_eval"),
            payload.get("n_nds"),
            *[payload.get(key) for key in METRIC_TABLE_ORDER],
        ]
        for payload in history
    ]
    return headers, rows


def hv_config_table_data(payload: Mapping[str, Any]) -> tuple[list[str], list[list[object]]]:
    config = payload.get("hv_config")
    if not isinstance(config, Mapping):
        return ["field", "value"], [["status", "unavailable"]]
    rows = []
    for key in ("mode", "source", "normalized", "n_obj", "ideal", "nadir", "raw_reference_point", "reference_point"):
        value = config.get(key)
        if isinstance(value, (list, tuple, dict)):
            value = json.dumps(value, ensure_ascii=False)
        rows.append([key, "" if value is None else value])
    return ["field", "value"], rows


def _xlsx_value(value: Any) -> object:
    # Normalize scalar values before writing them to a workbook cell.
    if value is None:
        return ""
    if isinstance(value, np.generic):
        value = value.item()
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    return numeric if math.isfinite(numeric) else ""


def solution_table_data(
    payload: Mapping[str, Any],
    n_obj: int,
) -> tuple[list[str], list[list[object]]]:
    # Convert a final nondominated front and decision matrix into a workbook table.
    expected_n_obj = max(1, int(n_obj))
    raw_f = payload.get("feasible_nd_F")
    try:
        f_raw = np.asarray(raw_f, dtype=float) if raw_f is not None else np.empty((0, expected_n_obj))
    except (TypeError, ValueError):
        f_raw = np.empty((0, expected_n_obj))
    if f_raw.size == 0:
        f_raw = np.empty((0, expected_n_obj))
    elif f_raw.ndim == 1:
        f_raw = f_raw.reshape(1, -1)
    if f_raw.ndim != 2:
        f_raw = np.empty((0, expected_n_obj))

    objective_count = f_raw.shape[1] if f_raw.shape[1] > 0 else expected_n_obj
    finite_mask = np.isfinite(f_raw).all(axis=1) if f_raw.shape[0] else np.empty(0, dtype=bool)
    f_values = f_raw[finite_mask]
    headers = ["id", *[f"f{index + 1}" for index in range(objective_count)]]

    x_values: Optional[np.ndarray] = None
    raw_x = payload.get("feasible_nd_X")
    if raw_x is not None and f_raw.shape[0] > 0:
        try:
            x_raw = np.asarray(raw_x, dtype=object)
        except (TypeError, ValueError):
            x_raw = None
        if x_raw is not None:
            if x_raw.ndim == 1 and f_raw.shape[0] == 1:
                x_raw = x_raw.reshape(1, -1)
            elif x_raw.ndim == 1 and x_raw.shape[0] == f_raw.shape[0]:
                x_raw = x_raw.reshape(-1, 1)
            if x_raw.ndim == 2 and x_raw.shape[0] == f_raw.shape[0]:
                x_values = x_raw[finite_mask]
                headers.extend(f"x{index + 1}" for index in range(x_values.shape[1]))

    rows: list[list[object]] = []
    for row_id, objectives in enumerate(f_values, start=1):
        row = [row_id, *[_xlsx_value(value) for value in objectives]]
        if x_values is not None:
            row.extend(_xlsx_value(value) for value in x_values[row_id - 1])
        rows.append(row)
    return headers, rows


class MultiExperimentWorker(QThread):
    # Execute selected problem/algorithm pairs sequentially outside the GUI thread.

    run_started = pyqtSignal(object)
    run_progress = pyqtSignal(object)
    run_finished = pyqtSignal(object)
    done = pyqtSignal(object)
    cancelled = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(
        self,
        specs: Sequence[MultiRunSpec],
        n_gen: int,
        seed: int,
        project_root: Path,
        parent=None,
    ) -> None:
        # Store the finite batch configuration and output location.
        super().__init__(parent)
        if int(n_gen) < 1:
            raise ValueError("n_gen must be at least 1")
        self._specs = list(specs)
        self._n_gen = int(n_gen)
        self._seed = int(seed)
        self._project_root = Path(project_root)
        self._cancel_requested = threading.Event()
        self._results: list[dict[str, Any]] = []
        self._started_at = datetime.now(timezone.utc)
        self.experiment_id = build_run_id("multi", "experiment", self._seed, now=self._started_at)
        self.experiment_directory = self._project_root / "multi_experiments" / self.experiment_id
        self.manifest_path = self.experiment_directory / "experiment_manifest.json"
        self.runs_path = self.experiment_directory / "runs.xlsx"

    def _experiment_summary_configuration(self, status: str) -> dict[str, Any]:
        # Describe the complete Multi batch independently of any one combination.
        return {
            "run_id": self.experiment_id,
            "started_at_utc": self._started_at.isoformat().replace("+00:00", "Z"),
            "execution_mode": "Multi experiment",
            "framework_name": "AGtest-framework",
            "framework_version": __version__,
            "git_commit": git_commit_for_path(self._project_root),
            "random_seed": self._seed,
            "termination": "maximum generations",
            "maximum_generations": self._n_gen,
            "status": status,
            "run_parameters": {
                "combination_count": len(self._specs),
                "problem_keys": [spec.problem_key for spec in self._specs],
                "algorithm_keys": [spec.algorithm_key for spec in self._specs],
            },
            **runtime_dependency_versions(),
        }

    def _write_experiment_summary(self, status: str) -> None:
        # Persist a machine-readable manifest and a one-row-per-run workbook.
        self.experiment_directory.mkdir(parents=True, exist_ok=True)
        configuration = self._experiment_summary_configuration(status)
        manifest = {"experiment": configuration, "runs": self._results}
        temporary_manifest = self.manifest_path.with_suffix(".json.tmp")
        temporary_manifest.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        temporary_manifest.replace(self.manifest_path)

        headers = [
            "run_id",
            "problem_key",
            "problem_name",
            "algorithm_key",
            "algorithm_name",
            "status",
            "n_gen",
            "n_eval",
            "n_nds",
            "metrics_path",
            "solutions_path",
            "error",
        ]
        rows = [[result.get(field) for field in headers] for result in self._results]
        config_headers, config_rows = experiment_configuration_table_data(configuration)
        write_xlsx_workbook(
            self.runs_path,
            [("Runs", headers, rows), ("Configuration", config_headers, config_rows)],
        )

    def request_cancel(self) -> None:
        # Request cancellation after the current optimizer callback is reached.
        self._cancel_requested.set()
        self.requestInterruption()

    def _cancel_pending(self) -> bool:
        # Return whether cooperative cancellation was requested.
        return self._cancel_requested.is_set() or self.isInterruptionRequested()

    def _write_result_files(
        self,
        spec: MultiRunSpec,
        history: Sequence[Mapping[str, Any]],
        last_payload: Mapping[str, Any],
        n_obj: int,
        run_id: str,
        experiment_configuration: Mapping[str, Any],
    ) -> tuple[Optional[Path], Optional[Path], list[str]]:
        # Persist metrics history and final nondominated solutions for one run.
        errors: list[str] = []
        metrics_path = next_available_export_path(
            metrics_export_path(
                self._project_root,
                spec.algorithm_name,
                spec.problem_name,
                run_id=run_id,
            )
        )
        solutions_path = next_available_export_path(
            solutions_export_path(
                self._project_root,
                spec.algorithm_name,
                spec.problem_name,
                run_id=run_id,
            )
        )
        metric_headers, metric_rows = metrics_table_data(history)
        config_headers, config_rows = hv_config_table_data(last_payload)
        experiment_headers, experiment_rows = experiment_configuration_table_data(
            experiment_configuration
        )
        solution_headers, solution_rows = solution_table_data(last_payload, n_obj=n_obj)
        try:
            write_xlsx_workbook(
                metrics_path,
                [
                    ("Metrics", metric_headers, metric_rows),
                    ("Configuration", experiment_headers, experiment_rows),
                    ("HV Configuration", config_headers, config_rows),
                ],
            )
        except Exception as exc:
            errors.append(f"Metrics export failed: {exc!r}")
            metrics_path = None
        try:
            write_xlsx_workbook(
                solutions_path,
                [
                    ("Solutions", solution_headers, solution_rows),
                    ("Configuration", experiment_headers, experiment_rows),
                ],
            )
        except Exception as exc:
            errors.append(f"Solutions export failed: {exc!r}")
            solutions_path = None
        return metrics_path, solutions_path, errors

    def _execute_spec(self, spec: MultiRunSpec, index: int, total: int) -> dict[str, Any]:
        # Execute and export one problem/algorithm combination.
        started_at = datetime.now(timezone.utc)
        run_id = build_run_id(spec.algorithm_key, spec.problem_key, self._seed, now=started_at)
        problem_params = default_entry_params(PROBLEMS[spec.problem_key])
        algorithm_params = default_entry_params(ALGORITHMS[spec.algorithm_key])
        algorithm_entry = ALGORITHMS[spec.algorithm_key]
        experiment_configuration = {
            "run_id": run_id,
            "started_at_utc": started_at.isoformat().replace("+00:00", "Z"),
            "execution_mode": "Multi",
            "framework_name": "AGtest-framework",
            "framework_version": __version__,
            "git_commit": git_commit_for_path(self._project_root),
            "problem_key": spec.problem_key,
            "problem_name": spec.problem_name,
            "algorithm_key": spec.algorithm_key,
            "algorithm_name": spec.algorithm_name,
            "random_seed": self._seed,
            "termination": "maximum generations",
            "maximum_generations": self._n_gen,
            "step_mode": False,
            "hv_mode": "auto",
            "hv_reference_point": None,
            "hv_source": None,
            "hv_normalized": None,
            "hv_ideal": None,
            "hv_nadir": None,
            "hv_raw_reference_point": None,
            "hv_effective_reference_point": None,
            "nondominated_export_mode": "final epoch",
            "nondominated_export_step": 1,
            "verbose": False,
            "parallel_evaluation": False,
            "parallel_workers": 1,
            "parallel_backend": "off",
            "implementation_type": algorithm_entry.get("implementation_type", "unavailable"),
            "implementation_source": algorithm_entry.get("reference", "unavailable"),
            "implementation_source_commit": algorithm_entry.get("source_commit") or "unavailable",
            "implementation_verified_against": algorithm_entry.get("verified_against", "unavailable"),
            "problem_parameters": dict(problem_params),
            "algorithm_parameters": dict(algorithm_params),
            "status": "running",
            "final_generation": None,
            "final_evaluations": None,
            **runtime_dependency_versions(),
        }
        context = {
            "run_id": run_id,
            "run_index": index,
            "total_runs": total,
            "problem_key": spec.problem_key,
            "algorithm_key": spec.algorithm_key,
            "problem_name": spec.problem_name,
            "algorithm_name": spec.algorithm_name,
        }
        self.run_started.emit(dict(context))
        history: list[dict[str, Any]] = []
        last_payload: dict[str, Any] = {}
        problem = None
        n_obj = 1
        status = "completed"
        error_message = ""
        hv_config = None

        try:
            if self._cancel_pending():
                raise MultiExperimentCancelled()
            problem_entry = PROBLEMS[spec.problem_key]
            problem_factory = problem_entry["factory"]
            problem = problem_factory(**filter_callable_kwargs(problem_factory, problem_params))
            n_obj = max(1, int(getattr(problem, "n_obj", 1)))

            known_pf = None
            known_pf_factory = problem_entry.get("known_pf_factory")
            if callable(known_pf_factory):
                known_pf = known_pf_factory(problem)

            validate_algorithm_problem(algorithm_entry, problem)
            algorithm_factory = algorithm_entry["factory"]
            runtime_algorithm_params = dict(algorithm_params)
            runtime_algorithm_params["problem"] = problem
            algorithm = algorithm_factory(
                **filter_callable_kwargs(algorithm_factory, runtime_algorithm_params)
            )

            def on_generation(payload: Mapping[str, Any]) -> None:
                # Record metrics and report lightweight progress without rendering a plot.
                nonlocal last_payload
                if self._cancel_pending():
                    raise MultiExperimentCancelled()
                last_payload = dict(payload or {})
                history.append(
                    {
                        "n_gen": last_payload.get("n_gen"),
                        "n_eval": last_payload.get("n_eval"),
                        "n_nds": last_payload.get("n_nds"),
                        **{key: last_payload.get(key) for key in METRIC_TABLE_ORDER},
                    }
                )
                progress = dict(context)
                progress.update(
                    {
                        "n_gen": last_payload.get("n_gen"),
                        "n_eval": last_payload.get("n_eval"),
                        "n_nds": last_payload.get("n_nds"),
                    }
                )
                self.run_progress.emit(progress)
                if self._cancel_pending():
                    raise MultiExperimentCancelled()

            hv_config = resolve_hv_config(spec.problem_name, n_obj, pareto_front=known_pf)
            callback = make_generation_callback(
                on_generation,
                problem=problem,
                hv_ref_point=None,
                known_pf=known_pf,
                algorithm_key=spec.algorithm_key,
                hv_config=hv_config,
            )
            minimize(
                problem,
                algorithm,
                ("n_gen", self._n_gen),
                seed=self._seed,
                verbose=False,
                callback=callback,
            )
            if self._cancel_pending():
                raise MultiExperimentCancelled()
        except MultiExperimentCancelled:
            status = "cancelled"
        except AlgorithmProblemCompatibilityError as exc:
            status = "skipped"
            error_message = str(exc)
        except Exception as exc:
            status = "failed"
            error_message = repr(exc)
        finally:
            close = getattr(problem, "close", None)
            if callable(close):
                try:
                    close()
                except Exception as exc:
                    status = "failed" if status == "completed" else status
                    close_message = f"Problem cleanup failed: {exc!r}"
                    error_message = f"{error_message}; {close_message}".strip("; ")

        experiment_configuration.update(
            {
                "status": status,
                "final_generation": last_payload.get("n_gen"),
                "final_evaluations": last_payload.get("n_eval"),
            }
        )
        if hv_config is not None:
            hv_data = hv_config.as_dict()
            experiment_configuration.update(
                {
                    "hv_source": hv_data.get("source"),
                    "hv_normalized": hv_data.get("normalized"),
                    "hv_ideal": hv_data.get("ideal"),
                    "hv_nadir": hv_data.get("nadir"),
                    "hv_raw_reference_point": hv_data.get("raw_reference_point"),
                    "hv_effective_reference_point": hv_data.get("reference_point"),
                }
            )

        if status == "skipped":
            metrics_path = solutions_path = None
            export_errors: list[str] = []
        else:
            metrics_path, solutions_path, export_errors = self._write_result_files(
                spec,
                history,
                last_payload,
                n_obj=n_obj,
                run_id=run_id,
                experiment_configuration=experiment_configuration,
            )
        if export_errors:
            status = "failed" if status == "completed" else status
            export_message = "; ".join(export_errors)
            error_message = f"{error_message}; {export_message}".strip("; ")
        experiment_configuration["status"] = status

        result = dict(context)
        result.update(
            {
                "status": status,
                "n_gen": last_payload.get("n_gen"),
                "n_eval": last_payload.get("n_eval"),
                "n_nds": last_payload.get("n_nds"),
                "metrics_path": str(metrics_path) if metrics_path is not None else "",
                "solutions_path": str(solutions_path) if solutions_path is not None else "",
                "experiment_id": self.experiment_id,
                "manifest_path": str(self.manifest_path),
                "runs_path": str(self.runs_path),
                "configuration": experiment_configuration,
                "error": error_message,
            }
        )
        self.run_finished.emit(dict(result))
        return result

    def run(self) -> None:
        # Run all combinations, preserving per-run failures and partial cancellation results.
        try:
            total = len(self._specs)
            for index, spec in enumerate(self._specs, start=1):
                if self._cancel_pending():
                    self._write_experiment_summary("cancelled")
                    self.cancelled.emit(list(self._results))
                    return
                result = self._execute_spec(spec, index, total)
                self._results.append(result)
                self._write_experiment_summary("running")
                if result.get("status") == "cancelled" or self._cancel_pending():
                    self._write_experiment_summary("cancelled")
                    self.cancelled.emit(list(self._results))
                    return
            self._write_experiment_summary("completed")
            self.done.emit(list(self._results))
        except Exception as exc:
            try:
                self._write_experiment_summary("failed")
            except Exception:
                pass
            self.failed.emit(repr(exc))
