"""CMOBR decomposition-based constrained multi-objective optimizer.

------------------------------------------------------------------------------------
Module: cmobr.py
Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
Article: F. Ming, B. Xue, M. Zhang, W. Gong and H. Zhen,
         "Constrained Multiobjective Optimization via Relaxations on Both
         Constraints and Objectives", IEEE Transactions on Artificial
         Intelligence 5(12), 6709-6722, 2024.
Reference implementation: PlatEMO CMOBR and the supplied CMOBR.py port.
Implementation: standalone NumPy implementation of the push/pull transition,
                dual populations, epsilon relaxation and SPEA2 archive.
Responsibility: constrained decomposition search with objective/constraint relaxation.
Author: Kristina Valevska, MSc Eng.
------------------------------------------------------------------------------------
"""

from __future__ import annotations

import math
from typing import Any, Dict

import numpy as np

from .dssea import epsilon_spea2_survival
from .research_common import (
    PopulationState,
    ResearchMOOAlgorithm,
    assign_rank_and_crowding,
    parse_positive_float,
    parse_positive_int,
    parse_probability,
    polynomial_mutation,
    project_to_bounds,
    termination_generations,
)


def relative_front_change(history: list[np.ndarray], window: int) -> float:
    """Maximum relative ideal/nadir change over the requested window."""
    if len(history) <= window:
        return float("inf")
    old, new = history[-window - 1], history[-1]
    return float(np.max(np.abs(new - old) / np.maximum(np.abs(old), 1e-6)))


def epsilon_relaxation(current: float, initial: float, feasible_ratio: float, progress: float) -> float:
    if feasible_ratio < 0.95:
        return max(0.0, 0.95 * current)
    return max(0.0, initial * max(0.0, 1.0 - progress / 0.9) ** 2)


