"""CMOEA-CD constrained multi-objective evolutionary algorithm.

------------------------------------------------------------------------------------
Module: cmoea_cd.py
Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
Article: Z. Liu, F. Han, Q.-H. Ling, H. Han and J. Jiang,
         "Constraint-Pareto Dominance and Diversity Enhancement Strategy-Based
         Evolutionary Algorithm for Solving Constrained Multiobjective Optimization
         Problems", IEEE Transactions on Evolutionary Computation 29(6), 2025.
DOI: 10.1109/TEVC.2024.3525153
Implementation: standalone NumPy port of the supplied CMOEA_CD.py/PlatEMO flow.
Responsibility: maintains forward exploration (FA), diversity enhancement (DA),
                and feasibility exploitation (FEA) archives with GA/DE reproduction.
Author: Kristina Valevska, MSc Eng.
------------------------------------------------------------------------------------
"""

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .research_common import (
    PopulationState,
    ResearchMOOAlgorithm,
    assign_rank_and_crowding,
    crowding_distance,
    non_dominated_fronts,
    normalized_objectives,
    parse_positive_int,
    polynomial_mutation,
    project_to_bounds,
    sbx_crossover,
    select_survivors_nsga2,
)


def _state(X: np.ndarray, F: np.ndarray, CV: np.ndarray) -> PopulationState:
    rank, crowding = assign_rank_and_crowding(F, CV)
    return PopulationState(np.asarray(X), np.asarray(F), np.asarray(CV), rank, crowding)


def constraint_pareto_mask(F: np.ndarray, CV: np.ndarray, constrained: bool) -> np.ndarray:
    """Return points not dominated by the paper's constraint-Pareto relation."""
    F, CV = np.asarray(F), np.asarray(CV).reshape(-1)
    n = len(F)
    alive = np.ones(n, dtype=bool)
    for i in range(n):
        for j in range(i + 1, n):
            i_dom = np.all(F[i] <= F[j]) and np.any(F[i] < F[j])
            j_dom = np.all(F[j] <= F[i]) and np.any(F[j] < F[i])
            if i_dom and (not constrained or CV[i] <= CV[j]):
                alive[j] = False
            elif j_dom and (not constrained or CV[j] <= CV[i]):
                alive[i] = False
    return alive


def _truncate_distance(F: np.ndarray, count: int) -> np.ndarray:
    remaining = list(range(len(F)))
    Fn, _, _ = normalized_objectives(F)
    while len(remaining) > count:
        profiles = []
        for i in remaining:
            d = np.linalg.norm(Fn[remaining] - Fn[i], axis=1)
            profiles.append(tuple(np.sort(d[d > 0])))
        del remaining[min(range(len(remaining)), key=lambda k: profiles[k])]
    return np.asarray(remaining, dtype=int)


def _mode_indices(F: np.ndarray, count: int, mode: int, refs: np.ndarray) -> np.ndarray:
    if len(F) <= count:
        return np.resize(np.arange(len(F)), count)
    if mode == 1:
        return _truncate_distance(F, count)
    if mode == 2:
        return np.argsort(-crowding_distance(F), kind="mergesort")[:count]
    Fn, _, _ = normalized_objectives(F)
    W = refs[:count] / np.maximum(np.linalg.norm(refs[:count], axis=1, keepdims=True), 1e-15)
    norms = np.linalg.norm(Fn, axis=1)
    cosine = Fn @ W.T / np.maximum(norms[:, None], 1e-15)
    perpendicular = norms[:, None] * np.sqrt(np.maximum(0.0, 1.0 - np.clip(cosine, -1, 1) ** 2))
    return np.argmin(perpendicular, axis=0)


