"""
EN: Shared utilities and GUI-compatible base classes for custom research MOEAs.
"""

# ------------------------------------------------------------------------------------
# File: research_common.py
# Contents: validation helpers, NumPy-based multiobjective operators and a GUI runtime adapter.
# What happens here: custom research algorithms reuse one deterministic optimization loop and shared survival logic.
# Role in the framework: supports article-based MOEA variants not provided directly by pymoo or Platypus.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on the article.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Dict, Iterable, Optional, Sequence

import numpy as np
from pymoo.core.result import Result
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting
from pymoo.util.ref_dirs import get_reference_directions

from .platypus_common import termination_generations


FEASIBILITY_TOL = 1e-12


def parse_positive_int(value: Any, field_name: str) -> int:
    """
    EN:
    Parse a positive integer shared by research algorithm factories.

    PL:
    Sprawdza, czy parametr algorytmu jest dodatnia liczba calkowita.
    """
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def parse_optional_positive_int(value: Any, field_name: str) -> Optional[int]:
    """
    EN:
    Parse an optional positive integer while preserving `None`.

    PL:
    Odczytuje dodatnia liczbe calkowita albo zostawia `None`.
    """
    if value is None:
        return None
    return parse_positive_int(value, field_name)


def parse_positive_float(value: Any, field_name: str) -> float:
    """
    EN:
    Parse a strictly positive floating-point value.

    PL:
    Sprawdza, czy parametr jest liczba dodatnia.
    """
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed <= 0.0:
        raise ValueError(f"{field_name} must be > 0, got {parsed}")
    return parsed


def parse_probability(value: Any, field_name: str) -> float:
    """
    EN:
    Parse a probability from the inclusive interval [0, 1].

    PL:
    Sprawdza, czy parametr jest prawdopodobienstwem z zakresu od 0 do 1.
    """
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if not 0.0 <= parsed <= 1.0:
        raise ValueError(f"{field_name} must be in [0, 1], got {parsed}")
    return parsed


