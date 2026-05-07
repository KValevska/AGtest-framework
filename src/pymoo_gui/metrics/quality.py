"""
EN: Quality indicator implementations for Pareto-front approximations produced by the GUI.
"""

# ------------------------------------------------------------------------------------
# File: quality.py
# Contents: metric result model and implementations of HV, GD, IGD, Spread, Delta and KKTPM calculations.
# What happens here: objective and decision data are normalized, filtered for feasibility and evaluated with indicators.
# Role in the framework: computes quantitative quality measures for dissertation optimization results.
# Author: mgr inż. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import numpy as np

FEASIBILITY_TOL = 1e-12
FINITE_DIFF_EPS = 1e-6

METRIC_DISPLAY_ORDER = ("hv", "igd", "gd", "igd_plus", "gd_plus", "spread", "delta", "kktpm")
METRIC_TABLE_ORDER = ("igd", "gd", "igd_plus", "gd_plus", "spread", "delta", "hv", "kktpm")
METRIC_LABELS = {
    "hv": "HV",
    "igd": "IGD",
    "gd": "GD",
    "igd_plus": "IGD+",
    "gd_plus": "GD+",
    "spread": "Spread",
    "delta": "Delta",
    "kktpm": "KKTPM",
}


@dataclass
class MetricResult:
    """
    EN:
    Container for all quality indicators computed for one generation or final run.

    PL:
    Przechowuje wartosci metryk policzonych dla jednej generacji albo wyniku koncowego.
    """

    hv: Optional[float] = None
    igd: Optional[float] = None
    gd: Optional[float] = None
    igd_plus: Optional[float] = None
    gd_plus: Optional[float] = None
    spread: Optional[float] = None
    delta: Optional[float] = None
    kktpm: Optional[float] = None
    n_obj: Optional[int] = None
    ref_point: Optional[np.ndarray] = None
    kktpm_values: Optional[np.ndarray] = None


def _safe_float(x) -> Optional[float]:
    """
    EN:
    Convert a value to `float`, returning `None` when conversion is unsafe.

    PL:
    Probuje zamienic wartosc na liczbe zmiennoprzecinkowa; przy bledzie zwraca `None`.
    """
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _as_2d(arr: Optional[np.ndarray], n_obj: Optional[int] = None) -> Optional[np.ndarray]:
    """
    EN:
    Normalize objective data to a two-dimensional matrix with optional objective-count validation.

    PL:
    Zamienia dane celow na tabele liczb i opcjonalnie sprawdza, czy ma oczekiwana
    liczbe kolumn.
    """
    if arr is None:
        return None
    try:
        data = np.asarray(arr, dtype=float)
    except (TypeError, ValueError):
        return None
    if data.ndim == 1:
        if n_obj is not None and int(n_obj) > 1:
            return None
        data = data.reshape(-1, 1)
    if data.ndim != 2 or data.shape[0] == 0:
        return None
    if n_obj is not None and int(n_obj) > 1 and data.shape[1] != int(n_obj):
        return None
    return data


def _as_decision_matrix(values: Optional[np.ndarray], n_var: Optional[int] = None) -> Optional[np.ndarray]:
    """
    EN:
    Normalize decision vectors to a two-dimensional matrix.

    PL:
    Zamienia zmienne decyzyjne na tabele, w ktorej kazdy wiersz jest jednym rozwiazaniem.
    """
    if values is None:
        return None
    try:
        data = np.asarray(values, dtype=float)
    except (TypeError, ValueError):
        return None
    if data.ndim == 1:
        data = data.reshape(1, -1)
    if data.ndim != 2 or data.shape[0] == 0:
        return None
    if n_var is not None and data.shape[1] != int(n_var):
        return None
    return data


def _finite_rows(arr: np.ndarray) -> np.ndarray:
    """
    EN:
    Keep only rows whose values are finite numbers.

    PL:
    Usuwa wiersze zawierajace `NaN` albo nieskonczonosc.
    """
    mask = np.isfinite(arr).all(axis=1)
    return arr[mask]


