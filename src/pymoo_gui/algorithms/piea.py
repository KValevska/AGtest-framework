# PIEA implementation and GUI factory definition.
# Provenance: AGtest-framework standalone implementation using scikit-learn SVR and SciPy primitives.
#
# ------------------------------------------------------------------------------------
# Module: piea.py
# Summary: performance-indicator selection, SVR surrogate modelling and infill search.
# Implementation: PIEA adaptively selects SDE, additive epsilon+ or Minkowski fitness,
# trains an RBF-SVR model and uses DE with polynomial mutation to propose one expensive
# evaluation per generation.
# Responsibility: adds the 2024 surrogate-assisted PIEA algorithm to GUI experiments.
# Author: Kristina Valevska, MSc Eng.
# Article reference: Y. Li, W. Li, S. Li, and Y. Zhao, "A performance
# indicator-based evolutionary algorithm for expensive high-dimensional
# multi-/many-objective optimization," Information Sciences, 2024, 121045.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, Optional

import numpy as np
from pymoo.core.result import Result
from scipy.spatial.distance import cdist
from scipy.stats import qmc
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR

from .platypus_common import termination_generations
from .research_common import (
    ArrayPopulationView,
    PopulationState,
    evaluate_problem,
    parse_positive_int,
    problem_bounds,
    select_survivors_nsga2,
)


def _safe_normalize(values: np.ndarray) -> np.ndarray:
    # Normalize each column while keeping constant columns finite.
    values = np.asarray(values, dtype=float)
    lower = np.min(values, axis=0)
    upper = np.max(values, axis=0)
    return (values - lower) / np.where(upper > lower, upper - lower, 1.0)


def nondominated_sort(objectives: np.ndarray) -> np.ndarray:
    # Return one-based Pareto-front numbers for a minimization problem.
    objectives = np.asarray(objectives, dtype=float)
    count = objectives.shape[0]
    dominates = np.zeros((count, count), dtype=bool)
    for index in range(count):
        dominates[index] = np.all(objectives[index] <= objectives, axis=1) & np.any(
            objectives[index] < objectives,
            axis=1,
        )
    fronts = np.full(count, np.inf)
    remaining = np.ones(count, dtype=bool)
    level = 0
    while np.any(remaining):
        level += 1
        current = remaining & ~dominates[remaining].any(axis=0)
        fronts[current] = level
        remaining[current] = False
    return fronts.astype(int)


def _sdr_sort(objectives: np.ndarray) -> np.ndarray:
    # Apply strengthened-dominance sorting when scoring a new expensive evaluation.
    normalized = _safe_normalize(objectives)
    count = normalized.shape[0]
    norm_p = np.sum(normalized, axis=1)
    norms = np.linalg.norm(normalized, axis=1)
    cosine = (normalized @ normalized.T) / np.maximum(
        np.outer(norms, norms),
        np.finfo(float).eps,
    )
    cosine = np.clip(cosine, -1.0, 1.0)
    np.fill_diagonal(cosine, 0.0)
    angles = np.arccos(cosine)
    minima = np.sort(np.unique(np.min(angles, axis=1)))
    min_angle = minima[min(int(np.ceil(count / 2)), len(minima)) - 1]
    theta = np.maximum(1.0, angles / max(min_angle, np.finfo(float).eps))
    dominates = np.zeros((count, count), dtype=bool)
    for left in range(count - 1):
        for right in range(left + 1, count):
            if norm_p[left] * theta[left, right] < norm_p[right]:
                dominates[left, right] = True
            elif norm_p[right] * theta[right, left] < norm_p[left]:
                dominates[right, left] = True
    fronts = np.full(count, np.inf)
    remaining = np.ones(count, dtype=bool)
    level = 0
    while np.any(remaining):
        level += 1
        current = remaining & ~dominates[remaining].any(axis=0)
        fronts[current] = level
        remaining[current] = False
    return fronts.astype(int)


