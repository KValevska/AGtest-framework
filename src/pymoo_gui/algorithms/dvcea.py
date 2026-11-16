"""DVCEA decision-variable classification evolutionary algorithm.

------------------------------------------------------------------------------------
Module: dvcea.py
Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
Article: X. Ban, J. Liang, K. Qiao, K. Yu, Y. Wang, J. Zhu and B. Qu,
         "A Decision Variables Classification-Based Evolutionary Algorithm for
         Constrained Multi-Objective Optimization Problems", IEEE/CAA Journal
         of Automatica Sinica 12(9), 1830-1849, 2025.
Implementation: standalone NumPy port of the supplied DVCEA.py/PlatEMO flow.
Responsibility: classifies FEA/INFEA variables, executes pbest and diversity DE
                stages, and performs epsilon-constrained SPEA2 survival.
Author: Kristina Valevska, MSc Eng.
------------------------------------------------------------------------------------
"""

from __future__ import annotations

import math
from typing import Any, Dict

import numpy as np

from .dssea import epsilon_spea2_fitness, epsilon_spea2_survival
from .research_common import (
    PopulationState,
    ResearchMOOAlgorithm,
    assign_rank_and_crowding,
    parse_positive_float,
    parse_positive_int,
    polynomial_mutation,
    project_to_bounds,
    termination_generations,
)


def kmeans_centroids(X: np.ndarray, count: int, rng: np.random.Generator, iterations: int = 35) -> np.ndarray:
    """Small deterministic Lloyd k-means used by the article's DV classification."""
    X = np.asarray(X, dtype=float)
    if len(X) < count:
        raise ValueError(f"DVCEA classification requires population_size >= {count}")
    centers = X[rng.choice(len(X), size=count, replace=False)].copy()
    for _ in range(iterations):
        labels = np.argmin(np.linalg.norm(X[:, None, :] - centers[None, :, :], axis=2), axis=1)
        updated = centers.copy()
        for index in range(count):
            members = X[labels == index]
            updated[index] = np.mean(members, axis=0) if len(members) else X[int(rng.integers(len(X)))]
        if np.allclose(updated, centers, atol=1e-9, rtol=0.0):
            break
        centers = updated
    return centers


def improved_epsilon_survival(X: np.ndarray, F: np.ndarray, CV: np.ndarray, count: int, epsilon: float) -> tuple[PopulationState, np.ndarray]:
    """DVCEA survival: [objectives,CV] for epsilon-feasible, CDP for the rest."""
    CV = np.asarray(CV, dtype=float).reshape(-1)
    feasible_ids = np.flatnonzero(CV <= epsilon)
    infeasible_ids = np.flatnonzero(CV > epsilon)
    selected: list[int] = []
    fitness_out: list[float] = []
    if feasible_ids.size:
        augmented = np.column_stack((F[feasible_ids], CV[feasible_ids]))
        state, fitness = epsilon_spea2_survival(X[feasible_ids], augmented, np.zeros(len(feasible_ids)), min(count, len(feasible_ids)), 0.0)
        # Recover original rows by decision vectors; duplicates use stable first matches.
        available = list(feasible_ids)
        for row in state.X:
            pos = next(i for i in available if np.array_equal(X[i], row))
            selected.append(int(pos)); available.remove(pos)
        fitness_out.extend(float(v) for v in fitness)
    remaining = count - len(selected)
    if remaining > 0 and infeasible_ids.size:
        state, fitness = epsilon_spea2_survival(X[infeasible_ids], F[infeasible_ids], CV[infeasible_ids], min(remaining, len(infeasible_ids)), 0.0)
        available = list(infeasible_ids)
        offset = max(fitness_out, default=0.0)
        for row in state.X:
            pos = next(i for i in available if np.array_equal(X[i], row))
            selected.append(int(pos)); available.remove(pos)
        fitness_out.extend(offset + float(v) for v in fitness)
    ids = np.asarray(selected[:count], dtype=int)
    rank, crowding = assign_rank_and_crowding(F[ids], CV[ids])
    return PopulationState(X[ids], F[ids], CV[ids], rank, crowding), np.asarray(fitness_out[:len(ids)])


