"""
EN: Shared generation-payload, Pareto-front and callback utilities for GUI algorithms.
"""

# ------------------------------------------------------------------------------------
# File: common.py
# Contents: generation payload schema, Pareto-front extraction and optimization callback utilities.
# What happens here: population data is normalized, feasible nondominated fronts are selected and metrics are computed.
# Role in the framework: supplies shared runtime data collection for algorithms in the doctoral-dissertation framework.
# Author: mgr inż. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations

import inspect
import logging
from typing import Any, Callable, Dict, Optional, TypedDict

import numpy as np
from pymoo.core.callback import Callback
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting
from pymoo.util.ref_dirs import get_reference_directions

from ..metrics import METRIC_TABLE_ORDER, compute_metrics


logger = logging.getLogger(__name__)
FEASIBILITY_TOL = 1e-12


class GenerationPayload(TypedDict, total=False):
    """
    EN:
    Typed dictionary describing the per-generation data emitted to the GUI.

    PL:
    Opis danych wysylanych do okna aplikacji po kazdej generacji algorytmu:
    liczby iteracji, metryki, populacje i komunikaty diagnostyczne.
    """

    n_gen: Optional[int]
    n_eval: Optional[int]
    n_nds: Optional[int]
    igd: Optional[float]
    gd: Optional[float]
    igd_plus: Optional[float]
    gd_plus: Optional[float]
    spread: Optional[float]
    delta: Optional[float]
    hv: Optional[float]
    kktpm: Optional[float]
    known_pf: Optional[np.ndarray]
    population_X: Optional[np.ndarray]
    population_F: Optional[np.ndarray]
    feasible_nd_X: Optional[np.ndarray]
    feasible_nd_F: Optional[np.ndarray]
    diagnostics: list[str]


def _safe_int(value: Optional[object]) -> Optional[int]:
    """
    EN:
    Convert a value to `int` and return `None` instead of raising on invalid input.

    PL:
    Probuje zamienic wartosc na liczbe calkowita; jesli sie nie da, zwraca `None`.
    """
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _report_issue(messages: Optional[list[str]], message: str) -> None:
    """
    EN:
    Append a diagnostic message to a list or log it when no list is available.

    PL:
    Zapisuje informacje o problemie do listy diagnostycznej albo do logu.
    """
    if messages is not None:
        messages.append(message)
    else:
        logger.warning(message)


def _record_diagnostic(messages: Optional[list[str]], context: str, exc: BaseException) -> None:
    """
    EN:
    Store exception context as a diagnostic message without interrupting the run.

    PL:
    Dodaje opis bledu do diagnostyki, zeby aplikacja mogla pokazac problem bez
    przerywania calego programu.
    """
    _report_issue(messages, f"{context}: {exc!r}")


def _pareto_front_call_kwargs(pf_fn: Any) -> Dict[str, Any]:
    """
    EN:
    Inspect a Pareto-front callable and provide compatible sampling keyword arguments.

    PL:
    Sprawdza, jakich argumentow oczekuje funkcja frontu Pareto, i dobiera
    odpowiedni sposob pobrania punktow.
    """
    sig = inspect.signature(pf_fn)
    if "ref_dirs" in sig.parameters:
        return {"ref_dirs": _default_ref_dirs(pf_fn)}
    if "n_pareto_points" in sig.parameters:
        return {"n_pareto_points": 1000}
    if "n_points" in sig.parameters:
        return {"n_points": 1000}
    return {}


def _default_ref_dirs(pf_fn: Any) -> np.ndarray:
    """
    EN:
    Generate default reference directions for Pareto-front methods requiring `ref_dirs`.

    PL:
    Tworzy domyslne kierunki odniesienia, gdy znany front Pareto wymaga takiego
    parametru.
    """
    try:
        problem = getattr(pf_fn, "__self__", None)
        n_obj = int(getattr(problem, "n_obj", None))
    except (TypeError, ValueError):
        n_obj = 3
    if n_obj < 2:
        n_obj = 2
    return get_reference_directions("das-dennis", n_obj, n_partitions=12)


def _as_objective_matrix(values: Optional[np.ndarray]) -> Optional[np.ndarray]:
    """
    EN:
    Normalize objective values to a finite two-dimensional NumPy matrix.

    PL:
    Zamienia wyniki funkcji celu na czytelna tabele liczb i usuwa wiersze z
    wartosciami nieliczbowymi.
    """
    if values is None:
        return None
    try:
        data = np.asarray(values, dtype=float)
    except (TypeError, ValueError):
        return None
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    if data.ndim != 2 or data.shape[0] == 0:
        return None
    data = data[np.isfinite(data).all(axis=1)]
    return data if data.shape[0] > 0 else None