def _estimate_shape(objectives: np.ndarray) -> float:
    # Estimate the Pareto-front shape parameter used by two PIEA indicators.
    first_front = objectives[nondominated_sort(objectives) == 1]
    if first_front.shape[0] < 20:
        return 1.0
    normalized = _safe_normalize(first_front)
    candidates = np.asarray(
        [0.27, 0.36, 0.43, 0.5, 0.57, 0.66, 0.75, 0.86, 1.0, 1.15, 1.35, 1.6, 2.0, 2.4, 3.1, 4.2, 6.5]
    )
    scores: list[float] = []
    for candidate in candidates:
        distances = np.sum(normalized**candidate, axis=1) ** (1.0 / candidate)
        ordered = np.sort(distances)
        q1 = ordered[max(int(np.fix(len(distances) * 0.25)), 1) - 1]
        q3 = ordered[max(int(np.fix(len(distances) * 0.75)), 1) - 1]
        kept = distances[distances <= q3 + 1.5 * (q3 - q1)]
        scores.append(float(np.std(kept / max(np.max(kept), np.finfo(float).eps))))
    return float(candidates[int(np.argmin(scores))])


def _fitness_sde(objectives: np.ndarray, shape: float) -> np.ndarray:
    # Compute the shift-based density fitness combined with convergence pressure.
    normalized = _safe_normalize(objectives)
    count = normalized.shape[0]
    distances = np.full((count, count), np.inf)
    for index in range(count):
        shifted = np.maximum(normalized, normalized[index])
        distances[index] = np.linalg.norm(normalized[index] - shifted, axis=1)
        distances[index, index] = np.inf
    fitness = np.min(distances, axis=1)
    fitness = 3.0 * (fitness - np.min(fitness)) / (
        np.max(fitness) - np.min(fitness) + np.finfo(float).eps
    )
    convergence = cdist(
        normalized,
        np.min(normalized, axis=0, keepdims=True),
        metric="minkowski",
        p=shape,
    ).ravel()
    convergence = -3.0 * (convergence - np.min(convergence)) / (
        np.max(convergence) - np.min(convergence) + np.finfo(float).eps
    )
    fitness[fitness < 1e-4] = convergence[fitness < 1e-4]
    return np.tanh(fitness)


def _fitness_epsilon(objectives: np.ndarray, kappa: float = 0.05) -> np.ndarray:
    # Compute additive epsilon+ indicator fitness.
    normalized = _safe_normalize(objectives)
    indicator = np.max(normalized[:, None, :] - normalized[None, :, :], axis=2)
    scale = np.maximum(np.max(np.abs(indicator), axis=0), np.finfo(float).eps)
    return np.sum(-np.exp(-indicator / scale[None, :] / kappa), axis=0) + 1.0


def _fitness_minkowski(objectives: np.ndarray, shape: float) -> np.ndarray:
    # Prefer solutions close to the normalized ideal point.
    normalized = _safe_normalize(objectives)
    return -cdist(
        normalized,
        np.min(normalized, axis=0, keepdims=True),
        metric="minkowski",
        p=shape,
    ).ravel()


def _tournament(fitness: np.ndarray, count: int, rng: np.random.Generator) -> np.ndarray:
    # Select the larger fitness value in each binary tournament.
    left, right = rng.integers(0, len(fitness), size=(2, count))
    return np.where(fitness[left] >= fitness[right], left, right)


def operator_de(
    parent: np.ndarray,
    donor_a: np.ndarray,
    donor_b: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    rng: np.random.Generator,
    crossover_rate: float = 1.0,
    differential_weight: float = 0.5,
    mutation_probability: float = 1.0,
    mutation_eta: float = 20.0,
) -> np.ndarray:
    # Apply differential evolution followed by polynomial mutation.
    child = np.asarray(parent, dtype=float).copy()
    mask = rng.random(child.shape) < crossover_rate
    child[mask] += differential_weight * (donor_a[mask] - donor_b[mask])
    child = np.clip(child, lower, upper)
    mutate = rng.random(child.shape) < mutation_probability / child.shape[1]
    random_values = rng.random(child.shape)
    span = np.maximum(upper - lower, np.finfo(float).eps)
    lower_matrix = np.broadcast_to(lower, child.shape)
    upper_matrix = np.broadcast_to(upper, child.shape)
    span_matrix = np.broadcast_to(span, child.shape)
    left = mutate & (random_values <= 0.5)
    child[left] += span_matrix[left] * (
        (
            2.0 * random_values[left]
            + (1.0 - 2.0 * random_values[left])
            * (1.0 - (child[left] - lower_matrix[left]) / span_matrix[left]) ** (mutation_eta + 1.0)
        )
        ** (1.0 / (mutation_eta + 1.0))
        - 1.0
    )
    right = mutate & ~left
    child[right] += span_matrix[right] * (
        1.0
        - (
            2.0 * (1.0 - random_values[right])
            + 2.0
            * (random_values[right] - 0.5)
            * (1.0 - (upper_matrix[right] - child[right]) / span_matrix[right]) ** (mutation_eta + 1.0)
        )
        ** (1.0 / (mutation_eta + 1.0))
    )
    return np.clip(child, lower, upper)


