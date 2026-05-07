"""
EN: Threaded pymoo runner and debug callback utilities for optimization progress.
"""

# ------------------------------------------------------------------------------------
# File: runner.py
# Contents: threaded optimization runner, pymoo callback bridge and generation debug utilities.
# What happens here: pymoo minimize is executed in a QThread and generation payloads are emitted to the GUI.
# Role in the framework: separates optimization execution from the interface in the dissertation framework.
# Author: mgr inż. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass
import random
import traceback
from typing import Any, Dict, Optional

import numpy as np
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from pymoo.core.callback import Callback
from pymoo.optimize import minimize


def _log_generation_debug(
    gen: Optional[int],
    pop_F: Optional[np.ndarray],
    front_F: Optional[np.ndarray],
    log_every: int = 10,
) -> None:
    """
    EN:
    Print lightweight diagnostics about population and nondominated-front shapes.

    PL:
    Wypisuje proste informacje diagnostyczne o populacji i froncie niezdominowanym.
    """
    try:
        gen_val = int(gen) if gen is not None else None
    except Exception:
        gen_val = None
    if gen_val is None:
        return
    if log_every and gen_val != 1 and gen_val % int(log_every) != 0:
        return

    pop_arr = np.asarray(pop_F) if pop_F is not None else None
    front_arr = np.asarray(front_F) if front_F is not None else None

    def _dims(arr: Optional[np.ndarray]) -> str:
        """
        EN:
        Format an array shape for debug output.

        PL:
        Zamienia rozmiar tablicy na krotki tekst do logu.
        """
        if arr is None:
            return "None"
        try:
            if arr.ndim == 1:
                return f"({arr.shape[0]},)"
            if arr.ndim >= 2:
                return f"({arr.shape[0]},{arr.shape[1]})"
            return str(arr.shape)
        except Exception:
            return "?"

    n_pop = None
    if pop_arr is not None:
        try:
            n_pop = int(len(pop_arr))
        except Exception:
            n_pop = None
    n_front = None
    if front_arr is not None:
        try:
            n_front = int(len(front_arr))
        except Exception:
            n_front = None

    same_shape = False
    same_arrays = False
    if pop_arr is not None and front_arr is not None:
        try:
            same_shape = pop_arr.shape == front_arr.shape
            if same_shape:
                same_arrays = bool(np.allclose(pop_arr, front_arr, equal_nan=True))
        except Exception:
            same_shape = False
            same_arrays = False

    nd_ratio = None
    if pop_arr is not None and pop_arr.ndim == 2 and pop_arr.shape[0] > 0:
        try:
            from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

            nd_idx = NonDominatedSorting().do(pop_arr, only_non_dominated_front=True)
            if nd_idx is not None and len(pop_arr) > 0:
                nd_ratio = float(len(nd_idx)) / float(len(pop_arr))
        except Exception:
            nd_ratio = None

    nd_ratio_str = f"{nd_ratio:.2f}" if nd_ratio is not None else "NA"
    print(
        f"DBG gen={gen_val} pop={_dims(pop_arr)} front={_dims(front_arr)} "
        f"N_pop={n_pop} N_front={n_front} nd_ratio={nd_ratio_str} "
        f"same_shape={same_shape} same_arrays={same_arrays}"
    )
    if nd_ratio is not None and nd_ratio >= 0.999:
        print(
            "INFO: nd_ratio=1.00 -> cała populacja niezdominowana w tej generacji "
            "(możliwe przy 3+ celach / doborze)."
        )


@dataclass
class RunConfig:
    """
    EN:
    Runtime settings for `OptimizationThread`.

    PL:
    Przechowuje ustawienia pojedynczego uruchomienia optymalizacji.
    """

    seed: int = 1
    n_gen: int = 100
    verbose: bool = False
    save_history: bool = False


class _QtCallback(Callback):
    """
    EN:
    Bridge from pymoo callbacks to a Qt-compatible generation handler.

    PL:
    Przekazuje stan algorytmu z pymoo do funkcji, ktora moze wyslac sygnal Qt.
    """

    """
    Callback pymoo -> sygnał Qt. Dostajesz stan algorytmu na każdą generację.
    Pymoo przewiduje taki mechanizm (Callback.notify).
    """

    def __init__(self, on_generation):
        """
        EN:
        Store the callable invoked for each generation.

        PL:
        Zapamietuje funkcje wywolywana po kazdej generacji.
        """
        super().__init__()
        self._on_generation = on_generation

    def notify(self, algorithm):
        """
        EN:
        Read objective values from the population and call the GUI handler.

        PL:
        Pobiera wartosci funkcji celu z populacji i przekazuje je dalej.
        """
        # Populacja w przestrzeni celów
        try:
            F = algorithm.pop.get("F")
        except Exception:
            F = None
        self._on_generation(algorithm, F)