def _safe_solve(A: np.ndarray, b: np.ndarray) -> Optional[np.ndarray]:
    """
    EN:
    Solve a linear system, falling back to least squares for singular matrices.

    PL:
    Rozwiazuje uklad rownan; jesli jest trudny do rozwiazania dokladnie, probuje
    metody najmniejszych kwadratow.
    """
    try:
        return np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        try:
            return np.linalg.lstsq(A, b, rcond=None)[0]
        except np.linalg.LinAlgError:
            return None


def _problem_n_ieq_constr(problem: Any) -> int:
    """
    EN:
    Read the number of inequality constraints from compatible pymoo problem attributes.

    PL:
    Pobiera liczbe ograniczen nierownosciowych z problemu, niezaleznie od wersji pymoo.
    """
    for name in ("n_ieq_constr", "n_constr"):
        try:
            value = getattr(problem, name, None)
            if value is not None:
                return max(0, int(value))
        except (TypeError, ValueError):
            continue
    return 0


def _problem_bounds(problem: Any, n_var: int) -> tuple[np.ndarray, np.ndarray]:
    """
    EN:
    Return lower and upper decision-variable bounds, using infinities when missing.

    PL:
    Pobiera dolne i gorne granice zmiennych; gdy ich brakuje, zastepuje je
    nieskonczonoscia.
    """
    def _bound(name: str, fill: float) -> np.ndarray:
        """
        EN:
        Normalize one bound vector to the expected variable count.

        PL:
        Dopasowuje jedna granice zmiennych do wymaganej liczby kolumn.
        """
        value = getattr(problem, name, None)
        if value is None:
            return np.full(n_var, fill, dtype=float)
        try:
            arr = np.asarray(value, dtype=float)
        except (TypeError, ValueError):
            return np.full(n_var, fill, dtype=float)
        if arr.ndim == 0:
            return np.full(n_var, float(arr), dtype=float)
        arr = arr.reshape(-1)
        if arr.size != n_var:
            return np.full(n_var, fill, dtype=float)
        return arr

    return _bound("xl", -np.inf), _bound("xu", np.inf)


def _evaluate_fg(problem: Any, X: np.ndarray) -> Optional[tuple[np.ndarray, np.ndarray]]:
    """
    EN:
    Evaluate objective and inequality-constraint matrices for KKTPM support.

    PL:
    Liczy funkcje celu i ograniczenia potrzebne do metryki KKTPM.
    """
    try:
        F, G = problem.evaluate(X, return_values_of=["F", "G"])
    except Exception:
        try:
            F = problem.evaluate(X, return_values_of=["F"])
            G = np.empty((len(X), 0), dtype=float)
        except Exception:
            return None
    F_arr = _as_2d(F)
    if F_arr is None:
        return None
    try:
        G_arr = np.asarray(G, dtype=float)
    except (TypeError, ValueError):
        G_arr = np.empty((F_arr.shape[0], 0), dtype=float)
    if G_arr.ndim == 1:
        G_arr = G_arr.reshape(-1, 1)
    if G_arr.ndim != 2 or G_arr.shape[0] != F_arr.shape[0]:
        G_arr = np.empty((F_arr.shape[0], 0), dtype=float)
    return F_arr, G_arr


def _valid_derivative(values: Any, expected_shape: tuple[int, int, int]) -> Optional[np.ndarray]:
    """
    EN:
    Validate analytical derivative arrays returned by a problem.

    PL:
    Sprawdza, czy pochodne zwrocone przez problem maja poprawny ksztalt i liczby.
    """
    try:
        arr = np.asarray(values, dtype=float)
    except (TypeError, ValueError):
        return None
    if arr.shape != expected_shape or not np.isfinite(arr).all():
        return None
    return arr


