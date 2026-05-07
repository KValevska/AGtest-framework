"""
EN: Parallel problem wrapper for evaluating pymoo problem rows in threads or processes.
"""

# ------------------------------------------------------------------------------------
# File: parallel.py
# Contents: optional parallel evaluation wrapper for pymoo problems.
# What happens here: vectorized problems are evaluated row-by-row using a thread or process pool.
# Role in the framework: allows expensive objective functions to use multiple CPU workers from the GUI.
# Author: mgr inz. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations

import multiprocessing as mp
from multiprocessing.pool import ThreadPool
from typing import Any, Iterable, Sequence

import numpy as np
from pymoo.core.problem import Problem

_PROCESS_PROBLEM: Any = None


def _init_process_problem(problem: Any) -> None:
    """
    EN:
    Store a problem instance in each worker process initializer.

    PL:
    Zapamietuje problem w procesie roboczym, aby kolejne zadania mogly go uzywac.
    """
    global _PROCESS_PROBLEM
    _PROCESS_PROBLEM = problem


def _row_output(value: Any) -> np.ndarray:
    """
    EN:
    Normalize one-row pymoo evaluation output to a row vector.

    PL:
    Porzadkuje wynik obliczen jednego rozwiazania, usuwajac niepotrzebny wymiar.
    """
    arr = np.asarray(value)
    if arr.ndim > 0 and arr.shape[0] == 1:
        arr = arr[0]
    return arr


def _evaluate_problem_row(problem: Any, x: Any, return_values_of: Sequence[str]) -> dict[str, np.ndarray]:
    """
    EN:
    Evaluate one decision vector with the wrapped pymoo problem.

    PL:
    Liczy wskazane wyniki dla jednego rozwiazania.
    """
    row = np.asarray(x).reshape(1, -1)
    evaluated = problem.evaluate(
        row,
        return_values_of=list(return_values_of),
        return_as_dictionary=True,
    )
    return {key: _row_output(value) for key, value in evaluated.items() if value is not None}


def _evaluate_thread_row(args: tuple[Any, Any, Sequence[str]]) -> dict[str, np.ndarray]:
    """
    EN:
    Thread-pool worker entry point with the problem passed in each task.

    PL:
    Funkcja robocza dla watkow, gdzie problem jest przekazywany razem z zadaniem.
    """
    problem, x, return_values_of = args
    return _evaluate_problem_row(problem, x, return_values_of)


def _evaluate_process_row(args: tuple[Any, Sequence[str]]) -> dict[str, np.ndarray]:
    """
    EN:
    Process-pool worker entry point using the initialized global problem.

    PL:
    Funkcja robocza dla procesow, korzystajaca z problemu zapamietanego w procesie.

    Raises:
        RuntimeError: EN: If the process initializer did not set the problem.
                      PL: Gdy proces roboczy nie zostal poprawnie przygotowany.
    """
    x, return_values_of = args
    if _PROCESS_PROBLEM is None:
        raise RuntimeError("Process worker problem was not initialized.")
    return _evaluate_problem_row(_PROCESS_PROBLEM, x, return_values_of)