def parse_reference_directions(value: Any, n_obj: int) -> Optional[np.ndarray]:
    """
    EN:
    Normalize user-provided reference directions to a finite two-dimensional array.

    PL:
    Zamienia kierunki odniesienia na poprawna macierz albo zwraca `None`.
    """
    if value is None:
        return None
    arr = np.asarray(value, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    if arr.ndim != 2 or arr.shape[1] != int(n_obj):
        raise ValueError(f"reference_directions must have shape (n, {int(n_obj)})")
    if arr.shape[0] == 0 or not np.isfinite(arr).all():
        raise ValueError("reference_directions must be finite and non-empty.")
    return arr


def problem_bounds(problem: Any) -> tuple[np.ndarray, np.ndarray, int]:
    """
    EN:
    Extract finite lower and upper bounds for every problem variable.

    PL:
    Pobiera dolne i gorne granice wszystkich zmiennych decyzyjnych.
    """
    n_var = parse_positive_int(getattr(problem, "n_var", None), "n_var")
    xl = np.asarray(getattr(problem, "xl", None), dtype=float).reshape(-1)
    xu = np.asarray(getattr(problem, "xu", None), dtype=float).reshape(-1)
    if xl.size == 1:
        xl = np.repeat(xl, n_var)
    if xu.size == 1:
        xu = np.repeat(xu, n_var)
    if xl.size != n_var or xu.size != n_var:
        raise ValueError("Custom research algorithms require finite lower and upper bounds for every variable.")
    if not np.isfinite(xl).all() or not np.isfinite(xu).all():
        raise ValueError("Custom research algorithms require finite variable bounds.")
    return xl, xu, n_var


def problem_n_obj(problem: Any) -> int:
    """
    EN:
    Extract and validate the objective count of a pymoo-like problem.

    PL:
    Pobiera liczbe funkcji celu i sprawdza, czy jest poprawna.
    """
    return parse_positive_int(getattr(problem, "n_obj", None), "n_obj")


def project_to_bounds(X: np.ndarray, xl: np.ndarray, xu: np.ndarray) -> np.ndarray:
    """
    EN:
    Clip decision vectors to valid variable bounds.

    PL:
    Przycina rozwiazania do granic problemu.
    """
    return np.clip(np.asarray(X, dtype=float), np.asarray(xl, dtype=float), np.asarray(xu, dtype=float))


def evaluate_problem(problem: Any, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    EN:
    Evaluate objective values and aggregate constraint violation for a decision matrix.

    PL:
    Liczy wartosci funkcji celu oraz laczne naruszenie ograniczen dla populacji.
    """
    X = np.asarray(X, dtype=float)
    out = problem.evaluate(
        X,
        return_values_of=["F", "G", "H"],
        return_as_dictionary=True,
    )
    F = np.asarray(out.get("F"), dtype=float)
    if F.ndim == 1:
        F = F.reshape(-1, 1)
    cv = np.zeros(F.shape[0], dtype=float)

    G = out.get("G")
    if G is not None:
        G = np.asarray(G, dtype=float)
        if G.ndim == 1:
            G = G.reshape(-1, 1)
        cv += np.sum(np.maximum(G, 0.0), axis=1)

    H = out.get("H")
    if H is not None:
        H = np.asarray(H, dtype=float)
        if H.ndim == 1:
            H = H.reshape(-1, 1)
        cv += np.sum(np.abs(H), axis=1)

    return F, cv


def feasible_mask(cv: np.ndarray) -> np.ndarray:
    """
    EN:
    Return a boolean mask for feasible solutions.

    PL:
    Zwraca maske rozwiazan spelniajacych ograniczenia.
    """
    return np.asarray(cv, dtype=float) <= FEASIBILITY_TOL


def crowding_distance(F: np.ndarray) -> np.ndarray:
    """
    EN:
    Compute the classic NSGA-II crowding distance for one front.

    PL:
    Liczy klasyczny dystans crowding dla jednego frontu Pareto.
    """
    F = np.asarray(F, dtype=float)
    n_points = F.shape[0]
    if n_points == 0:
        return np.zeros(0, dtype=float)
    if n_points <= 2:
        return np.full(n_points, np.inf, dtype=float)

    distances = np.zeros(n_points, dtype=float)
    for axis in range(F.shape[1]):
        order = np.argsort(F[:, axis], kind="mergesort")
        distances[order[0]] = np.inf
        distances[order[-1]] = np.inf
        span = F[order[-1], axis] - F[order[0], axis]
        if span <= 0.0:
            continue
        distances[order[1:-1]] += (F[order[2:], axis] - F[order[:-2], axis]) / span
    return distances


def assign_rank_and_crowding(F: np.ndarray, CV: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    EN:
    Assign rank and crowding values with feasible-first handling.

    PL:
    Nadaje rangi i crowding z preferencja dla rozwiazan wykonalnych.
    """
    F = np.asarray(F, dtype=float)
    CV = np.asarray(CV, dtype=float).reshape(-1)
    n = F.shape[0]
    rank = np.full(n, np.iinfo(int).max, dtype=int)
    crowding = np.zeros(n, dtype=float)

    feasible = feasible_mask(CV)
    feasible_idx = np.flatnonzero(feasible)
    if feasible_idx.size:
        fronts = NonDominatedSorting().do(F[feasible_idx], only_non_dominated_front=False)
        for front_rank, front in enumerate(fronts):
            front = feasible_idx[np.asarray(front, dtype=int)]
            rank[front] = front_rank
            crowding[front] = crowding_distance(F[front])
        base_rank = len(fronts)
    else:
        base_rank = 0

    infeasible_idx = np.flatnonzero(~feasible)
    if infeasible_idx.size:
        order = infeasible_idx[np.argsort(CV[infeasible_idx], kind="mergesort")]
        for offset, idx in enumerate(order):
            rank[idx] = base_rank + offset
            crowding[idx] = 1.0 / (1.0 + CV[idx])

    return rank, crowding


def stable_survivor_order(rank: np.ndarray, crowding: np.ndarray, cv: np.ndarray) -> np.ndarray:
    """
    EN:
    Return a deterministic lexicographic order for survivor selection.

    PL:
    Zwraca deterministyczna kolejnosc wyboru osobnikow.
    """
    rank = np.asarray(rank, dtype=int)
    crowding = np.asarray(crowding, dtype=float)
    cv = np.asarray(cv, dtype=float)
    return np.lexsort((np.arange(rank.size), cv, -crowding, rank))


def select_survivors_nsga2(X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> "PopulationState":
    """
    EN:
    Select survivors with feasible-first non-dominated sorting and crowding distance.

    PL:
    Wybiera populacje nastepnej generacji w stylu NSGA-II.
    """
    rank, crowding = assign_rank_and_crowding(F, CV)
    order = stable_survivor_order(rank, crowding, CV)[: int(n_survive)]
    return PopulationState(
        X=np.asarray(X, dtype=float)[order],
        F=np.asarray(F, dtype=float)[order],
        CV=np.asarray(CV, dtype=float)[order],
        rank=rank[order],
        crowding=crowding[order],
    )


def tournament_indices(
    rank: np.ndarray,
    crowding: np.ndarray,
    cv: np.ndarray,
    n_parents: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """
    EN:
    Run binary tournament selection using feasibility, rank and crowding.

    PL:
    Wykonuje turniej binarny oparty o wykonalnosc, range i crowding.
    """
    n = rank.size
    parents = np.zeros((int(n_parents), 2), dtype=int)
    for i in range(int(n_parents)):
        for j in range(2):
            a, b = rng.integers(0, n, size=2)
            a_feasible = cv[a] <= FEASIBILITY_TOL
            b_feasible = cv[b] <= FEASIBILITY_TOL
            winner = int(a)
            if a_feasible and not b_feasible:
                winner = int(a)
            elif b_feasible and not a_feasible:
                winner = int(b)
            elif rank[a] < rank[b]:
                winner = int(a)
            elif rank[b] < rank[a]:
                winner = int(b)
            elif crowding[a] > crowding[b]:
                winner = int(a)
            elif crowding[b] > crowding[a]:
                winner = int(b)
            elif cv[a] < cv[b]:
                winner = int(a)
            elif cv[b] < cv[a]:
                winner = int(b)
            else:
                winner = int(a if rng.random() < 0.5 else b)
            parents[i, j] = winner
    return parents


def sbx_crossover(
    X: np.ndarray,
    parent_pairs: np.ndarray,
    xl: np.ndarray,
    xu: np.ndarray,
    eta: float,
    prob: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """
    EN:
    Apply simulated binary crossover to selected parent pairs.

    PL:
    Stosuje krzyzowanie SBX do wybranych par rodzicow.
    """
    X = np.asarray(X, dtype=float)
    xl = np.asarray(xl, dtype=float)
    xu = np.asarray(xu, dtype=float)
    children = np.zeros((parent_pairs.shape[0], X.shape[1]), dtype=float)

    for i, (a, b) in enumerate(parent_pairs):
        p1 = X[int(a)].copy()
        p2 = X[int(b)].copy()
        child = p1.copy()
        if rng.random() <= float(prob):
            for j in range(X.shape[1]):
                y1 = float(p1[j])
                y2 = float(p2[j])
                if abs(y1 - y2) <= 1e-14:
                    child[j] = y1
                    continue
                if y1 > y2:
                    y1, y2 = y2, y1
                yl = float(xl[j])
                yu = float(xu[j])
                rand = float(rng.random())
                beta = 1.0 + (2.0 * (y1 - yl) / (y2 - y1))
                alpha = 2.0 - beta ** (-(eta + 1.0))
                if rand <= 1.0 / alpha:
                    betaq = (rand * alpha) ** (1.0 / (eta + 1.0))
                else:
                    betaq = (1.0 / (2.0 - rand * alpha)) ** (1.0 / (eta + 1.0))
                c1 = 0.5 * ((y1 + y2) - betaq * (y2 - y1))

                beta = 1.0 + (2.0 * (yu - y2) / (y2 - y1))
                alpha = 2.0 - beta ** (-(eta + 1.0))
                if rand <= 1.0 / alpha:
                    betaq = (rand * alpha) ** (1.0 / (eta + 1.0))
                else:
                    betaq = (1.0 / (2.0 - rand * alpha)) ** (1.0 / (eta + 1.0))
                c2 = 0.5 * ((y1 + y2) + betaq * (y2 - y1))
                child[j] = c1 if rng.random() < 0.5 else c2
        children[i] = child

    return project_to_bounds(children, xl, xu)


def polynomial_mutation(
    X: np.ndarray,
    xl: np.ndarray,
    xu: np.ndarray,
    eta: float,
    prob: float,
    rng: np.random.Generator,
    strength: float = 1.0,
) -> np.ndarray:
    """
    EN:
    Apply polynomial mutation to a decision matrix.

    PL:
    Stosuje mutacje wielomianowa do macierzy rozwiazan.
    """
    Y = np.asarray(X, dtype=float).copy()
    xl = np.asarray(xl, dtype=float)
    xu = np.asarray(xu, dtype=float)
    strength = float(max(strength, 1e-6))

    for i in range(Y.shape[0]):
        for j in range(Y.shape[1]):
            if rng.random() > float(prob):
                continue
            y = float(Y[i, j])
            yl = float(xl[j])
            yu = float(xu[j])
            span = yu - yl
            if span <= 0.0:
                continue
            delta1 = (y - yl) / span
            delta2 = (yu - y) / span
            rand = float(rng.random())
            mut_pow = 1.0 / (eta + 1.0)
            if rand < 0.5:
                xy = 1.0 - delta1
                val = 2.0 * rand + (1.0 - 2.0 * rand) * (xy ** (eta + 1.0))
                deltaq = (val ** mut_pow - 1.0) * strength
            else:
                xy = 1.0 - delta2
                val = 2.0 * (1.0 - rand) + 2.0 * (rand - 0.5) * (xy ** (eta + 1.0))
                deltaq = (1.0 - val ** mut_pow) * strength
            Y[i, j] = np.clip(y + deltaq * span, yl, yu)
    return Y


def gaussian_mutation(
    X: np.ndarray,
    xl: np.ndarray,
    xu: np.ndarray,
    prob: float,
    sigma: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """
    EN:
    Apply Gaussian mutation scaled by the search-space span.

    PL:
    Stosuje mutacje Gaussowska skalowana zakresem zmiennych.
    """
    Y = np.asarray(X, dtype=float).copy()
    span = np.asarray(xu, dtype=float) - np.asarray(xl, dtype=float)
    sigma = float(max(sigma, 1e-6))
    mask = rng.random(size=Y.shape) <= float(prob)
    noise = rng.normal(0.0, sigma, size=Y.shape) * span[None, :]
    Y[mask] += noise[mask]
    return project_to_bounds(Y, xl, xu)


def de_crossover(
    X: np.ndarray,
    xl: np.ndarray,
    xu: np.ndarray,
    F_weight: np.ndarray,
    CR: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    """
    EN:
    Generate offspring with a basic DE/current-to-rand/1/bin operator.

    PL:
    Tworzy potomkow operatorem DE/current-to-rand/1/bin.
    """
    X = np.asarray(X, dtype=float)
    n_pop, n_var = X.shape
    children = np.zeros_like(X)
    indices = np.arange(n_pop)

    for i in range(n_pop):
        pool = np.delete(indices, i)
        r1, r2, r3 = rng.choice(pool, size=3, replace=False)
        mutant = X[r1] + F_weight[i] * (X[r2] - X[r3])
        j_rand = int(rng.integers(0, n_var))
        trial = X[i].copy()
        for j in range(n_var):
            if rng.random() <= CR[i] or j == j_rand:
                trial[j] = mutant[j]
        children[i] = trial
    return project_to_bounds(children, xl, xu)


def sample_reference_directions(
    n_obj: int,
    population_size: int,
    n_partitions: int,
    rng: np.random.Generator,
    reference_directions: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    EN:
    Prepare a usable set of reference directions for many-objective variants.

    PL:
    Przygotowuje kierunki odniesienia dla metod dekompozycyjnych.
    """
    if reference_directions is not None:
        return np.asarray(reference_directions, dtype=float)

    try:
        refs = get_reference_directions("das-dennis", int(n_obj), n_partitions=int(max(n_partitions, 1)))
    except Exception:
        refs = np.empty((0, int(n_obj)), dtype=float)

    refs = np.asarray(refs, dtype=float)
    if refs.ndim != 2 or refs.shape[1] != int(n_obj):
        refs = np.empty((0, int(n_obj)), dtype=float)

    if refs.shape[0] < int(population_size):
        extra = rng.dirichlet(np.ones(int(n_obj)), size=int(population_size) - refs.shape[0])
        refs = np.vstack([refs, extra]) if refs.size else extra
    return refs


def normalized_objectives(F: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    EN:
    Normalize objectives to [0, 1] using the current ideal and nadir points.

    PL:
    Normalizuje cele do zakresu od 0 do 1.
    """
    F = np.asarray(F, dtype=float)
    ideal = np.min(F, axis=0)
    nadir = np.max(F, axis=0)
    span = np.where(nadir > ideal, nadir - ideal, 1.0)
    return (F - ideal) / span, ideal, nadir


def associate_to_reference_directions(F: np.ndarray, ref_dirs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    EN:
    Associate each point with the closest reference direction by perpendicular distance.

    PL:
    Przypisuje kazdy punkt do najblizszego kierunku odniesienia.
    """
    Fn, _, _ = normalized_objectives(F)
    ref_dirs = np.asarray(ref_dirs, dtype=float)
    ref_norm = np.linalg.norm(ref_dirs, axis=1, keepdims=True)
    ref_unit = ref_dirs / np.where(ref_norm > 0.0, ref_norm, 1.0)
    point_norm = np.linalg.norm(Fn, axis=1, keepdims=True)
    point_unit = Fn / np.where(point_norm > 0.0, point_norm, 1.0)
    cosine = np.clip(point_unit @ ref_unit.T, -1.0, 1.0)
    projection = point_norm * cosine
    perpendicular = np.sqrt(np.maximum(point_norm ** 2 - projection ** 2, 0.0))
    association = np.argmin(perpendicular, axis=1)
    distance = perpendicular[np.arange(F.shape[0]), association]
    return association, distance


def tchebycheff_scores(F: np.ndarray, ref_dirs: np.ndarray) -> np.ndarray:
    """
    EN:
    Compute Tchebycheff decomposition scores for each point and direction.

    PL:
    Liczy wyniki dekompozycyjne Tchebycheffa dla punktow i kierunkow.
    """
    Fn, ideal, _ = normalized_objectives(F)
    weights = np.asarray(ref_dirs, dtype=float)
    weights = np.where(weights <= 0.0, 1e-8, weights)
    shifted = np.abs(Fn - np.min(Fn, axis=0))
    return np.max(shifted[:, None, :] * weights[None, :, :], axis=2)


def shifted_density(F: np.ndarray) -> np.ndarray:
    """
    EN:
    Compute a shifted-density estimate similar to MOEA-SD literature.

    PL:
    Liczy przyblizona gestosc przesunieta w przestrzeni celow.
    """
    F = np.asarray(F, dtype=float)
    n = F.shape[0]
    if n == 0:
        return np.zeros(0, dtype=float)
    density = np.zeros(n, dtype=float)
    for i in range(n):
        shifted = np.maximum(F, F[i])
        distances = np.linalg.norm(shifted - F[i], axis=1)
        distances[i] = np.inf
        density[i] = 1.0 / (1e-8 + np.min(distances))
    return density


@dataclass
class PopulationState:
    """
    EN:
    Snapshot of one multiobjective population.

    PL:
    Migawka jednej populacji algorytmu.
    """

    X: np.ndarray
    F: np.ndarray
    CV: np.ndarray
    rank: np.ndarray
    crowding: np.ndarray

    @property
    def feasible(self) -> np.ndarray:
        """
        EN:
        Return a feasibility mask for the snapshot.

        PL:
        Zwraca maske rozwiazan wykonalnych.
        """
        return feasible_mask(self.CV)


class ArrayPopulationView:
    """
    EN:
    Read-only pymoo-like population view over NumPy matrices.

    PL:
    Prosty widok populacji zgodny z oczekiwaniami callbackow GUI.
    """

    def __init__(self, state: Optional[PopulationState]):
        """
        EN:
        Store a state snapshot used by GUI callbacks.

        PL:
        Zapamietuje migawke populacji dla GUI.
        """
        self.state = state

    def get(self, name: str) -> Optional[np.ndarray]:
        """
        EN:
        Return `X`, `F` or `CV` arrays compatible with pymoo callbacks.

        PL:
        Zwraca macierze `X`, `F` lub `CV`.
        """
        if self.state is None:
            return None
        key = str(name).upper()
        if key == "X":
            return self.state.X
        if key == "F":
            return self.state.F
        if key == "CV":
            return self.state.CV
        return None


class ResearchMOOAlgorithm:
    """
    EN:
    GUI-compatible base class for custom article-inspired MOEAs implemented in NumPy.
    Implementation source: own implementation based on the article.
    PL:
    Bazowa klasa zgodna z GUI dla autorskich implementacji MOEA opartych o artykuly.
    """

    implementation_source = "own implementation based on the article"
    def __init__(
        self,
        population_size: int = 100,
        archive_size: int = 100,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        crossover_eta: float = 15.0,
        mutation_eta: float = 20.0,
        epsilon: float = 0.05,
        n_neighbors: int = 15,
        n_partitions: int = 12,
        reference_directions: Any = None,
        seed: int = 1,
    ) -> None:
        """
        EN:
        Store common configuration shared by research algorithm variants.

        PL:
        Zapamietuje wspolne ustawienia uzywane przez nowe warianty algorytmow.
        """
        self.population_size = parse_positive_int(population_size, "population_size")
        self.archive_size = parse_positive_int(archive_size, "archive_size")
        self.crossover_rate = parse_probability(crossover_rate, "crossover_rate")
        self.mutation_rate = parse_probability(mutation_rate, "mutation_rate")
        self.crossover_eta = parse_positive_float(crossover_eta, "crossover_eta")
        self.mutation_eta = parse_positive_float(mutation_eta, "mutation_eta")
        self.epsilon = parse_positive_float(epsilon, "epsilon")
        self.n_neighbors = parse_positive_int(n_neighbors, "n_neighbors")
        self.n_partitions = parse_positive_int(n_partitions, "n_partitions")
        self._reference_directions_input = reference_directions
        self.seed = int(seed)

        self.problem: Any = None
        self.xl: np.ndarray = np.empty(0, dtype=float)
        self.xu: np.ndarray = np.empty(0, dtype=float)
        self.n_var = 0
        self.n_obj = 0
        self.state: Optional[PopulationState] = None
        self.archive: Optional[PopulationState] = None
        self.pop = ArrayPopulationView(None)
        self.history: list[Dict[str, np.ndarray]] = []
        self.reference_directions: Optional[np.ndarray] = None
        self.random_state = np.random.default_rng(self.seed)
        self.evaluator = SimpleNamespace(n_eval=0)
        self.n_gen = 0

    def setup_rng(self, seed: Optional[int]) -> None:
        """
        EN:
        Initialize deterministic NumPy and Python random generators.

        PL:
        Ustawia deterministyczne generatory liczb losowych.
        """
        actual_seed = self.seed if seed is None else int(seed)
        random.seed(actual_seed)
        np.random.seed(actual_seed)
        self.random_state = np.random.default_rng(actual_seed)

    def initialize(self, problem: Any) -> None:
        """
        EN:
        Initialize the population, reference directions and archive for a new run.

        PL:
        Przygotowuje poczatkowa populacje, kierunki odniesienia i archiwum.
        """
        self.problem = problem
        self.xl, self.xu, self.n_var = problem_bounds(problem)
        self.n_obj = problem_n_obj(problem)
        self.reference_directions = sample_reference_directions(
            self.n_obj,
            self.population_size,
            self.n_partitions,
            self.random_state,
            parse_reference_directions(self._reference_directions_input, self.n_obj)
            if self._reference_directions_input is not None
            else None,
        )

        population = self.sample_initial_population()
        warm = self.warm_start_candidates()
        if warm is not None and np.asarray(warm).size:
            population = np.vstack([population, project_to_bounds(np.asarray(warm, dtype=float), self.xl, self.xu)])

        F, CV = self.evaluate(population)
        self.state = self.environmental_selection(population, F, CV, self.population_size)
        self.archive = self.build_archive(self.state)
        self.n_gen = 0
        self._update_population_view()
        self._remember_state()
        self.after_initialize()

    def after_initialize(self) -> None:
        """
        EN:
        Hook executed after the initial population has been created.

        PL:
        Hak wykonywany po przygotowaniu pierwszej populacji.
        """
        return None

    def sample_initial_population(self) -> np.ndarray:
        """
        EN:
        Sample the initial population uniformly inside the problem bounds.

        PL:
        Losuje poczatkowa populacje jednorodnie w granicach problemu.
        """
        return self.random_state.uniform(self.xl, self.xu, size=(self.population_size, self.n_var))

    def warm_start_candidates(self) -> Optional[np.ndarray]:
        """
        EN:
        Optional hook returning extra candidate solutions added before generation 1.

        PL:
        Opcjonalny hak zwracajacy dodatkowe rozwiazania startowe.
        """
        return None

    def evaluate(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        EN:
        Evaluate a decision matrix on the current problem and update evaluation counters.

        PL:
        Ocenia populacje na biezacym problemie i aktualizuje licznik ocen.
        """
        F, CV = evaluate_problem(self.problem, project_to_bounds(X, self.xl, self.xu))
        self.evaluator.n_eval += int(np.asarray(X).shape[0])
        return F, CV

    def select(self) -> np.ndarray:
        """
        EN:
        Select parent pairs with binary tournament selection.

        PL:
        Wybiera pary rodzicow przez turniej binarny.
        """
        assert self.state is not None
        return tournament_indices(
            self.state.rank,
            self.state.crowding,
            self.state.CV,
            self.population_size,
            self.random_state,
        )

    def crossover(self, parent_pairs: np.ndarray) -> np.ndarray:
        """
        EN:
        Create offspring with SBX crossover over the selected parent pairs.

        PL:
        Tworzy potomkow przez krzyzowanie SBX.
        """
        assert self.state is not None
        return sbx_crossover(
            self.state.X,
            parent_pairs,
            self.xl,
            self.xu,
            self.crossover_eta,
            self.crossover_rate,
            self.random_state,
        )

    def mutation(self, offspring: np.ndarray) -> np.ndarray:
        """
        EN:
        Mutate offspring with polynomial mutation.

        PL:
        Modyfikuje potomkow mutacja wielomianowa.
        """
        return polynomial_mutation(
            offspring,
            self.xl,
            self.xu,
            self.mutation_eta,
            self.mutation_rate,
            self.random_state,
        )

    def guided_candidates(self) -> np.ndarray:
        """
        EN:
        Optional hook producing article-specific guided candidate solutions.

        PL:
        Opcjonalny hak tworzacy dodatkowe kandydaty specyficzne dla danego artykulu.
        """
        return np.empty((0, self.n_var), dtype=float)

    def create_offspring(self) -> np.ndarray:
        """
        EN:
        Build the default offspring set used in one generation.

        PL:
        Buduje domyslny zestaw potomkow dla jednej generacji.
        """
        offspring = self.crossover(self.select())
        return self.mutation(offspring)

    def environmental_selection(
        self,
        X: np.ndarray,
        F: np.ndarray,
        CV: np.ndarray,
        n_survive: int,
    ) -> PopulationState:
        """
        EN:
        Select survivors with the default NSGA-II style feasible-first strategy.

        PL:
        Wybiera rozwiazania do kolejnej generacji domyslna metoda w stylu NSGA-II.
        """
        return select_survivors_nsga2(X, F, CV, n_survive)

    def build_archive(self, state: PopulationState) -> PopulationState:
        """
        EN:
        Maintain a bounded nondominated archive reused by guided variants.

        PL:
        Utrzymuje ograniczone archiwum rozwiazan do wykorzystania przez warianty predykcyjne.
        """
        if self.archive is None:
            merged_X = state.X
            merged_F = state.F
            merged_CV = state.CV
        else:
            merged_X = np.vstack([self.archive.X, state.X])
            merged_F = np.vstack([self.archive.F, state.F])
            merged_CV = np.concatenate([self.archive.CV, state.CV])
        return select_survivors_nsga2(merged_X, merged_F, merged_CV, self.archive_size)

    def archive_elites(self, count: int) -> np.ndarray:
        """
        EN:
        Return decision vectors of the best archived solutions.

        PL:
        Zwraca zmienne decyzyjne najlepszych rozwiazan z archiwum.
        """
        if self.archive is None or self.archive.X.size == 0:
            return np.empty((0, self.n_var), dtype=float)
        count = max(1, min(int(count), self.archive.X.shape[0]))
        return self.archive.X[:count]

    def state_centroid(self, state: Optional[PopulationState] = None, elite_fraction: float = 0.25) -> np.ndarray:
        """
        EN:
        Compute the centroid of the best fraction of a population state.

        PL:
        Liczy srodek ciezkosci najlepszej czesci populacji.
        """
        state = self.state if state is None else state
        if state is None or state.X.size == 0:
            return np.zeros(self.n_var, dtype=float)
        elite_count = max(1, int(math.ceil(state.X.shape[0] * float(elite_fraction))))
        return np.mean(state.X[:elite_count], axis=0)

    def state_spread(self, state: Optional[PopulationState] = None, elite_fraction: float = 0.25) -> np.ndarray:
        """
        EN:
        Compute a per-variable spread estimate over the best population fraction.

        PL:
        Liczy przyblizona skale najlepszej czesci populacji.
        """
        state = self.state if state is None else state
        if state is None or state.X.size == 0:
            return np.maximum(self.xu - self.xl, 1e-8)
        elite_count = max(1, int(math.ceil(state.X.shape[0] * float(elite_fraction))))
        elite = state.X[:elite_count]
        spread = np.std(elite, axis=0)
        return np.where(spread > 1e-8, spread, np.maximum((self.xu - self.xl) * 0.05, 1e-8))

    def diversity_score(self, state: Optional[PopulationState] = None) -> float:
        """
        EN:
        Return a simple objective-space diversity estimate for adaptation rules.

        PL:
        Zwraca prosty wskaznik roznorodnosci w przestrzeni celow.
        """
        state = self.state if state is None else state
        if state is None or state.F.shape[0] < 2:
            return 0.0
        Fn, _, _ = normalized_objectives(state.F)
        distances = np.linalg.norm(Fn[:, None, :] - Fn[None, :, :], axis=2)
        distances += np.eye(distances.shape[0]) * np.inf
        return float(np.mean(np.min(distances, axis=1)))

    def progress_score(self, previous: PopulationState, current: PopulationState) -> float:
        """
        EN:
        Compute a simple progress signal from ideal-point improvement and archive growth.

        PL:
        Liczy prosty sygnal postepu na podstawie ideal point i rozmiaru frontu.
        """
        prev_feasible = previous.F[previous.feasible] if np.any(previous.feasible) else previous.F
        curr_feasible = current.F[current.feasible] if np.any(current.feasible) else current.F
        prev_ideal = np.min(prev_feasible, axis=0)
        curr_ideal = np.min(curr_feasible, axis=0)
        ideal_gain = float(np.sum(np.maximum(prev_ideal - curr_ideal, 0.0)))
        nd_gain = max(0, np.sum(current.rank == 0) - np.sum(previous.rank == 0))
        return ideal_gain + 0.01 * float(nd_gain)

    def after_generation(self, previous: PopulationState, current: PopulationState) -> None:
        """
        EN:
        Hook executed after one full generation has finished.

        PL:
        Hak wykonywany po zakonczonej generacji.
        """
        return None

    def _remember_state(self) -> None:
        """
        EN:
        Append a compact history record used by predictive variants.

        PL:
        Dopisuje skondensowany rekord historii uzywany przez warianty predykcyjne.
        """
        if self.state is None:
            return
        self.history.append(
            {
                "centroid": self.state_centroid(self.state).copy(),
                "spread": self.state_spread(self.state).copy(),
                "ideal": np.min(self.state.F, axis=0).copy(),
                "rank0_mean": np.mean(self.state.F[self.state.rank == 0], axis=0)
                if np.any(self.state.rank == 0)
                else np.mean(self.state.F, axis=0),
            }
        )
        if len(self.history) > 20:
            self.history = self.history[-20:]

    def _update_population_view(self) -> None:
        """
        EN:
        Refresh the GUI-visible `pop` snapshot.

        PL:
        Odswieza widoczna dla GUI migawke populacji.
        """
        self.pop = ArrayPopulationView(self.state)

    def step(self) -> None:
        """
        EN:
        Execute one full evolutionary generation.

        PL:
        Wykonuje jedna pelna generacje algorytmu.
        """
        if self.state is None:
            raise RuntimeError("Algorithm must be initialized before step().")

        previous = self.state
        offspring = self.create_offspring()
        guided = self.guided_candidates()
        new_X = offspring if guided.size == 0 else np.vstack([offspring, guided])
        new_X = project_to_bounds(new_X, self.xl, self.xu)
        new_F, new_CV = self.evaluate(new_X)

        candidate_X = np.vstack([previous.X, new_X])
        candidate_F = np.vstack([previous.F, new_F])
        candidate_CV = np.concatenate([previous.CV, new_CV])

        self.state = self.environmental_selection(candidate_X, candidate_F, candidate_CV, self.population_size)
        self.archive = self.build_archive(self.state)
        self.n_gen += 1
        self._update_population_view()
        self._remember_state()
        self.after_generation(previous, self.state)

    def run(self, n_generations: int, callback: Any = None) -> None:
        """
        EN:
        Run a fixed number of generations with optional GUI callback notifications.

        PL:
        Uruchamia zadana liczbe generacji z opcjonalnym callbackiem GUI.
        """
        for _ in range(int(n_generations)):
            self.step()
            if callback is not None:
                callback(self)

    def finalize_result(self) -> Result:
        """
        EN:
        Build a pymoo-compatible result object from the current state.

        PL:
        Tworzy wynik zgodny z pymoo na podstawie aktualnego stanu.
        """
        result = Result()
        result.algorithm = self
        result.problem = self.problem
        result.X = None if self.state is None else self.state.X
        result.F = None if self.state is None else self.state.F
        result.CV = None if self.state is None else self.state.CV
        return result

    def gui_minimize(
        self,
        *,
        problem: Any,
        termination: Any,
        seed: Optional[int] = None,
        callback: Any = None,
        **kwargs: Any,
    ) -> Result:
        """
        EN:
        GUI-compatible optimization entry point used by the framework dispatcher.

        PL:
        Punkt wejsciowy zgodny z GUI frameworka.
        """
        self.setup_rng(seed)
        self.evaluator.n_eval = 0
        self.history = []
        self.archive = None
        self.initialize(problem)

        max_generations = termination_generations(termination)
        if max_generations is None:
            while True:
                self.step()
                if callback is not None:
                    callback(self)
        else:
            for _ in range(int(max_generations)):
                self.step()
                if callback is not None:
                    callback(self)

        return self.finalize_result()