def known_pareto_front(problem: Any, diagnostics: Optional[list[str]] = None) -> Optional[np.ndarray]:
    """
    EN:
    Retrieve and normalize the known Pareto front from a custom GUI hook or pymoo API.

    PL:
    Pobiera znany front Pareto dla problemu, aby mozna bylo porownac z nim wynik
    algorytmu i pokazac go na wykresie.

    Args:
        problem (Any): EN: Problem instance that may expose `_gui_known_pf` or `pareto_front`.
                       PL: Problem, dla ktorego szukany jest znany front Pareto.
        diagnostics (Optional[list[str]]): EN: Optional list collecting non-fatal issues.
                                           PL: Lista komunikatow o problemach, ktore nie zatrzymuja programu.

    Returns:
        Optional[np.ndarray]: EN: Finite objective matrix or `None` when unavailable.
                              PL: Tabela punktow frontu albo `None`, jesli front nie jest dostepny.
    """
    if problem is None:
        return None
    custom_pf = getattr(problem, "_gui_known_pf", None)
    if callable(custom_pf):
        try:
            pf = custom_pf()
        except (TypeError, ValueError, AttributeError) as exc:
            _record_diagnostic(diagnostics, "custom known Pareto front failed", exc)
        else:
            normalized = _as_objective_matrix(pf)
            if normalized is not None or pf is None:
                return normalized
    pf_fn = getattr(problem, "pareto_front", None)
    if pf_fn is None:
        return None
    try:
        pf = pf_fn(**_pareto_front_call_kwargs(pf_fn))
    except (TypeError, ValueError, AttributeError) as exc:
        _record_diagnostic(diagnostics, "known_pareto_front failed", exc)
        return None
    normalized = _as_objective_matrix(pf)
    if normalized is not None or pf is None:
        return normalized
    try:
        arr = np.asarray(pf)
    except (TypeError, ValueError) as exc:
        _record_diagnostic(diagnostics, "known_pareto_front returned invalid data", exc)
        return None
    _report_issue(diagnostics, f"known_pareto_front returned unsupported shape: {getattr(arr, 'shape', None)}")
    return None


def _feasibility_mask_from_cv(cv: Optional[np.ndarray]) -> Optional[np.ndarray]:
    """
    EN:
    Build a boolean mask selecting rows with constraint violation below tolerance.

    PL:
    Tworzy maske wskazujaca rozwiazania spelniajace ograniczenia problemu.
    """
    if cv is None:
        return None
    try:
        arr = np.asarray(cv, dtype=float)
    except (TypeError, ValueError):
        return None
    if arr.ndim == 1:
        return np.isfinite(arr) & (arr <= FEASIBILITY_TOL)
    if arr.ndim == 2:
        return np.isfinite(arr).all(axis=1) & np.all(arr <= FEASIBILITY_TOL, axis=1)
    return None


def _unique_rows(values: Optional[np.ndarray]) -> Optional[np.ndarray]:
    """
    EN:
    Normalize an objective matrix and keep the first occurrence of each unique row.

    PL:
    Usuwa powtarzajace sie punkty, zostawiajac pierwsze wystapienie kazdego z nich.
    """
    data = _as_objective_matrix(values)
    if data is None:
        return None
    try:
        _, first_indices = np.unique(data, axis=0, return_index=True)
    except (TypeError, ValueError):
        return data
    return data[np.sort(first_indices)]


def _feasible_nondominated_front(
    F: Optional[np.ndarray],
    CV: Optional[np.ndarray] = None,
    diagnostics: Optional[list[str]] = None,
) -> tuple[Optional[np.ndarray], Optional[int]]:
    """
    EN:
    Return the feasible nondominated objective front and its size.

    PL:
    Wybiera z populacji rozwiazania wykonalne i niezdominowane oraz zwraca ich liczbe.
    """
    front, _indices, count = _feasible_nondominated_front_with_indices(F, CV, diagnostics=diagnostics)
    return front, count