class ParallelProblem(Problem):
    """
    EN:
    pymoo `Problem` wrapper that evaluates each row through a worker pool.

    PL:
    Opakowuje problem tak, aby wiele rozwiazan moglo byc ocenianych rownolegle.
    """

    def __init__(self, problem: Any, workers: int, backend: str = "process"):
        """
        EN:
        Initialize a parallel evaluation wrapper and its worker pool.

        PL:
        Przygotowuje problem do rownoleglego liczenia oraz tworzy pule watkow albo procesow.

        Raises:
            ValueError: EN: If worker count or backend name is invalid.
                        PL: Gdy liczba workerow albo typ backendu jest niepoprawny.
        """
        workers = int(workers)
        if workers < 1:
            raise ValueError(f"parallel_workers must be >= 1, got {workers}")
        backend = str(backend).strip().lower()
        if backend not in {"process", "thread"}:
            raise ValueError(f"Unsupported parallel backend: {backend!r}")

        super().__init__(
            n_var=int(getattr(problem, "n_var")),
            n_obj=int(getattr(problem, "n_obj")),
            n_ieq_constr=int(getattr(problem, "n_ieq_constr", getattr(problem, "n_constr", 0)) or 0),
            n_eq_constr=int(getattr(problem, "n_eq_constr", 0) or 0),
            xl=getattr(problem, "xl", None),
            xu=getattr(problem, "xu", None),
            vtype=getattr(problem, "vtype", None),
            replace_nan_values_by=getattr(problem, "replace_nan_values_by", None),
            strict=bool(getattr(problem, "strict", True)),
        )
        self.problem = problem
        self.parallel_workers = workers
        self.parallel_backend = backend
        self.data = dict(getattr(problem, "data", {}) or {})
        self._pool = self._make_pool()

    def _make_pool(self) -> Any:
        """
        EN:
        Create a thread or process pool according to the selected backend.

        PL:
        Tworzy pule watkow albo procesow wybrana w ustawieniach GUI.
        """
        if self.parallel_backend == "thread":
            return ThreadPool(processes=self.parallel_workers)
        context = mp.get_context("spawn")
        return context.Pool(
            processes=self.parallel_workers,
            initializer=_init_process_problem,
            initargs=(self.problem,),
        )

    def __getattr__(self, name: str) -> Any:
        """
        EN:
        Delegate unknown attributes to the wrapped problem.

        PL:
        Gdy opakowanie nie ma danego pola, pobiera je z oryginalnego problemu.
        """
        return getattr(self.problem, name)

    def _map_rows(self, X: np.ndarray, return_values_of: Sequence[str]) -> Iterable[dict[str, np.ndarray]]:
        """
        EN:
        Dispatch all decision-vector rows to the selected worker pool.

        PL:
        Rozdziela wiersze populacji miedzy watki albo procesy robocze.
        """
        if self.parallel_backend == "thread":
            tasks = ((self.problem, x, return_values_of) for x in X)
            return self._pool.map(_evaluate_thread_row, tasks)
        tasks = ((x, return_values_of) for x in X)
        return self._pool.map(_evaluate_process_row, tasks)

    def _evaluate(self, X: np.ndarray, out: dict[str, Any], *args: Any, **kwargs: Any) -> None:
        """
        EN:
        Evaluate a batch row-by-row and assemble pymoo output arrays.

        PL:
        Liczy cala populacje wiersz po wierszu i sklada wyniki z powrotem do formatu pymoo.

        Raises:
            ValueError: EN: If extra evaluation arguments are supplied.
                        PL: Gdy wywolanie zawiera dodatkowe argumenty, ktorych opakowanie nie obsluguje.
        """
        if args or kwargs:
            raise ValueError("ParallelProblem does not support extra evaluation args or kwargs.")

        return_values_of = tuple(out.keys())
        rows = list(self._map_rows(np.asarray(X), return_values_of))
        for key in return_values_of:
            values = [row[key] for row in rows if key in row]
            if values:
                out[key] = np.asarray(values)

    def close(self) -> None:
        """
        EN:
        Close or terminate the worker pool and release resources.

        PL:
        Zamyka pule workerow, aby po zakonczeniu obliczen nie zostawac dodatkowych procesow.
        """
        pool = getattr(self, "_pool", None)
        if pool is None:
            return
        self._pool = None
        try:
            pool.close()
            pool.join()
        except Exception:
            try:
                pool.terminate()
                pool.join()
            except Exception:
                pass


def make_parallel_problem(problem: Any, workers: int, backend: str = "process") -> ParallelProblem:
    """
    EN:
    Factory helper used by the GUI to wrap a problem for parallel evaluation.

    PL:
    Tworzy rownolegla wersje problemu na podstawie ustawien z formularza.
    """
    return ParallelProblem(problem, workers=workers, backend=backend)