class OptimizationThread(QThread):
    """
    EN:
    QThread wrapper that runs `pymoo.optimize.minimize` and emits progress signals.

    PL:
    Watek Qt, ktory wykonuje optymalizacje poza glownym oknem, aby aplikacja nie
    zawieszala sie podczas obliczen.
    """

    """
    Uruchamia optimize.minimize w wątku, emituje postęp do GUI.
    """
    generation = pyqtSignal(object)      # payload: dict
    done = pyqtSignal(object)            # payload: dict
    failed = pyqtSignal(str)             # payload: error str

    def __init__(self, problem: Any, algorithm: Any, config: RunConfig, parent: Optional[QObject] = None):
        """
        EN:
        Store the problem, algorithm and run configuration for background execution.

        PL:
        Zapamietuje problem, algorytm i ustawienia potrzebne do pracy w tle.
        """
        super().__init__(parent)
        self.problem = problem
        self.algorithm = algorithm
        self.config = config

    def run(self) -> None:
        """
        EN:
        Execute pymoo minimization, emit generation payloads and report final status.

        PL:
        Uruchamia obliczenia, wysyla postep po generacjach i zwraca wynik albo blad.
        """
        try:
            random.seed(int(self.config.seed))
            np.random.seed(int(self.config.seed))
            gen_counter = 0

            def _front_from_population(pop_F, CV):
                """
                EN:
                Compute a feasible nondominated front from population objectives.

                PL:
                Wybiera z populacji wykonalne rozwiazania niezdominowane.
                """
                if pop_F is None:
                    return None
                arr = np.asarray(pop_F)
                if arr.ndim != 2 or arr.shape[0] == 0:
                    return None

                pop_feas = arr
                if CV is not None:
                    try:
                        cv_arr = np.asarray(CV)
                        if cv_arr.ndim == 1:
                            mask = cv_arr <= 0
                        elif cv_arr.ndim == 2:
                            mask = cv_arr.sum(axis=1) <= 0
                        else:
                            mask = None
                        if mask is not None:
                            filtered = arr[mask]
                            if filtered.size > 0:
                                pop_feas = filtered
                    except Exception:
                        pass

                try:
                    from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

                    nds = NonDominatedSorting()
                    nd_idx = nds.do(pop_feas, only_non_dominated_front=True)
                    if nd_idx is None:
                        return None
                    return pop_feas[nd_idx]
                except Exception:
                    return None

            def _on_gen(algo, F):
                """
                EN:
                Build and emit one progress payload from the running algorithm.

                PL:
                Tworzy pakiet danych z jednej generacji i wysyla go do GUI.
                """
                nonlocal gen_counter
                pop_F = None
                front_F = None
                pop_CV = None
                opt_F = None
                opt_CV = None
                try:
                    pop_F = algo.pop.get("F")
                except Exception:
                    pop_F = None
                try:
                    pop_CV = algo.pop.get("CV")
                except Exception:
                    pop_CV = None
                try:
                    if getattr(algo, "opt", None) is not None:
                        opt_F = algo.opt.get("F")
                        opt_CV = algo.opt.get("CV")
                except Exception:
                    opt_F = None
                    opt_CV = None
                try:
                    front_F = _front_from_population(pop_F, pop_CV)
                except Exception:
                    front_F = None

                n_gen = getattr(algo, "n_gen", None)
                try:
                    n_gen = int(n_gen) if n_gen is not None else None
                except Exception:
                    n_gen = None
                if n_gen is None or n_gen <= 0:
                    gen_counter += 1
                    n_gen = gen_counter
                else:
                    if n_gen > gen_counter:
                        gen_counter = n_gen
                total = int(self.config.n_gen)
                if n_gen > total:
                    n_gen = total

                _log_generation_debug(n_gen, pop_F, front_F)

                payload = {
                    "gen": n_gen,
                    "n_gen_total": int(self.config.n_gen),
                    "n_gen": n_gen,
                    "n_eval": getattr(getattr(algo, "evaluator", None), "n_eval", None),
                    "pop_F": np.asarray(pop_F) if pop_F is not None else None,
                    "front_F": np.asarray(front_F) if front_F is not None else None,
                    "pop_CV": np.asarray(pop_CV) if pop_CV is not None else None,
                    "F": None,
                    "CV": None,
                }
                if opt_F is not None and np.asarray(opt_F).size > 0:
                    payload["F"] = np.asarray(opt_F)
                    if opt_CV is not None:
                        payload["CV"] = np.asarray(opt_CV)
                elif front_F is not None and np.asarray(front_F).size > 0:
                    payload["F"] = np.asarray(front_F)
                elif pop_F is not None:
                    payload["F"] = np.asarray(pop_F)
                    if pop_CV is not None:
                        payload["CV"] = np.asarray(pop_CV)
                self.generation.emit(payload)

            cb = _QtCallback(_on_gen)

            res = minimize(
                self.problem,
                self.algorithm,
                termination=("n_gen", int(self.config.n_gen)),
                seed=int(self.config.seed),
                verbose=bool(self.config.verbose),
                save_history=bool(self.config.save_history),
                callback=cb,
            )

            out = {
                "X": getattr(res, "X", None),
                "F": getattr(res, "F", None),
                "pop_F": None,
                "front_F": None,
                "pop_CV": None,
                "gen": None,
                "n_gen": None,
                "res": res,
            }
            try:
                n_gen = getattr(getattr(res, "algorithm", None), "n_gen", None)
                if n_gen is None:
                    n_gen = int(self.config.n_gen)
                n_gen = int(n_gen) if n_gen is not None else None
            except Exception:
                n_gen = int(self.config.n_gen)
            if n_gen is not None and n_gen > int(self.config.n_gen):
                n_gen = int(self.config.n_gen)
            out["n_gen"] = n_gen
            out["gen"] = out.get("n_gen")
            try:
                pop = getattr(res, "pop", None)
                if pop is not None:
                    out["pop_F"] = np.asarray(pop.get("F"))
                    out["pop_CV"] = np.asarray(pop.get("CV"))
            except Exception:
                out["pop_F"] = None
            try:
                pop = getattr(res, "pop", None)
                pop_cv = pop.get("CV") if pop is not None else None
                out["front_F"] = _front_from_population(out["pop_F"], pop_cv)
            except Exception:
                out["front_F"] = None
            if out["front_F"] is None:
                try:
                    front = getattr(res, "F", None)
                    out["front_F"] = np.asarray(front) if front is not None else None
                except Exception:
                    out["front_F"] = None
            self.done.emit(out)

        except Exception:
            self.failed.emit(traceback.format_exc())