class SurrogateArchiveAlgorithm:
    # Shared pymoo-compatible runtime facade for expensive surrogate algorithms.

    def __init__(self, population_size: int, seed: int) -> None:
        self.population_size = parse_positive_int(population_size, "population_size")
        if self.population_size < 2:
            raise ValueError("population_size must be at least 2")
        self.seed = int(seed)
        self.run_seed = self.seed
        self.problem: Any = None
        self.xl = np.empty(0, dtype=float)
        self.xu = np.empty(0, dtype=float)
        self.n_var = 0
        self.archive_X = np.empty((0, 0), dtype=float)
        self.archive_F = np.empty((0, 0), dtype=float)
        self.archive_CV = np.empty(0, dtype=float)
        self.state: Optional[PopulationState] = None
        self.pop = ArrayPopulationView(None)
        self.evaluator = SimpleNamespace(n_eval=0)
        self.n_gen = 0
        self.random_state = np.random.default_rng(self.seed)

    def _evaluate(self, decisions: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        # Evaluate true objectives and update the expensive-evaluation counter.
        objectives, violations = evaluate_problem(self.problem, decisions)
        self.evaluator.n_eval += int(len(decisions))
        return objectives, violations

    def _refresh_population(self) -> None:
        # Expose a bounded feasible-first archive view to GUI callbacks.
        keep = min(self.population_size, len(self.archive_X))
        self.state = select_survivors_nsga2(
            self.archive_X,
            self.archive_F,
            self.archive_CV,
            keep,
        )
        self.pop = ArrayPopulationView(self.state)

    def initialize(self, problem: Any) -> None:
        # Build the initial Latin-hypercube design and evaluate it exactly.
        self.problem = problem
        self.xl, self.xu, self.n_var = problem_bounds(problem)
        unit_design = qmc.LatinHypercube(d=self.n_var, seed=self.random_state).random(
            self.population_size
        )
        self.archive_X = self.xl + unit_design * (self.xu - self.xl)
        self.archive_F, self.archive_CV = self._evaluate(self.archive_X)
        self.n_gen = 0
        self._refresh_population()

    def finalize_result(self) -> Result:
        # Create the result structure expected by the framework.
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
        # Run one surrogate infill iteration per GUI generation.
        actual_seed = self.seed if seed is None else int(seed)
        self.run_seed = actual_seed
        self.random_state = np.random.default_rng(actual_seed)
        self.evaluator.n_eval = 0
        self.initialize(problem)
        maximum = termination_generations(termination)
        if maximum is None:
            while True:
                self.step()
                if callback is not None:
                    callback(self)
        else:
            for _ in range(int(maximum)):
                self.step()
                if callback is not None:
                    callback(self)
        return self.finalize_result()


class PIEA(SurrogateArchiveAlgorithm):
    # Performance Indicator-based Evolutionary Algorithm for expensive objectives.

    implementation_source = "standalone Python implementation based on Li et al. (2024)"

    def __init__(
        self,
        population_size: int = 40,
        eta: int = 5,
        surrogate_generations: int = 20,
        adaptation_window: int = 20,
        seed: int = 1,
    ) -> None:
        super().__init__(population_size=population_size, seed=seed)
        self.eta = parse_positive_int(eta, "eta")
        self.surrogate_generations = parse_positive_int(
            surrogate_generations,
            "surrogate_generations",
        )
        self.adaptation_window = parse_positive_int(adaptation_window, "adaptation_window")
        if self.eta > self.population_size:
            raise ValueError("eta must not exceed population_size")
        self.indicator_probabilities = np.full(3, 1.0 / 3.0)
        self._chosen = np.ones((3, self.adaptation_window), dtype=float)
        self._won = np.ones((3, self.adaptation_window), dtype=float)

    def initialize(self, problem: Any) -> None:
        # Reset adaptive indicator statistics for an independent run.
        super().initialize(problem)
        self.indicator_probabilities = np.full(3, 1.0 / 3.0)
        self._chosen = np.ones((3, self.adaptation_window), dtype=float)
        self._won = np.ones((3, self.adaptation_window), dtype=float)

    def step(self) -> None:
        # Train the selected surrogate and evaluate one diverse predicted candidate.
        shape = _estimate_shape(self.archive_F)
        indicator = int(self.random_state.choice(3, p=self.indicator_probabilities))
        if indicator == 0:
            fitness = _fitness_sde(self.archive_F, shape)
        elif indicator == 1:
            fitness = _fitness_epsilon(self.archive_F)
        else:
            fitness = _fitness_minkowski(self.archive_F, shape)

        model = make_pipeline(StandardScaler(), SVR(kernel="rbf", gamma="scale"))
        model.fit(self.archive_X, fitness)
        archive = self.archive_X[
            self.random_state.permutation(len(self.archive_X))[: self.population_size]
        ].copy()
        archive_fitness = np.full(self.population_size, -np.inf)
        for generation in range(self.surrogate_generations):
            mating = _tournament(fitness, self.population_size, self.random_state)
            donors = self.archive_X[
                self.random_state.permutation(len(self.archive_X))[: self.population_size]
            ]
            offspring = operator_de(
                self.archive_X[mating],
                archive,
                donors,
                self.xl,
                self.xu,
                self.random_state,
            )
            predicted = model.predict(offspring)
            if generation == 0:
                archive, archive_fitness = offspring, predicted
            else:
                replace = archive_fitness < predicted
                archive[replace] = offspring[replace]
                archive_fitness[replace] = predicted[replace]

        candidate_pool = archive[np.argsort(archive_fitness)[::-1][: self.eta]]
        normalized_archive = (self.archive_X - self.xl) / (self.xu - self.xl)
        normalized_candidates = (candidate_pool - self.xl) / (self.xu - self.xl)
        candidate = candidate_pool[
            int(np.argmax(np.min(cdist(normalized_candidates, normalized_archive), axis=1)))
        ]
        new_objectives, new_violations = self._evaluate(candidate[None, :])
        self.archive_X = np.vstack((self.archive_X, candidate))
        self.archive_F = np.vstack((self.archive_F, new_objectives))
        self.archive_CV = np.concatenate((self.archive_CV, new_violations))

        fronts = nondominated_sort(self.archive_F)
        score = 0.0
        if fronts[-1] == 1:
            score = 1.0
            if _sdr_sort(self.archive_F[fronts == 1])[-1] == 1:
                score = 2.0
        self._chosen[:, :-1] = self._chosen[:, 1:]
        self._chosen[:, -1] = 0.0
        self._chosen[indicator, -1] = 1.0
        self._won[:, :-1] = self._won[:, 1:]
        self._won[:, -1] = 0.0
        self._won[indicator, -1] = score / 2.0
        rates = (np.finfo(float).eps + np.sum(self._won, axis=1)) / (
            np.finfo(float).eps + np.sum(self._chosen, axis=1)
        )
        self.indicator_probabilities = rates / np.sum(rates)
        self.n_gen += 1
        self._refresh_population()


def make_piea(
    population_size: int = 40,
    eta: int = 5,
    surrogate_generations: int = 20,
    adaptation_window: int = 20,
    seed: int = 1,
) -> PIEA:
    # Create a configured PIEA instance for the GUI registry.
    return PIEA(
        population_size=population_size,
        eta=eta,
        surrogate_generations=surrogate_generations,
        adaptation_window=adaptation_window,
        seed=seed,
    )


PIEA_DEFINITION: Dict[str, Any] = {
    "label": "PIEA",
    "factory": make_piea,
    "implementation_type": "adapted_port",
    "reference": "Y. Li et al., Information Sciences 2024, 121045",
    "verified_against": "article-mechanism tests and deterministic short runs; no claim of numerical identity with the article experiments",
    "form_fields": {
        "population_size": {"default": 40, "kind": "int", "minimum": 2},
        "eta": {"default": 5, "kind": "int", "minimum": 1},
        "surrogate_generations": {"default": 20, "kind": "int", "minimum": 1},
        "adaptation_window": {"default": 20, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": (
        "Surrogate-assisted PIEA (Li et al., 2024). Each GUI generation trains an "
        "RBF-SVR model and performs one expensive infill evaluation after the initial LHS design."
    ),
}
