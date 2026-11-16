# TEA implementation and GUI factory definition.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
#
# ------------------------------------------------------------------------------------
# Module: tea.py
# Summary: two-phase Gaussian-process assistance, P-PD sorting and batch infill search.
# Implementation: objective and constraint Kriging surrogates guide DE evolution; P-PD
# ranks uncertain predictions and the most distant candidates receive true evaluations.
# Responsibility: adds the 2024 surrogate-assisted TEA algorithm to GUI experiments.
# Author: Kristina Valevska, MSc Eng.
# Article reference: Z. Zhang, Y. Wang, J. Liu, G. Sun, and K. Tang,
# "A Two-Phase Kriging-Assisted Evolutionary Algorithm for Expensive Constrained
# Multiobjective Optimization Problems," IEEE TSMC: Systems, 2024, 54: 4579-4591,
# DOI: 10.1109/TSMC.2024.3383219.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
from scipy.spatial.distance import cdist
from scipy.stats import norm, qmc

from .piea import SurrogateArchiveAlgorithm, nondominated_sort, operator_de
from .research_common import parse_positive_int, problem_bounds
from .surrogate_common import Kriging


def _normalize(objectives: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # Normalize objectives and return the scale needed for MSE conversion.
    lower = np.min(objectives, axis=0)
    upper = np.max(objectives, axis=0)
    scale = np.maximum(upper - lower, 1e-9)
    return (objectives - lower) / scale, scale


def _standard_sort(objectives: np.ndarray, constraints: Optional[np.ndarray] = None) -> np.ndarray:
    # Apply feasible-first nondominated sorting to exact observations.
    if constraints is None or constraints.shape[1] == 0:
        return nondominated_sort(objectives)
    violation = np.sum(np.maximum(constraints, 0.0), axis=1)
    count = len(objectives)
    dominates = np.zeros((count, count), dtype=bool)
    for left in range(count):
        for right in range(count):
            if violation[left] == 0.0 and violation[right] == 0.0:
                dominates[left, right] = np.all(objectives[left] <= objectives[right]) and np.any(
                    objectives[left] < objectives[right]
                )
            elif violation[left] < violation[right]:
                dominates[left, right] = True
    fronts = np.full(count, np.inf)
    remaining = np.ones(count, dtype=bool)
    level = 0
    while np.any(remaining):
        level += 1
        current = remaining & ~dominates[remaining].any(axis=0)
        fronts[current] = level
        remaining[current] = False
    return fronts.astype(int)


def ppd_sort(
    objectives: np.ndarray,
    mse: np.ndarray,
    n_sort: int,
    constraints: Optional[np.ndarray] = None,
    constraint_mse: Optional[np.ndarray] = None,
) -> np.ndarray:
    # Perform TEA probability-based Pareto-dominance sorting.
    count = len(objectives)
    dominates = np.zeros((count, count), dtype=bool)
    feasible_probability = None
    total_probability = None
    if constraints is not None and constraints.shape[1]:
        safe_mse = np.maximum(np.asarray(constraint_mse, dtype=float), 1e-15)
        probabilities = norm.cdf(-constraints / np.sqrt(safe_mse))
        feasible_probability = np.min(probabilities, axis=1)
        total_probability = np.prod(probabilities, axis=1)

    for left in range(count - 1):
        for right in range(left + 1, count):
            sigma = np.sqrt(np.maximum(mse[left] + mse[right], 1e-15))
            left_probability = norm.cdf((objectives[right] - objectives[left]) / sigma)
            right_probability = 1.0 - left_probability
            near = np.abs(left_probability - right_probability) <= 0.75
            left_vector = np.r_[-left_probability[~near], -np.prod(left_probability[near])]
            right_vector = np.r_[-right_probability[~near], -np.prod(right_probability[near])]
            if np.all(left_vector <= right_vector) and np.any(left_vector < right_vector):
                flag = 1
            elif np.all(left_vector >= right_vector) and np.any(left_vector > right_vector):
                flag = 2
            else:
                flag = 3
            if feasible_probability is not None and not (
                (
                    feasible_probability[left] >= 0.5
                    and feasible_probability[right] >= 0.5
                )
                or feasible_probability[left] == feasible_probability[right]
            ):
                flag = 1 if total_probability[left] > total_probability[right] else 2
            if flag == 1:
                dominates[left, right] = True
            elif flag == 2:
                dominates[right, left] = True

    fronts = np.full(count, np.inf)
    remaining = np.ones(count, dtype=bool)
    level = 0
    while np.sum(~np.isfinite(fronts)) < min(int(n_sort), count):
        level += 1
        indices = np.flatnonzero(remaining)
        indegree = np.sum(dominates[np.ix_(indices, indices)], axis=0)
        current = indices[indegree == np.min(indegree)]
        fronts[current] = level
        remaining[current] = False
        dominates[current] = False
    fronts[~np.isfinite(fronts)] = level + 1
    return fronts.astype(int)


def _truncate(objectives: np.ndarray, keep: int) -> np.ndarray:
    # Remove crowded solutions using lexicographic nearest-neighbour distances.
    alive = np.ones(len(objectives), dtype=bool)
    distances = cdist(objectives, objectives)
    np.fill_diagonal(distances, np.inf)
    while np.sum(alive) > keep:
        indices = np.flatnonzero(alive)
        ordered = np.sort(distances[np.ix_(indices, indices)], axis=1)
        drop = indices[np.lexsort(ordered[:, ::-1].T)[0]]
        alive[drop] = False
    return alive


def _environmental_selection(
    objectives: np.ndarray,
    mse: np.ndarray,
    constraints: np.ndarray,
    constraint_mse: np.ndarray,
    size: int,
    phase: int,
) -> np.ndarray:
    # Select a fixed-size population from exact or surrogate observations.
    normalized, scale = _normalize(objectives)
    normalized_mse = mse / scale**2
    fronts = ppd_sort(
        normalized,
        normalized_mse,
        size,
        constraints if phase == 2 else None,
        constraint_mse if phase == 2 else None,
    )
    last = int(np.max(fronts))
    selected = fronts < last
    candidates = np.flatnonzero(fronts == last)
    remaining = int(size - np.sum(selected))
    if remaining <= 0:
        return selected
    if last == 1:
        chosen = _truncate(normalized[candidates], remaining)
        selected[candidates[chosen]] = True
    else:
        distances = cdist(normalized, normalized)
        np.fill_diagonal(distances, np.inf)
        density = 1.0 / (np.min(distances[candidates], axis=1) + 2.0)
        selected[candidates[np.argsort(density)[:remaining]]] = True
    return selected


def _fit_models(
    decisions: np.ndarray,
    values: np.ndarray,
    seed: Optional[int],
) -> list[Kriging]:
    # Fit one independent DACE-style universal Kriging model per output column.
    models: list[Kriging] = []
    for column in values.T:
        model = Kriging(linear=True).fit(decisions, column)
        models.append(model)
    return models


def _predict(
    models: list[Kriging],
    decisions: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    # Return predicted means and variances for all surrogate outputs.
    predictions = [model.predict(decisions) for model in models]
    means = np.column_stack([prediction[0] for prediction in predictions])
    variances = np.column_stack([prediction[1] for prediction in predictions])
    return means, variances


class TEA(SurrogateArchiveAlgorithm):
    # Two-phase Kriging-assisted evolutionary algorithm.

    implementation_source = "standalone Python implementation based on Zhang et al. (2024)"

    def __init__(
        self,
        population_size: int = 40,
        surrogate_generations: int = 20,
        infill_batch_size: int = 5,
        seed: int = 1,
    ) -> None:
        super().__init__(population_size=population_size, seed=seed)
        self.surrogate_generations = parse_positive_int(
            surrogate_generations,
            "surrogate_generations",
        )
        self.infill_batch_size = parse_positive_int(infill_batch_size, "infill_batch_size")
        if self.infill_batch_size > self.population_size:
            raise ValueError("infill_batch_size must not exceed population_size")
        self.phase = 1
        self._stalled = 0
        self._active = np.empty(0, dtype=int)
        self._constraint_values = np.empty((0, 0), dtype=float)

    def _evaluate_exact(
        self,
        decisions: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Preserve individual constraints for TEA models and aggregate them for GUI callbacks.
        output = self.problem.evaluate(
            np.asarray(decisions, dtype=float),
            return_values_of=["F", "G", "H"],
            return_as_dictionary=True,
        )
        objectives = np.asarray(output.get("F"), dtype=float)
        if objectives.ndim == 1:
            objectives = objectives.reshape(-1, 1)
        columns: list[np.ndarray] = []
        inequalities = output.get("G")
        if inequalities is not None:
            inequalities = np.asarray(inequalities, dtype=float)
            columns.append(
                inequalities.reshape(-1, 1) if inequalities.ndim == 1 else inequalities
            )
        equalities = output.get("H")
        if equalities is not None:
            equalities = np.asarray(equalities, dtype=float)
            equalities = equalities.reshape(-1, 1) if equalities.ndim == 1 else equalities
            columns.append(np.abs(equalities))
        constraints = (
            np.column_stack(columns)
            if columns
            else np.zeros((len(objectives), 0), dtype=float)
        )
        violations = (
            np.sum(np.maximum(constraints, 0.0), axis=1)
            if constraints.shape[1]
            else np.zeros(len(objectives), dtype=float)
        )
        self.evaluator.n_eval += int(len(decisions))
        return objectives, violations, constraints

    def initialize(self, problem: Any) -> None:
        # Initialize the exact archive and phase-one active population.
        self.problem = problem
        self.xl, self.xu, self.n_var = problem_bounds(problem)
        unit_design = qmc.LatinHypercube(d=self.n_var, seed=self.random_state).random(
            self.population_size
        )
        self.archive_X = self.xl + unit_design * (self.xu - self.xl)
        self.archive_F, self.archive_CV, self._constraint_values = self._evaluate_exact(
            self.archive_X
        )
        self.n_gen = 0
        self._refresh_population()
        self._active = np.arange(self.population_size)
        self.phase = 1
        self._stalled = 0

    def step(self) -> None:
        # Evolve surrogate populations and evaluate a diverse candidate batch.
        objective_models = _fit_models(self.archive_X, self.archive_F, self.run_seed)
        constraint_models = (
            _fit_models(self.archive_X, self._constraint_values, self.run_seed)
            if self.phase == 2 and self._constraint_values.shape[1]
            else []
        )
        population_X = self.archive_X[self._active].copy()
        population_F = self.archive_F[self._active].copy()
        population_C = self._constraint_values[self._active].copy()
        population_mse = np.zeros_like(population_F)
        population_constraint_mse = np.zeros_like(population_C)

        for _ in range(self.surrogate_generations):
            parent_indices = self.random_state.integers(0, len(population_X), len(population_X))
            donor_a = population_X[self.random_state.permutation(len(population_X))]
            donor_b = population_X[self.random_state.permutation(len(population_X))]
            offspring = operator_de(
                population_X[parent_indices],
                donor_a,
                donor_b,
                self.xl,
                self.xu,
                self.random_state,
            )
            offspring_F, offspring_mse = _predict(objective_models, offspring)
            if constraint_models:
                offspring_C, offspring_constraint_mse = _predict(constraint_models, offspring)
            else:
                offspring_C = np.zeros((len(offspring), self._constraint_values.shape[1]))
                offspring_constraint_mse = np.zeros_like(offspring_C)
            all_X = np.vstack((population_X, offspring))
            all_F = np.vstack((population_F, offspring_F))
            all_C = np.vstack((population_C, offspring_C))
            all_mse = np.vstack((population_mse, offspring_mse))
            all_constraint_mse = np.vstack(
                (population_constraint_mse, offspring_constraint_mse)
            )
            take = _environmental_selection(
                all_F,
                all_mse,
                all_C,
                all_constraint_mse,
                self.population_size,
                self.phase,
            )
            population_X = all_X[take]
            population_F = all_F[take]
            population_C = all_C[take]
            population_mse = all_mse[take]
            population_constraint_mse = all_constraint_mse[take]

        unique = np.asarray(
            [np.min(np.linalg.norm(self.archive_X - candidate, axis=1)) > 1e-5 for candidate in population_X]
        )
        candidate_X = population_X[unique]
        candidate_F = population_F[unique]
        if not len(candidate_X):
            # Maintain progress if all surrogate candidates duplicate evaluated points.
            candidate_X = self.random_state.uniform(self.xl, self.xu, size=(1, self.n_var))
            candidate_F, _ = _predict(objective_models, candidate_X)

        exact_front = self.archive_F[
            _standard_sort(
                self.archive_F,
                self._constraint_values if self.phase == 2 else None,
            )
            == 1
        ]
        chosen: list[np.ndarray] = []
        for _ in range(min(self.infill_batch_size, len(candidate_X))):
            index = int(np.argmax(np.min(cdist(candidate_F, exact_front), axis=1)))
            chosen.append(candidate_X[index])
            exact_front = np.vstack((exact_front, candidate_F[index]))
            candidate_X = np.delete(candidate_X, index, axis=0)
            candidate_F = np.delete(candidate_F, index, axis=0)
        new_X = np.asarray(chosen, dtype=float)
        new_F, new_CV, new_C = self._evaluate_exact(new_X)
        previous_feasible = (
            np.any(np.all(self._constraint_values <= 0.0, axis=1))
            if self._constraint_values.shape[1]
            else True
        )
        self.archive_X = np.vstack((self.archive_X, new_X))
        self.archive_F = np.vstack((self.archive_F, new_F))
        self.archive_CV = np.concatenate((self.archive_CV, new_CV))
        self._constraint_values = np.vstack((self._constraint_values, new_C))

        if self.phase == 1 and self._constraint_values.shape[1] and previous_feasible:
            new_is_nondominated = np.any(
                _standard_sort(self.archive_F, self._constraint_values)[-len(new_X) :] == 1
            )
            self._stalled = 0 if new_is_nondominated else self._stalled + 1
            if self._stalled >= 2:
                self.phase = 2

        keep = _environmental_selection(
            self.archive_F,
            np.zeros_like(self.archive_F),
            self._constraint_values,
            np.zeros_like(self._constraint_values),
            self.population_size,
            self.phase,
        )
        self._active = np.flatnonzero(keep)
        self.n_gen += 1
        self._refresh_population()


def make_tea(
    population_size: int = 40,
    surrogate_generations: int = 20,
    infill_batch_size: int = 5,
    seed: int = 1,
) -> TEA:
    # Create a configured TEA instance for the GUI registry.
    return TEA(
        population_size=population_size,
        surrogate_generations=surrogate_generations,
        infill_batch_size=infill_batch_size,
        seed=seed,
    )


TEA_DEFINITION: Dict[str, Any] = {
    "label": "TEA",
    "factory": make_tea,
    "requires_constraints": True,
    "implementation_type": "adapted_port",
    "reference": "Z. Zhang et al., IEEE TSMC: Systems 54, 4579-4591 (2024), DOI 10.1109/TSMC.2024.3383219",
    "verified_against": "mechanism tests, constrained runtime tests and deterministic short runs; internal DACE-style universal Kriging",
    "form_fields": {
        "population_size": {"default": 40, "kind": "int", "minimum": 2},
        "surrogate_generations": {"default": 20, "kind": "int", "minimum": 1},
        "infill_batch_size": {"default": 5, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": (
        "Two-phase Kriging-assisted TEA (Zhang et al., 2024). Each GUI generation "
        "evaluates a diverse infill batch after surrogate evolution and P-PD selection."
    ),
}