class CMOEACD(ResearchMOOAlgorithm):
    """Three-archive CMOEA-CD with constraint-Pareto diversity preservation."""

    def __init__(self, population_size: int = 90, e1: int = 1, e2: int = 1, seed: int = 1):
        if int(population_size) < 6:
            raise ValueError("population_size must be at least 6")
        if int(e1) not in {1, 2, 3} or int(e2) not in {1, 2, 3}:
            raise ValueError("e1 and e2 must be 1, 2 or 3")
        super().__init__(population_size=int(population_size), archive_size=int(population_size), mutation_rate=0.0, seed=seed)
        self.e1, self.e2 = int(e1), int(e2)
        self.fa: PopulationState | None = None
        self.da: PopulationState | None = None
        self.fea: PopulationState | None = None

    def after_initialize(self) -> None:
        assert self.state is not None
        self.fa = self._update_archive(None, self.state, self.population_size // 3, self.e1, False)
        self.da = self._update_da(None, self.state, self.population_size // 3)
        self.fea = self._update_archive(None, self.state, self.population_size, self.e2, True)
        self.state, self.archive = self.fea, self.fea

    def _merged(self, old: PopulationState | None, new: PopulationState) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if old is None:
            return new.X, new.F, new.CV
        return np.vstack((old.X, new.X)), np.vstack((old.F, new.F)), np.concatenate((old.CV, new.CV))

    def _update_archive(self, old: PopulationState | None, new: PopulationState, count: int, mode: int, constrained: bool) -> PopulationState:
        X, F, CV = self._merged(old, new)
        mask = constraint_pareto_mask(F, CV, constrained)
        X, F, CV = X[mask], F[mask], CV[mask]
        ids = _mode_indices(F, count, mode, self.reference_directions)
        return _state(X[ids], F[ids], CV[ids])

    def _update_da(self, old: PopulationState | None, new: PopulationState, count: int) -> PopulationState:
        X, F, CV = self._merged(old, new)
        mask = constraint_pareto_mask(F, CV, True)
        X, F, CV = X[mask], F[mask], CV[mask]
        Fn, _, _ = normalized_objectives(F)
        W = self.reference_directions[:count]
        W = W / np.maximum(np.linalg.norm(W, axis=1, keepdims=True), 1e-15)
        norms = np.linalg.norm(Fn, axis=1)
        angle = np.sqrt(np.maximum(0, 1 - np.clip(Fn @ W.T / np.maximum(norms[:, None], 1e-15), -1, 1) ** 2))
        selected = []
        for j in range(count):
            nearby = np.argsort(angle[:, j])[:max(1, min(3, len(F)))]
            feasible = nearby[CV[nearby] <= 1e-12]
            selected.append(int(feasible[np.argmin(angle[feasible, j])] if feasible.size else nearby[np.argmin(CV[nearby])]))
        ids = np.asarray(selected)
        return _state(X[ids], F[ids], CV[ids])

    def _children(self) -> np.ndarray:
        assert self.fa is not None and self.da is not None and self.fea is not None
        count = self.population_size // 3
        groups = (self.fa.X, self.da.X, self.fea.X[self.random_state.integers(0, len(self.fea.X), size=count)])
        children = []
        use_de = self.random_state.random() < 0.5
        for group in groups:
            if use_de:
                p2, p3 = self.random_state.permutation(len(group)), self.random_state.permutation(len(group))
                child = group + 0.5 * (group[p2] - group[p3])
            else:
                pairs = np.column_stack((np.arange(len(group)), np.roll(np.arange(len(group)), 1)))
                child = sbx_crossover(group, pairs, self.xl, self.xu, 20.0, 1.0, self.random_state)
            children.append(polynomial_mutation(child, self.xl, self.xu, 20.0, 1.0 / self.n_var, self.random_state))
        result = np.vstack(children)
        if len(result) < self.population_size:
            result = np.vstack((result, self.fea.X[self.random_state.integers(0, len(self.fea.X), size=self.population_size-len(result))]))
        return project_to_bounds(result[:self.population_size], self.xl, self.xu)

    def step(self) -> None:
        offspring_X = self._children()
        F, CV = self.evaluate(offspring_X)
        offspring = _state(offspring_X, F, CV)
        count = self.population_size // 3
        self.fa = self._update_archive(self.fa, offspring, count, self.e1, False)
        self.da = self._update_da(self.da, offspring, count)
        self.fea = self._update_archive(self.fea, offspring, self.population_size, self.e2, True)
        self.state, self.archive = self.fea, self.fea
        self.n_gen += 1
        self._update_population_view()
        self._remember_state()


def make_cmoea_cd(pop_size: int = 90, e1: int = 1, e2: int = 1, seed: int = 1) -> CMOEACD:
    return CMOEACD(parse_positive_int(pop_size, "pop_size"), e1=e1, e2=e2, seed=int(seed))


CMOEA_CD_DEFINITION: Dict[str, Any] = {
    "label": "CMOEA-CD",
    "factory": make_cmoea_cd,
    "reference": "Z. Liu et al., IEEE TEVC 29(6), 2771-2784 (2025), DOI 10.1109/TEVC.2024.3525153",
    "requires_constraints": True,
    "form_fields": {
        "pop_size": {"default": 90, "kind": "int", "minimum": 6},
        "e1": {"default": 1, "kind": "int", "minimum": 1, "maximum": 3},
        "e2": {"default": 1, "kind": "int", "minimum": 1, "maximum": 3},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Three archives: FA, DA and FEA; e1/e2 select distance, crowding or reference-direction truncation.",
}

__all__ = ["CMOEACD", "CMOEA_CD_DEFINITION", "constraint_pareto_mask", "make_cmoea_cd"]