class DVCEA(ResearchMOOAlgorithm):
    """Constraint-aware DVCEA with exact evaluation accounting for classification."""

    def __init__(self, population_size: int = 40, classification_threshold: float = 1e-5, seed: int = 1):
        if int(population_size) < 6:
            raise ValueError("population_size must be at least 6")
        super().__init__(population_size=int(population_size), archive_size=int(population_size), mutation_rate=0.0, seed=seed)
        self.classification_threshold = parse_positive_float(classification_threshold, "classification_threshold")
        self.fea_variables = np.empty(0, dtype=int)
        self.infea_variables = np.empty(0, dtype=int)
        self.fitness = np.empty(0)
        self.epsilon0 = 1.0
        self.epsilon = 1.0
        self._max_evaluations = 1

    def gui_minimize(self, *, problem: Any, termination: Any, **kwargs: Any):
        generations = termination_generations(termination) or 1
        self._max_evaluations = self.population_size + 20 * int(problem.n_var) + 2 * self.population_size * generations
        return super().gui_minimize(problem=problem, termination=termination, **kwargs)

    def after_initialize(self) -> None:
        assert self.state is not None
        centers = kmeans_centroids(self.state.X, 5, self.random_state)
        significant, insignificant = [], []
        for variable in range(self.n_var):
            samples = []
            for center in centers:
                points = np.repeat(center[None, :], 4, axis=0)
                points[:, variable] = np.linspace(self.xl[variable], self.xu[variable], 4)
                _, cv = self.evaluate(points)
                samples.append(float(np.std(cv, ddof=1)))
            (significant if float(np.mean(samples)) > self.classification_threshold else insignificant).append(variable)
        self.fea_variables = np.asarray(significant, dtype=int)
        self.infea_variables = np.asarray(insignificant, dtype=int)
        self.epsilon0 = float(np.max(self.state.CV)) or 1.0
        self.epsilon = self.epsilon0
        self.fitness = epsilon_spea2_fitness(self.state.F, self.state.CV, self.epsilon0)
        self.archive = self.state

    def _pbest_children(self) -> np.ndarray:
        assert self.state is not None
        n = len(self.state.X)
        ranked = np.argsort(self.fitness, kind="mergesort")
        pbest_pool = ranked[:max(2, round(0.1 * n))]
        children = self.state.X.copy()
        for i in range(n):
            others = np.delete(np.arange(n), i)
            r1, r2 = self.random_state.choice(others, size=2, replace=False)
            pbest = int(self.random_state.choice(pbest_pool))
            scale = float(self.random_state.choice((0.6, 0.8, 1.0)))
            cr = float(self.random_state.choice((0.1, 0.2, 1.0)))
            trial = self.state.X[i] + scale * (self.state.X[pbest] - self.state.X[i] + self.state.X[r1] - self.state.X[r2])
            mask = self.random_state.random(self.n_var) < cr
            trial = np.where(mask, trial, self.state.X[i])
            if self.fea_variables.size:
                children[i, self.fea_variables] = trial[self.fea_variables]
        return polynomial_mutation(project_to_bounds(children, self.xl, self.xu), self.xl, self.xu, 20.0, 1.0 / self.n_var, self.random_state)

    def _diversity_children(self) -> np.ndarray:
        assert self.state is not None
        n = len(self.state.X)
        order = list(self.random_state.permutation(n))
        children = self.state.X.copy()
        for pos in range(0, n - 1, 2):
            a, b = order[pos], order[pos + 1]
            best, worst = (a, b) if self.fitness[a] <= self.fitness[b] else (b, a)
            scale = float(self.random_state.choice((0.6, 0.8, 1.0)))
            cr = float(self.random_state.choice((0.1, 0.2, 1.0)))
            trial = self.state.X[best] + scale * (self.state.X[best] - self.state.X[worst])
            mask = self.random_state.random(self.n_var) < cr
            mask[int(self.random_state.integers(self.n_var))] = True
            trial = np.where(mask, trial, self.state.X[best])
            mixed = np.where(self.random_state.random(self.n_var) <= 0.5, self.state.X[best], self.state.X[worst])
            if self.infea_variables.size:
                children[a, self.infea_variables] = trial[self.infea_variables]
                children[b, self.infea_variables] = mixed[self.infea_variables]
        return polynomial_mutation(project_to_bounds(children, self.xl, self.xu), self.xl, self.xu, 20.0, 1.0 / self.n_var, self.random_state)

    def _select_with(self, children: np.ndarray) -> None:
        assert self.state is not None
        F, CV = self.evaluate(children)
        X = np.vstack((self.state.X, children)); all_F = np.vstack((self.state.F, F)); all_CV = np.concatenate((self.state.CV, CV))
        self.state, self.fitness = improved_epsilon_survival(X, all_F, all_CV, self.population_size, self.epsilon)

    def step(self) -> None:
        progress = min(1.0, self.evaluator.n_eval / max(1, self._max_evaluations))
        cp = (-math.log(self.epsilon0) - 6.0) / math.log(0.5)
        self.epsilon = self.epsilon0 * max(0.0, 1.0 - progress) ** cp
        self._select_with(self._pbest_children())
        self._select_with(self._diversity_children())
        self.archive = self.state
        self.n_gen += 1
        self._update_population_view()
        self._remember_state()


def make_dvcea(pop_size: int = 40, classification_threshold: float = 1e-5, seed: int = 1) -> DVCEA:
    return DVCEA(parse_positive_int(pop_size, "pop_size"), classification_threshold, int(seed))


DVCEA_DEFINITION: Dict[str, Any] = {
    "label": "DVCEA",
    "factory": make_dvcea,
    "reference": "X. Ban et al., IEEE/CAA Journal of Automatica Sinica 12(9), 1830-1849 (2025)",
    "requires_constraints": True,
    "form_fields": {
        "pop_size": {"default": 40, "kind": "int", "minimum": 6},
        "classification_threshold": {"default": 1e-5, "kind": "float", "minimum": 1e-12},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Initial classification costs exactly 20 evaluations per decision variable; each generation uses two DE stages.",
}

__all__ = ["DVCEA", "DVCEA_DEFINITION", "improved_epsilon_survival", "kmeans_centroids", "make_dvcea"]