def _finite_difference_derivatives(
    problem: Any,
    X: np.ndarray,
    F: np.ndarray,
    G: np.ndarray,
    eps: float = FINITE_DIFF_EPS,
) -> tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """
    EN:
    Approximate objective and constraint derivatives with finite differences.

    PL:
    Przybliza pochodne numerycznie, gdy problem nie udostepnia ich bezposrednio.
    """
    # Liczy pochodne numerycznie, gdy problem nie daje dF/dG.
    n_solutions, n_var = X.shape
    n_obj = F.shape[1]
    n_ieq = G.shape[1] if G.ndim == 2 else 0
    dF = np.empty((n_solutions, n_obj, n_var), dtype=float)
    dG = np.empty((n_solutions, n_ieq, n_var), dtype=float)
    xl, xu = _problem_bounds(problem, n_var)

    for i in range(n_solutions):
        x = X[i].astype(float, copy=True)
        for j in range(n_var):
            h = float(eps) * max(1.0, abs(float(x[j])))
            lo = xl[j]
            hi = xu[j]
            can_plus = not np.isfinite(hi) or x[j] + h <= hi
            can_minus = not np.isfinite(lo) or x[j] - h >= lo

            if can_plus and can_minus:
                xp = x.copy()
                xm = x.copy()
                xp[j] += h
                xm[j] -= h
                plus = _evaluate_fg(problem, xp.reshape(1, -1))
                minus = _evaluate_fg(problem, xm.reshape(1, -1))
                if plus is None or minus is None:
                    return None, None
                dF[i, :, j] = (plus[0][0] - minus[0][0]) / (2.0 * h)
                if n_ieq:
                    dG[i, :, j] = (plus[1][0] - minus[1][0]) / (2.0 * h)
            elif can_plus:
                xp = x.copy()
                xp[j] += h
                plus = _evaluate_fg(problem, xp.reshape(1, -1))
                if plus is None:
                    return None, None
                dF[i, :, j] = (plus[0][0] - F[i]) / h
                if n_ieq:
                    dG[i, :, j] = (plus[1][0] - G[i]) / h
            elif can_minus:
                xm = x.copy()
                xm[j] -= h
                minus = _evaluate_fg(problem, xm.reshape(1, -1))
                if minus is None:
                    return None, None
                dF[i, :, j] = (F[i] - minus[0][0]) / h
                if n_ieq:
                    dG[i, :, j] = (G[i] - minus[1][0]) / h
            else:
                return None, None

    if not np.isfinite(dF).all() or (n_ieq and not np.isfinite(dG).all()):
        return None, None
    return dF, dG