def manual_nd_debug_run(seed: int = 1, n_gen: int = 2) -> None:
    """
    EN:
    Run a small NSGA-II debug scenario that prints nondominated-front diagnostics.

    PL:
    Uruchamia krotki test diagnostyczny, ktory pomaga sprawdzic obliczanie frontu.
    """
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.problems import get_problem

    problem = get_problem("zdt1")
    algorithm = NSGA2(pop_size=100)

    def _front_from_population(pop_F):
        """
        EN:
        Extract nondominated objective rows for the debug run.

        PL:
        Wybiera niezdominowane punkty z populacji w trybie testowym.
        """
        if pop_F is None:
            return None
        arr = np.asarray(pop_F)
        if arr.ndim != 2 or arr.shape[0] == 0:
            return None
        try:
            from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

            nd_idx = NonDominatedSorting().do(arr, only_non_dominated_front=True)
            if nd_idx is None:
                return None
            return arr[nd_idx]
        except Exception:
            return None

    def _on_generation(algo, _F):
        """
        EN:
        Print debug information for each generated population.

        PL:
        Wypisuje informacje diagnostyczne po kazdej generacji testu.
        """
        try:
            pop_F = algo.pop.get("F")
        except Exception:
            pop_F = None
        front_F = _front_from_population(pop_F)
        n_gen = getattr(algo, "n_gen", None)
        _log_generation_debug(n_gen, pop_F, front_F, log_every=1)

    minimize(
        problem,
        algorithm,
        termination=("n_gen", int(n_gen)),
        seed=int(seed),
        verbose=False,
        callback=_QtCallback(_on_generation),
    )


if __name__ == "__main__":
    manual_nd_debug_run()