def _feasible_nondominated_front_with_indices(
    F: Optional[np.ndarray],
    CV: Optional[np.ndarray] = None,
    diagnostics: Optional[list[str]] = None,
) -> tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[int]]:
    """
    EN:
    Filter objective values by feasibility, compute nondominated points and keep source indices.

    PL:
    Z populacji wybiera poprawne, wykonalne i niezdominowane rozwiazania, a takze
    zapamietuje ich indeksy w oryginalnej populacji.

    Args:
        F (Optional[np.ndarray]): EN: Objective matrix for the population.
                                  PL: Wartosci funkcji celu calej populacji.
        CV (Optional[np.ndarray]): EN: Constraint violation values aligned with `F`.
                                   PL: Informacja o naruszeniach ograniczen.
        diagnostics (Optional[list[str]]): EN: Optional diagnostic collector.
                                           PL: Lista ostrzezen dla GUI.

    Returns:
        tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[int]]:
            EN: Nondominated front, source row indices and number of selected rows.
            PL: Front niezdominowany, indeksy w populacji i liczba punktow.
    """
    if F is None:
        return None, None, None
    try:
        raw = np.asarray(F, dtype=float)
    except (TypeError, ValueError) as exc:
        _record_diagnostic(diagnostics, "population_F conversion failed", exc)
        return None, None, None
    if raw.ndim == 1:
        raw = raw.reshape(-1, 1)
    if raw.ndim != 2 or raw.shape[0] == 0:
        _report_issue(diagnostics, f"population_F has unsupported shape: {getattr(raw, 'shape', None)}")
        return None, None, None

    # Keep index mapping while removing invalid objective rows; the GUI uses it to map F back to X.
    finite_mask = np.isfinite(raw).all(axis=1)
    raw_indices = np.flatnonzero(finite_mask)
    data = raw[finite_mask]
    if data.shape[0] == 0:
        return np.empty((0, raw.shape[1])), np.empty(0, dtype=int), 0

    feasible_mask = _feasibility_mask_from_cv(CV)
    if feasible_mask is not None:
        feasible_mask = np.asarray(feasible_mask, dtype=bool).reshape(-1)
        if feasible_mask.shape[0] == raw.shape[0]:
            feasible_mask = feasible_mask[finite_mask]
        elif feasible_mask.shape[0] != data.shape[0]:
            _report_issue(diagnostics, "CV shape is inconsistent with population_F")
            return None, None, None
        data = data[feasible_mask]
        raw_indices = raw_indices[feasible_mask]
        if data.shape[0] == 0:
            return np.empty((0, raw.shape[1])), np.empty(0, dtype=int), 0

    try:
        indices = NonDominatedSorting().do(data, only_non_dominated_front=True)
    except (TypeError, ValueError) as exc:
        _record_diagnostic(diagnostics, "NonDominatedSorting failed", exc)
        return None, None, None
    if indices is None:
        return np.empty((0, raw.shape[1])), np.empty(0, dtype=int), 0

    front = data[indices]
    selected_indices = raw_indices[indices]
    try:
        _, first_indices = np.unique(front, axis=0, return_index=True)
    except (TypeError, ValueError):
        first_indices = np.arange(front.shape[0])
    order = np.sort(first_indices)
    front = front[order]
    selected_indices = selected_indices[order]
    return front, selected_indices, int(len(front))


def _population_values(algorithm: Any) -> tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
    """
    EN:
    Read `X`, `F` and `CV` matrices from a pymoo-like algorithm population.

    PL:
    Pobiera z algorytmu zmienne decyzyjne, wartosci celow i naruszenia ograniczen.
    """
    try:
        pop = getattr(algorithm, "pop", None)
    except AttributeError:
        return None, None, None
    if pop is None:
        return None, None, None
    return pop.get("X"), pop.get("F"), pop.get("CV")