class CMOBR(ResearchMOOAlgorithm):
    """MOEA/D-like push/pull search with a post-switch auxiliary population."""

    def __init__(
        self,
        population_size: int = 40,
        delta: float = 0.9,
        nr: int = 2,
        stagnation_window: int = 20,
        change_threshold: float = 0.1,
        seed: int = 1,
    ) -> None:
        if int(population_size) < 4:
            raise ValueError("population_size must be at least 4")
        super().__init__(population_size=int(population_size), archive_size=int(population_size), mutation_rate=0.0, seed=seed)
        self.delta = parse_probability(delta, "delta")
        self.nr = parse_positive_int(nr, "nr")
        self.stagnation_window = parse_positive_int(stagnation_window, "stagnation_window")
        self.change_threshold = parse_positive_float(change_threshold, "change_threshold")
        self.stage = "push"
        self.population1: PopulationState | None = None
        self.population2: PopulationState | None = None
        self.ideal = np.empty(0)
        self.ideal2 = np.empty(0)
        self.neighborhoods = np.empty((0, 0), dtype=int)
        self.front_history: list[np.ndarray] = []
        self.epsilon = 0.0
        self.epsilon_initial = 0.0
        self.eta = 0.0
        self._max_generations = 1

    def gui_minimize(self, *, problem: Any, termination: Any, **kwargs: Any):
        self._max_generations = termination_generations(termination) or 1
        return super().gui_minimize(problem=problem, termination=termination, **kwargs)

    def after_initialize(self) -> None:
        assert self.state is not None and self.reference_directions is not None
        self.population1 = PopulationState(self.state.X.copy(), self.state.F.copy(), self.state.CV.copy(), self.state.rank.copy(), self.state.crowding.copy())
        W = self.reference_directions[:self.population_size]
        distances = np.linalg.norm(W[:, None, :] - W[None, :, :], axis=2)
        count = max(2, int(math.ceil(self.population_size / 10)))
        self.neighborhoods = np.argsort(distances, axis=1)[:, :count]
        self.ideal = np.min(self.state.F, axis=0)
        self.archive, _ = epsilon_spea2_survival(self.state.X, self.state.F, self.state.CV, self.population_size, 0.0)
        self.stage, self.population2 = "push", None
        self.front_history, self.epsilon, self.epsilon_initial, self.eta = [], 0.0, 0.0, 0.0

    def _trial_matrix(self, state: PopulationState) -> tuple[np.ndarray, list[np.ndarray]]:
        trials, pools = [], []
        all_ids = np.arange(self.population_size)
        for i in range(self.population_size):
            pool = self.neighborhoods[i].copy() if self.random_state.random() < self.delta else all_ids.copy()
            self.random_state.shuffle(pool)
            if len(pool) < 2:
                pool = all_ids.copy()
            mutant = state.X[i] + 0.5 * (state.X[pool[0]] - state.X[pool[1]])
            trials.append(mutant)
            pools.append(pool)
        X = project_to_bounds(np.asarray(trials), self.xl, self.xu)
        X = polynomial_mutation(X, self.xl, self.xu, 20.0, 1.0 / self.n_var, self.random_state)
        return X, pools

    @staticmethod
    def _tchebycheff(F: np.ndarray, ideal: np.ndarray, weights: np.ndarray) -> np.ndarray:
        return np.max(np.abs(F - ideal) * np.maximum(weights, 1e-8), axis=1)

    def _replace(self, state: PopulationState, child_X: np.ndarray, child_F: np.ndarray, child_CV: float, pool: np.ndarray, ideal: np.ndarray, epsilon: float | None, eta: float | None = None) -> None:
        replaced = 0
        W = self.reference_directions
        for j in pool:
            old_score = self._tchebycheff(state.F[j:j+1], ideal, W[j:j+1])[0]
            new_score = self._tchebycheff(child_F[None, :], ideal, W[j:j+1])[0]
            if epsilon is None:
                permit = new_score <= old_score
            else:
                comparable = (state.CV[j] <= epsilon and child_CV <= epsilon) or np.isclose(state.CV[j], child_CV)
                objective_ok = new_score <= old_score
                if eta is not None:
                    span = np.maximum(np.max(state.F, axis=0) - ideal, 1e-12)
                    objective_ok = np.sum((child_F - ideal) / span) <= eta or objective_ok
                permit = (comparable and objective_ok) or child_CV < state.CV[j]
            if permit:
                state.X[j], state.F[j], state.CV[j] = child_X, child_F, child_CV
                replaced += 1
            if replaced >= self.nr:
                break

    def _evolve(self, state: PopulationState, ideal: np.ndarray, epsilon: float | None, eta: float | None = None) -> np.ndarray:
        X, pools = self._trial_matrix(state)
        F, CV = self.evaluate(X)
        for i in range(len(X)):
            ideal[:] = np.minimum(ideal, F[i])
            self._replace(state, X[i], F[i], float(CV[i]), pools[i], ideal, epsilon, eta)
        state.rank, state.crowding = assign_rank_and_crowding(state.F, state.CV)
        return ideal

    def step(self) -> None:
        assert self.population1 is not None and self.archive is not None
        pop1 = self.population1
        ideal_now, nadir_now = np.min(pop1.F, axis=0), np.max(pop1.F, axis=0)
        self.front_history.append(np.concatenate((ideal_now, nadir_now)))
        change = relative_front_change(self.front_history, self.stagnation_window)
        progress = self.n_gen / max(1, self._max_generations)
        if self.stage == "push" and change <= self.change_threshold:
            self.stage = "pull"
            self.epsilon_initial = self.epsilon = float(np.max(pop1.CV))
            self.population2 = PopulationState(pop1.X.copy(), pop1.F.copy(), pop1.CV.copy(), pop1.rank.copy(), pop1.crowding.copy())
            self.ideal2 = np.min(self.population2.F, axis=0)
        if self.stage == "pull":
            self.epsilon = epsilon_relaxation(self.epsilon, self.epsilon_initial, float(np.mean(pop1.CV <= 1e-12)), progress)
        self.ideal = self._evolve(pop1, self.ideal, None if self.stage == "push" else self.epsilon)
        if self.population2 is not None:
            if progress > 0.5:
                sums = np.sum((pop1.F - np.min(pop1.F, axis=0)) / np.maximum(np.ptp(pop1.F, axis=0), 1e-12), axis=1)
                upper, lower = 2 * float(np.max(sums)), 0.5 * float(np.min(sums))
                self.eta = 0.95 * self.eta if self.eta >= lower else upper
                if progress > 0.9:
                    self.eta = 0.0
            self.ideal2 = self._evolve(self.population2, self.ideal2, None if progress <= 0.5 else self.epsilon, None if progress <= 0.5 else self.eta)
        parts = [self.archive, pop1] + ([self.population2] if self.population2 is not None else [])
        X = np.vstack([part.X for part in parts]); F = np.vstack([part.F for part in parts]); CV = np.concatenate([part.CV for part in parts])
        unique = np.unique(np.round(np.column_stack((X, F, CV)), 12), axis=0, return_index=True)[1]
        self.archive, _ = epsilon_spea2_survival(X[unique], F[unique], CV[unique], self.population_size, 0.0)
        self.state = self.archive
        self.n_gen += 1
        self._update_population_view()
        self._remember_state()


def make_cmobr(pop_size: int = 40, delta: float = 0.9, nr: int = 2, stagnation_window: int = 20, change_threshold: float = 0.1, seed: int = 1) -> CMOBR:
    return CMOBR(pop_size, delta, nr, stagnation_window, change_threshold, seed)


CMOBR_DEFINITION: Dict[str, Any] = {
    "label": "CMOBR",
    "factory": make_cmobr,
    "reference": "F. Ming et al., IEEE Transactions on Artificial Intelligence 5(12), 6709-6722 (2024)",
    "requires_constraints": True,
    "form_fields": {
        "pop_size": {"default": 40, "kind": "int", "minimum": 4},
        "delta": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "nr": {"default": 2, "kind": "int", "minimum": 1},
        "stagnation_window": {"default": 20, "kind": "int", "minimum": 2},
        "change_threshold": {"default": 0.1, "kind": "float", "minimum": 1e-12},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Push/pull constrained decomposition with an auxiliary population and SPEA2 archive.",
}

__all__ = ["CMOBR", "CMOBR_DEFINITION", "epsilon_relaxation", "make_cmobr", "relative_front_change"]