def _evaluate_kktpm_inputs(
    X: np.ndarray,
    problem: Any,
    finite_diff_eps: float = FINITE_DIFF_EPS,
) -> Optional[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
    """
    EN:
    Collect objectives, constraints and derivatives required by the KKTPM calculation.

    PL:
    Przygotowuje wszystkie dane potrzebne do policzenia KKTPM: cele, ograniczenia
    i pochodne.
    """
    # Zbiera F, G oraz gradienty wymagane przez KKTPM.
    try:
        F, G, raw_dF, raw_dG = problem.evaluate(X, return_values_of=["F", "G", "dF", "dG"])
    except Exception:
        evaluated = _evaluate_fg(problem, X)
        if evaluated is None:
            return None
        F, G = evaluated
        raw_dF = raw_dG = None

    F_arr = _as_2d(F)
    if F_arr is None or F_arr.shape[0] != X.shape[0]:
        return None

    try:
        G_arr = np.asarray(G, dtype=float)
    except (TypeError, ValueError):
        G_arr = np.empty((X.shape[0], 0), dtype=float)
    if G_arr.ndim == 1:
        G_arr = G_arr.reshape(-1, 1)
    if G_arr.ndim != 2 or G_arr.shape[0] != X.shape[0]:
        G_arr = np.empty((X.shape[0], 0), dtype=float)

    dF = _valid_derivative(raw_dF, (X.shape[0], F_arr.shape[1], X.shape[1]))
    dG = _valid_derivative(raw_dG, (X.shape[0], G_arr.shape[1], X.shape[1]))
    if dF is None or dG is None:
        dF, dG = _finite_difference_derivatives(problem, X, F_arr, G_arr, eps=finite_diff_eps)
    if dF is None or dG is None:
        return None
    return F_arr, G_arr, dF, dG


def _calc_cv(G: np.ndarray) -> np.ndarray:
    """
    EN:
    Compute scalar constraint violation from inequality-constraint values.

    PL:
    Zamienia wartosci ograniczen na jedna liczbe pokazujaca, jak mocno rozwiazanie
    lamie ograniczenia.
    """
    if G.ndim != 2 or G.shape[1] == 0:
        return np.zeros(G.shape[0], dtype=float)
    return np.sum(np.maximum(G, 0.0), axis=1)


def compute_spread(F: np.ndarray) -> Optional[float]:
    """
    EN:
    Compute a normalized diversity spread score from objective-space distances.

    PL:
    Liczy, jak szeroko i rownomiernie rozwiazania sa rozlozone w przestrzeni celow.

    Args:
        F (np.ndarray): EN: Objective matrix.
                        PL: Tabela wartosci funkcji celu.

    Returns:
        Optional[float]: EN: Diversity score, or `None` for invalid data.
                         PL: Wartosc metryki albo `None`, gdy danych nie da sie policzyc.
    """
    A = _as_2d(F)
    if A is None:
        return None
    A = _finite_rows(A)
    if A.shape[0] == 0:
        return None
    if A.shape[0] == 1:
        return 0.0

    ranges = np.ptp(A, axis=0)
    active = ranges > 0.0
    if not np.any(active):
        return 0.0
    # Normalizacja usuwa wplyw skali poszczegolnych celow.
    normalized = np.zeros_like(A, dtype=float)
    normalized[:, active] = (A[:, active] - np.min(A[:, active], axis=0)) / ranges[active]

    # Bierzemy tylko gorny trojkat macierzy odleglosci, bez przekatnej.
    diff = normalized[:, None, :] - normalized[None, :, :]
    distances = np.sqrt(np.sum(diff * diff, axis=2))
    upper = distances[np.triu_indices(A.shape[0], k=1)]
    if upper.size == 0:
        return 0.0
    return _safe_float(np.mean(upper) / np.sqrt(float(A.shape[1])))


def compute_delta(F: np.ndarray, pareto_front: np.ndarray) -> Optional[float]:
    """
    EN:
    Compute the classical NSGA-II Delta diversity metric.

    PL:
    Liczy metryke Delta dla dwoch celow. Pokazuje, czy rozwiazania sa rowno
    rozlozone na froncie i czy dochodza do jego skrajnych punktow. Mniej znaczy lepiej.
    """
    A = _as_2d(F, n_obj=2)
    pf = _as_2d(pareto_front, n_obj=2)
    if A is None or pf is None:
        return None
    A = _finite_rows(A)
    pf = _finite_rows(pf)
    if A.shape[0] < 2 or pf.shape[0] < 2:
        return None
    if A.shape[1] != 2 or pf.shape[1] != 2:
        return None

    A = A[np.lexsort((A[:, 1], A[:, 0]))]
    pf = pf[np.lexsort((pf[:, 1], pf[:, 0]))]
    # Klasyczna Delta uzywa odstepow miedzy kolejnymi punktami frontu.
    distances = np.sqrt(np.sum(np.diff(A, axis=0) ** 2, axis=1))
    d_mean = float(np.mean(distances))
    d_first = float(np.linalg.norm(A[0] - pf[0]))
    d_last = float(np.linalg.norm(A[-1] - pf[-1]))
    numerator = d_first + d_last + float(np.sum(np.abs(distances - d_mean)))
    denominator = d_first + d_last + float((A.shape[0] - 1) * d_mean)
    if denominator <= 0.0:
        return 0.0 if numerator == 0.0 else None
    return _safe_float(numerator / denominator)


def compute_kktpm(
    X: np.ndarray,
    problem: Any,
    ideal: Optional[np.ndarray] = None,
    utopian_eps: float = 1e-4,
    rho: float = 1e-3,
    finite_diff_eps: float = FINITE_DIFF_EPS,
) -> Optional[np.ndarray]:
    """
    EN:
    Compute KKTPM for decision vectors.

    PL:
    Liczy KKTPM, czyli miare bliskosci rozwiazania do warunkow optymalnosci.
    Im mniejsza wartosc, tym bardziej rozwiazanie przypomina punkt optymalny Pareto.

    Args:
        X (np.ndarray): EN: Decision-variable matrix.
                        PL: Tabela zmiennych decyzyjnych rozwiazan.
        problem (Any): EN: pymoo-like problem providing objectives and constraints.
                       PL: Problem, dla ktorego oceniane sa rozwiazania.
        ideal (Optional[np.ndarray]): EN: Optional ideal objective point.
                                      PL: Opcjonalny idealny punkt odniesienia.
        utopian_eps (float): EN: Offset applied to the ideal point.
                             PL: Male przesuniecie punktu idealnego.
        rho (float): EN: Regularization parameter in KKTPM equations.
                     PL: Parametr stabilizujacy obliczenia.
        finite_diff_eps (float): EN: Step size for finite-difference derivatives.
                                 PL: Wielkosc kroku do numerycznych pochodnych.

    Returns:
        Optional[np.ndarray]: EN: KKTPM value per solution, or `None` when unavailable.
                              PL: Wartosc KKTPM dla kazdego rozwiazania albo `None`.
    """
    try:
        n_var = int(getattr(problem, "n_var"))
        n_obj = int(getattr(problem, "n_obj"))
    except (TypeError, ValueError, AttributeError):
        return None
    if n_var <= 0 or n_obj <= 0 or not callable(getattr(problem, "evaluate", None)):
        return None

    X_arr = _as_decision_matrix(X, n_var=n_var)
    if X_arr is None or not np.isfinite(X_arr).all():
        return None

    inputs = _evaluate_kktpm_inputs(X_arr, problem, finite_diff_eps=finite_diff_eps)
    if inputs is None:
        return None
    F, G, dF, dG = inputs
    if F.shape[1] != n_obj:
        return None

    if ideal is None:
        try:
            ideal = problem.ideal_point()
        except Exception:
            ideal = np.min(F, axis=0)
    try:
        z = np.asarray(ideal, dtype=float).reshape(-1)
    except (TypeError, ValueError):
        return None
    if z.size != n_obj or not np.isfinite(z).all():
        z = np.min(F, axis=0)
    z = z.astype(float, copy=True) - float(utopian_eps)

    n_ieq_constr = min(_problem_n_ieq_constr(problem), G.shape[1])
    values = np.full(X_arr.shape[0], np.inf, dtype=float)
    # Dla punktow niewykonalnych KKTPM zwraca kare 1 + CV.
    cv = _calc_cv(G[:, :n_ieq_constr])

    for i in range(X_arr.shape[0]):
        if cv[i] > 0:
            values[i] = 1.0 + float(cv[i])
            continue

        f = F[i]
        df = dF[i].swapaxes(1, 0)
        denom = f - z
        tiny = np.finfo(float).eps
        denom = np.where(np.abs(denom) < tiny, tiny, denom)
        w = np.sqrt(np.sum(np.power(f - z, 2))) / denom
        a_m = (df * w + (float(rho) * np.sum(df * w, axis=1))[:, None]).T

        A = np.ones((n_obj, n_obj), dtype=float) + a_m @ a_m.T
        b = np.ones(n_obj, dtype=float)
        g = np.empty(0, dtype=float)
        a_j = np.empty((0, X_arr.shape[1]), dtype=float)

        if n_ieq_constr > 0:
            g = G[i, :n_ieq_constr]
            dg = dG[i, :n_ieq_constr, :].T
            a_j = dg.T
            gsq = np.zeros((n_ieq_constr, n_ieq_constr), dtype=float)
            np.fill_diagonal(gsq, g * g)
            A = np.vstack([np.hstack([A, a_m @ a_j.T]), np.hstack([a_j @ a_m.T, a_j @ a_j.T + gsq])])
            b = np.hstack([b, np.zeros(n_ieq_constr, dtype=float)])

        u = _safe_solve(A, b)
        if u is None or not np.isfinite(u).all():
            continue

        # Ujemne mnozniki Lagrange'a sa zerowane i uklad jest rozwiazywany ponownie.
        for _ in range(len(u) + 1):
            if not np.any(u < 0):
                break
            neg_idx = int(np.flatnonzero(u < 0)[0])
            A[neg_idx, :] = 0.0
            A[:, neg_idx] = 0.0
            A[neg_idx, neg_idx] = 1.0
            b[neg_idx] = 0.0
            u = _safe_solve(A, b)
            if u is None or not np.isfinite(u).all():
                break
        if u is None or not np.isfinite(u).all():
            continue

        u_m = u[:n_obj]
        u_j = u[n_obj:]
        if n_ieq_constr > 0:
            kktpm = (1.0 - np.sum(u_m)) ** 2 + np.sum((np.vstack([a_m, a_j]).T @ u) ** 2)
            fval = kktpm + np.sum((u_j * g.T) ** 2)
            ujgj = -g @ u_j
            if np.sum(u_m) + ujgj * (1.0 + ujgj) > 1.0:
                adjusted_kktpm = -(u_j @ g.T)
                projected_kktpm = (kktpm * g @ g.T - g @ u_j) / (1.0 + g @ g.T)
                kktpm = (kktpm + adjusted_kktpm + projected_kktpm) / 3.0
            values[i] = float(kktpm if np.isfinite(kktpm) else fval)
        else:
            values[i] = float((1.0 - np.sum(u_m)) ** 2 + np.sum((a_m.T @ u_m) ** 2))

    return values


def _feasibility_mask_from_cv(cv: Optional[np.ndarray]) -> Optional[np.ndarray]:
    """
    EN:
    Convert constraint-violation data to a boolean feasible-row mask.

    PL:
    Tworzy maske rozwiazan, ktore spelniaja ograniczenia.
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


def compute_metrics(
    F: np.ndarray,
    pareto_front: Optional[np.ndarray],
    cv: Optional[np.ndarray] = None,
    ref_point: Optional[np.ndarray] = None,
    n_obj: Optional[int] = None,
    X: Optional[np.ndarray] = None,
    problem: Any = None,
    kktpm_ideal: Optional[np.ndarray] = None,
    delta_supported: bool = False,
) -> MetricResult:
    """
    EN:
    Compute GD, IGD, GD+, IGD+, Spread, Delta, HV and optionally KKTPM.

    PL:
    Liczy zestaw metryk jakosci wynikow. Czesc z nich porownuje wynik ze znanym
    frontem Pareto, HV uzywa punktu odniesienia, a KKTPM wymaga takze zmiennych
    decyzyjnych i problemu.

    Args:
        F (np.ndarray): EN: Objective matrix for evaluated solutions.
                        PL: Wartosci funkcji celu dla rozwiazan.
        pareto_front (Optional[np.ndarray]): EN: Known reference Pareto front.
                                             PL: Znany front Pareto do porownania.
        cv (Optional[np.ndarray]): EN: Constraint-violation values.
                                   PL: Informacje o naruszeniu ograniczen.
        ref_point (Optional[np.ndarray]): EN: Hypervolume reference point.
                                          PL: Punkt odniesienia dla HV.
        n_obj (Optional[int]): EN: Expected objective count.
                               PL: Oczekiwana liczba funkcji celu.
        X (Optional[np.ndarray]): EN: Decision-variable matrix for KKTPM.
                                  PL: Zmienne decyzyjne potrzebne do KKTPM.
        problem (Any): EN: Problem instance used for KKTPM.
                       PL: Problem potrzebny do policzenia KKTPM.
        kktpm_ideal (Optional[np.ndarray]): EN: Optional ideal point for KKTPM.
                                            PL: Opcjonalny punkt idealny do KKTPM.
        delta_supported (bool): EN: Whether Delta is meaningful for this algorithm/run.
                                PL: Czy metryka Delta ma byc liczona dla tego przebiegu.

    Returns:
        MetricResult: EN: Object containing all computed or unavailable metric values.
                      PL: Obiekt z policzonymi metrykami albo pustymi polami.
    """
    A = _as_2d(F, n_obj=n_obj)
    if A is None:
        return MetricResult()

    result = MetricResult(n_obj=int(A.shape[1]))
    X_arr = None
    try:
        problem_n_var = int(getattr(problem, "n_var")) if problem is not None else None
    except (TypeError, ValueError):
        problem_n_var = None
    X_raw = _as_decision_matrix(X, n_var=problem_n_var)
    row_mask = np.ones(A.shape[0], dtype=bool)

    feas_mask = _feasibility_mask_from_cv(cv)
    feasible_empty = False
    # Wszystkie metryki liczymy tylko na wierszach wykonalnych i skonczonych.
    if feas_mask is not None and np.asarray(feas_mask).reshape(-1).shape[0] == A.shape[0]:
        feas_mask = np.asarray(feas_mask, dtype=bool).reshape(-1)
        if np.any(feas_mask):
            row_mask &= feas_mask
        else:
            feasible_empty = True
    row_mask &= np.isfinite(A).all(axis=1)
    A = A[row_mask]
    if X_raw is not None and X_raw.shape[0] == row_mask.shape[0]:
        X_arr = X_raw[row_mask]
        if X_arr.shape[0] == 0:
            X_arr = None
    elif X_raw is not None:
        X_arr = X_raw

    if A.shape[0] == 0:
        return result

    # Spread nie wymaga znanego frontu Pareto.
    result.spread = compute_spread(A)

    pf = _as_2d(pareto_front, n_obj=n_obj)
    if pf is not None:
        pf = _finite_rows(pf)
        if pf.shape[0] == 0:
            pf = None

    if bool(delta_supported) and pf is not None and not feasible_empty:
        # Delta jest wlaczana tylko dla danych zgodnych z NSGA-II.
        result.delta = compute_delta(A, pf)

    if pf is not None and pf.shape[1] == A.shape[1] and not feasible_empty:
        try:
            from pymoo.indicators.gd import GD

            gd_val = GD(pf)(A)
            result.gd = _safe_float(gd_val)
        except Exception:
            result.gd = None
        try:
            from pymoo.indicators.gd_plus import GDPlus

            gd_plus_val = GDPlus(pf)(A)
            result.gd_plus = _safe_float(gd_plus_val)
        except Exception:
            result.gd_plus = None
        try:
            from pymoo.indicators.igd import IGD

            igd_val = IGD(pf)(A)
            result.igd = _safe_float(igd_val)
        except Exception:
            result.igd = None
        try:
            from pymoo.indicators.igd_plus import IGDPlus

            igd_plus_val = IGDPlus(pf)(A)
            result.igd_plus = _safe_float(igd_plus_val)
        except Exception:
            result.igd_plus = None

    if A.shape[1] >= 2:
        ref_arr = None
        if ref_point is not None:
            try:
                ref_arr = np.asarray(ref_point, dtype=float).reshape(-1)
                if ref_arr.size != A.shape[1]:
                    ref_arr = None
            except Exception:
                ref_arr = None
        if ref_arr is not None:
            try:
                from pymoo.indicators.hv import HV

                result.ref_point = np.asarray(ref_arr, dtype=float)
                hv_val = HV(ref_point=ref_arr)(A)
                result.hv = _safe_float(hv_val)
            except Exception:
                result.hv = None

    if X_arr is not None and problem is not None:
        ideal = kktpm_ideal
        if ideal is None and pf is not None and pf.shape[1] == A.shape[1]:
            ideal = np.min(pf, axis=0)
        kktpm_values = compute_kktpm(X_arr, problem, ideal=ideal)
        if kktpm_values is not None:
            finite_values = kktpm_values[np.isfinite(kktpm_values)]
            result.kktpm_values = kktpm_values
            if finite_values.shape[0] > 0:
                result.kktpm = _safe_float(np.mean(finite_values))

    return result


def get_hv_ref_point(problem_name: Optional[str], n_obj: Optional[int]) -> Optional[np.ndarray]:
    """
    EN:
    Return a fixed HV reference point for a problem and objective count.

    PL:
    Zwraca domyslny punkt odniesienia do metryki HV dla danego problemu i liczby celow.
    """
    if problem_name is None or n_obj is None:
        return None
    try:
        n_obj = int(n_obj)
    except (TypeError, ValueError):
        return None
    if n_obj <= 0:
        return None
    if problem_name == "DTLZ1" and n_obj == 3:
        # DTLZ1 PF lies roughly on f1+f2+f3=0.5, with objectives in [0, 0.5].
        return np.array([0.6, 0.6, 0.6], dtype=float)
    return np.full(n_obj, 1.1, dtype=float)


def fixed_ref_point_for_problem(problem_name: Optional[str], n_obj: Optional[int]) -> Optional[np.ndarray]:
    """
    EN:
    Backward-compatible alias for `get_hv_ref_point`.

    PL:
    Druga nazwa tej samej funkcji, zostawiona dla zgodnosci z reszta kodu.
    """
    return get_hv_ref_point(problem_name, n_obj)