def make_generation_callback(
    on_generation: Callable[[GenerationPayload], None],
    problem: Any = None,
    hv_ref_point: Optional[list[float]] = None,
    known_pf: Optional[np.ndarray] = None,
    algorithm_key: Optional[str] = None,
) -> Callback:
    """
    EN:
    Create a pymoo callback that emits normalized generation payloads and metrics.

    PL:
    Tworzy callback, ktory po kazdej generacji zbiera dane algorytmu, liczy metryki
    i przekazuje gotowy pakiet informacji do GUI.

    Args:
        on_generation (Callable[[GenerationPayload], None]): EN: Consumer called with each payload.
                                                             PL: Funkcja odbierajaca dane generacji.
        problem (Any): EN: Problem associated with the optimization run.
                       PL: Problem, na ktorym pracuje algorytm.
        hv_ref_point (Optional[list[float]]): EN: Hypervolume reference point.
                                              PL: Punkt odniesienia dla metryki HV.
        known_pf (Optional[np.ndarray]): EN: Precomputed known Pareto front.
                                         PL: Znany front Pareto, jesli jest juz przygotowany.
        algorithm_key (Optional[str]): EN: Registry key used for algorithm-specific metric rules.
                                       PL: Klucz algorytmu potrzebny do szczegolnych zasad metryk.

    Returns:
        Callback: EN: pymoo callback object ready for `minimize`.
                  PL: Callback gotowy do przekazania funkcji optymalizacji.
    """
    static_diagnostics: list[str] = []
    if known_pf is None:
        known_pf = known_pareto_front(problem, diagnostics=static_diagnostics)
    n_obj = _safe_int(getattr(problem, "n_obj", None))
    ref_point = None
    if hv_ref_point is not None:
        try:
            ref_point = np.asarray(hv_ref_point, dtype=float).reshape(-1)
        except (TypeError, ValueError):
            ref_point = None

    class _GenCallback(Callback):
        """
        EN:
        pymoo callback implementation that emits normalized GUI generation payloads.

        PL:
        Callback pymoo, ktory po kazdej generacji przygotowuje dane zrozumiale dla GUI.
        """

        def notify(self, algorithm):
            """
            EN:
            Collect one generation snapshot from the running algorithm and emit it.

            PL:
            Zbiera stan jednej generacji: populacje, front, metryki i ostrzezenia,
            a nastepnie wysyla je do aplikacji.
            """
            diagnostics: list[str] = list(static_diagnostics)
            payload: GenerationPayload = {
                "n_gen": None,
                "n_eval": None,
                "n_nds": None,
                "igd": None,
                "gd": None,
                "igd_plus": None,
                "gd_plus": None,
                "spread": None,
                "delta": None,
                "hv": None,
                "kktpm": None,
                "known_pf": known_pf,
                "population_X": None,
                "population_F": None,
                "feasible_nd_X": None,
                "feasible_nd_F": None,
                "diagnostics": diagnostics,
            }

            try:
                payload["n_gen"] = _safe_int(getattr(algorithm, "n_gen", None))
            except (AttributeError, TypeError, ValueError) as exc:
                _record_diagnostic(diagnostics, "reading algorithm.n_gen failed", exc)

            try:
                evaluator = getattr(algorithm, "evaluator", None)
                payload["n_eval"] = _safe_int(getattr(evaluator, "n_eval", None) if evaluator is not None else None)
            except (AttributeError, TypeError, ValueError) as exc:
                _record_diagnostic(diagnostics, "reading evaluator.n_eval failed", exc)

            population_X, population_F, population_CV = _population_values(algorithm)
            try:
                X_arr = np.asarray(population_X, dtype=float) if population_X is not None else None
                if X_arr is not None and X_arr.ndim == 1:
                    X_arr = X_arr.reshape(1, -1)
                payload["population_X"] = X_arr if X_arr is not None and X_arr.ndim == 2 else None
            except (TypeError, ValueError):
                payload["population_X"] = None
            payload["population_F"] = _as_objective_matrix(population_F)
            if population_F is None:
                diagnostics.append("population_F unavailable in current generation")
            elif payload["population_F"] is None:
                diagnostics.append("population_F is invalid or empty after normalization")

            front_F, front_indices, n_nds = _feasible_nondominated_front_with_indices(
                population_F, population_CV, diagnostics=diagnostics
            )
            payload["feasible_nd_F"] = front_F
            payload["n_nds"] = _safe_int(n_nds)
            if (
                front_indices is not None
                and payload["population_X"] is not None
                and payload["population_X"].shape[0] == np.asarray(population_F).shape[0]
            ):
                try:
                    payload["feasible_nd_X"] = payload["population_X"][front_indices]
                except (IndexError, TypeError, ValueError):
                    payload["feasible_nd_X"] = None

            if payload["feasible_nd_F"] is not None:
                try:
                    metrics = compute_metrics(
                        np.asarray(payload["feasible_nd_F"]),
                        known_pf,
                        cv=None,
                        ref_point=ref_point,
                        n_obj=n_obj,
                        X=payload["feasible_nd_X"],
                        problem=problem,
                        delta_supported=str(algorithm_key or "").lower() == "nsga2",
                    )
                except (TypeError, ValueError, ArithmeticError) as exc:
                    _record_diagnostic(diagnostics, "compute_metrics failed", exc)
                else:
                    for key in METRIC_TABLE_ORDER:
                        value = getattr(metrics, key, None)
                        payload[key] = float(value) if value is not None else None

            on_generation(payload)

    return _GenCallback()
