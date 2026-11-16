"""DSSEA dynamic subspace search evolutionary algorithm.

------------------------------------------------------------------------------------
Module: dssea.py
Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
Article: X. Ban et al., "A Dynamic Subspace Search-Based Evolutionary Algorithm
         for Large-Scale Constrained Multiobjective Optimization", IEEE
         Transactions on Cybernetics 55(5), 2486-2499, 2025.
Implementation: standalone NumPy implementation with exact SVD-based ALDVA,
                adaptive masks, DE/GA alternation and epsilon-SPEA2 survival.
Responsibility: constrained large-scale multi-objective optimization.
Author: Kristina Valevska, MSc Eng.
------------------------------------------------------------------------------------
"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional

import numpy as np
from scipy.spatial.distance import cdist

from .platypus_common import termination_generations
from .research_common import (
    PopulationState,
    ResearchMOOAlgorithm,
    assign_rank_and_crowding,
    non_dominated_fronts,
    polynomial_mutation,
    project_to_bounds,
    sbx_crossover,
)


def epsilon_spea2_fitness(F: np.ndarray, CV: np.ndarray, epsilon: float) -> np.ndarray:
    # SPEA2 strength, raw fitness and density under epsilon-constraint dominance.
    F = np.asarray(F, dtype=float)
    CV = np.asarray(CV, dtype=float).reshape(-1)
    effective = np.where(CV <= float(epsilon), 0.0, CV)
    objective_dominance = np.all(F[:, None] <= F[None, :], axis=2) & np.any(
        F[:, None] < F[None, :], axis=2
    )
    relation = np.where(
        effective[:, None] == effective[None, :],
        objective_dominance,
        effective[:, None] < effective[None, :],
    )
    np.fill_diagonal(relation, False)
    strength = relation.sum(axis=1)
    raw = relation.T @ strength
    if len(F) <= 1:
        return raw.astype(float)
    distances = cdist(F, F)
    np.fill_diagonal(distances, np.inf)
    neighbor = min(max(1, int(math.sqrt(len(F)))), len(F) - 1)
    kth = np.partition(distances, neighbor - 1, axis=1)[:, neighbor - 1]
    return raw + 1.0 / (kth + 2.0)


def epsilon_spea2_survival(
    X: np.ndarray,
    F: np.ndarray,
    CV: np.ndarray,
    count: int,
    epsilon: float,
) -> tuple[PopulationState, np.ndarray]:
    # Environmental selection and lexicographic SPEA2 truncation.
    fitness = epsilon_spea2_fitness(F, CV, epsilon)
    selected = list(np.flatnonzero(fitness < 1.0))
    if len(selected) < count:
        for index in np.argsort(fitness, kind="mergesort"):
            if int(index) not in selected:
                selected.append(int(index))
            if len(selected) == count:
                break
    while len(selected) > count:
        local = cdist(F[selected], F[selected])
        np.fill_diagonal(local, np.inf)
        profiles = np.sort(local, axis=1)
        victim = min(range(len(selected)), key=lambda i: tuple(profiles[i]))
        selected.pop(victim)
    selected = sorted(selected, key=lambda i: float(fitness[i]))
    ids = np.asarray(selected[:count], dtype=int)
    rank, crowding = assign_rank_and_crowding(F[ids], CV[ids])
    return PopulationState(X[ids], F[ids], CV[ids], rank, crowding), fitness[ids]


class DSSEA(ResearchMOOAlgorithm):
    # Dynamic subspace search-based EA for constrained large-scale MOO.

    def __init__(
        self,
        population_size: int = 100,
        n_sel: int = 2,
        n_per: int = 4,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=population_size,
            mutation_rate=0.1,
            seed=seed,
        )
        self.n_sel = int(n_sel)
        self.n_per = int(n_per)
        if self.n_sel < 1 or self.n_per < 2:
            raise ValueError("n_sel must be >= 1 and n_per must be >= 2")
        self.variable_ranks = np.empty(0, dtype=int)
        self.fitness = np.empty(0, dtype=float)
        self.epsilon0 = 100.0
        self.maximum_generations = 1

    def _aldva(self) -> np.ndarray:
        # Rank decision variables using the perturbation length and line angle from ALDVA.
        assert self.state is not None
        first_front = non_dominated_fronts(self.state.F)[0]
        reference = self.state.F[first_front]
        lower = np.min(reference, axis=0)
        upper = np.max(reference, axis=0)
        if np.any(np.isclose(upper, lower)):
            lower = np.zeros(self.n_obj)
            upper = np.ones(self.n_obj)
        lengths = np.zeros(self.n_var)
        angles = np.zeros(self.n_var)
        for dimension in range(self.n_var):
            chosen = self.random_state.integers(0, len(self.state.X), size=self.n_sel)
            decisions = np.repeat(self.state.X[chosen][None, :, :], self.n_per, axis=0)
            decisions[:, :, dimension] = self.random_state.uniform(
                self.xl[dimension], self.xu[dimension], size=(self.n_per, self.n_sel)
            )
            perturbed_F, _ = self.evaluate(decisions.reshape(-1, self.n_var))
            perturbed_F = perturbed_F.reshape(self.n_per, self.n_sel, self.n_obj)
            local_lengths = []
            local_angles = []
            for selected in range(self.n_sel):
                points = perturbed_F[:, selected, :]
                ordered = points[np.lexsort(tuple(points[:, i] for i in reversed(range(self.n_obj))))]
                local_lengths.append(float(np.linalg.norm(ordered[0] - ordered[-1])))
                normalized = (points - lower) / np.maximum(upper - lower, 1e-12)
                centered = normalized - np.mean(normalized, axis=0)
                _, _, vectors = np.linalg.svd(centered, full_matrices=False)
                vector = vectors[0]
                sine = abs(float(np.sum(vector))) / max(
                    np.linalg.norm(vector) * math.sqrt(self.n_obj), 1e-12
                )
                local_angles.append(math.degrees(math.asin(min(1.0, sine))))
            lengths[dimension] = float(np.mean(local_lengths))
            angles[dimension] = float(np.mean(local_angles))
        length_score = (lengths - lengths.min()) / max(float(np.ptp(lengths)), 1e-12)
        angle_score = (angles - angles.min()) / max(float(np.ptp(angles)), 1e-12)
        order = np.argsort(-(length_score + angle_score), kind="mergesort")
        ranks = np.empty(self.n_var, dtype=int)
        ranks[order] = np.arange(1, self.n_var + 1)
        return ranks

    def after_initialize(self) -> None:
        assert self.state is not None
        self.variable_ranks = self._aldva()
        self.epsilon0 = float(np.sum(self.state.CV))
        if self.epsilon0 <= 0.0:
            self.epsilon0 = 100.0
        self.fitness = epsilon_spea2_fitness(self.state.F, self.state.CV, self.epsilon0)

    def _active_variables(self) -> np.ndarray:
        if self.n_var == 1:
            initial = np.ones(1)
        else:
            initial = (self.variable_ranks - self.n_var) / (1.0 - self.n_var)
        progress = self.evaluator.n_eval / max(
            self.evaluator.n_eval + self.population_size * max(self.maximum_generations - self.n_gen, 1),
            1,
        )
        probability = (1.0 - initial) * np.tanh(9.0 * progress) + initial
        return self.random_state.random(self.n_var) <= probability

    def _pbest_offspring(self, active: np.ndarray) -> np.ndarray:
        assert self.state is not None
        count = len(self.state.X)
        ranked = np.argsort(self.fitness, kind="mergesort")
        pbest_count = max(2, int(round(0.1 * count)))
        children = np.empty_like(self.state.X)
        for i in range(count):
            others = np.delete(np.arange(count), i)
            r1, r2 = self.random_state.choice(others, size=2, replace=False)
            pbest = int(self.random_state.choice(ranked[:pbest_count]))
            weight = float(self.random_state.choice([0.6, 0.8, 1.0]))
            crossover = float(self.random_state.choice([0.1, 0.2, 1.0]))
            trial = self.state.X[i] + weight * (
                self.state.X[pbest] - self.state.X[i] + self.state.X[r1] - self.state.X[r2]
            )
            child = self.state.X[i].copy()
            mutate_mask = active & (self.random_state.random(self.n_var) < crossover)
            child[mutate_mask] = trial[mutate_mask]
            inactive = ~active
            if np.any(inactive):
                donors = self.random_state.integers(0, count, size=np.count_nonzero(inactive))
                child[inactive] = self.state.X[donors, np.flatnonzero(inactive)]
            children[i] = child
        return polynomial_mutation(
            project_to_bounds(children, self.xl, self.xu),
            self.xl,
            self.xu,
            20.0,
            1.0 / self.n_var,
            self.random_state,
        )

    def _ga_offspring(self, active: np.ndarray) -> np.ndarray:
        assert self.state is not None
        candidates = self.random_state.integers(0, len(self.state.X), size=(self.population_size, 2))
        winners = np.where(
            self.fitness[candidates[:, 0]] <= self.fitness[candidates[:, 1]],
            candidates[:, 0],
            candidates[:, 1],
        )
        pairs = np.column_stack((winners, np.roll(winners, -1)))
        children = sbx_crossover(
            self.state.X, pairs, self.xl, self.xu, 20.0, 1.0, self.random_state
        )
        children = polynomial_mutation(
            children, self.xl, self.xu, 20.0, 1.0 / self.n_var, self.random_state
        )
        inactive = ~active
        if np.any(inactive):
            donors = self.random_state.integers(
                0, len(self.state.X), size=(len(children), np.count_nonzero(inactive))
            )
            children[:, inactive] = self.state.X[donors, np.flatnonzero(inactive)]
        return children

    def step(self) -> None:
        if self.state is None:
            raise RuntimeError("Algorithm must be initialized before step().")
        previous = self.state
        active = self._active_variables()
        offspring = (
            self._pbest_offspring(active)
            if self.random_state.random() <= 0.5
            else self._ga_offspring(active)
        )
        offspring_F, offspring_CV = self.evaluate(offspring)
        progress = self.n_gen / max(self.maximum_generations, 1)
        exponent = (-math.log(self.epsilon0) - 6.0) / math.log(0.25)
        epsilon = self.epsilon0 * max(0.0, 1.0 - progress) ** exponent
        self.state, self.fitness = epsilon_spea2_survival(
            np.vstack((previous.X, offspring)),
            np.vstack((previous.F, offspring_F)),
            np.concatenate((previous.CV, offspring_CV)),
            self.population_size,
            epsilon,
        )
        self.archive = self.build_archive(self.state)
        self.n_gen += 1
        self._update_population_view()
        self._remember_state()

    def gui_minimize(self, *, problem: Any, termination: Any, **kwargs: Any):
        maximum = termination_generations(termination)
        self.maximum_generations = max(1, int(maximum)) if maximum is not None else 1000
        return super().gui_minimize(problem=problem, termination=termination, **kwargs)


def make_dssea(
    population_size: int = 100,
    n_sel: int = 2,
    n_per: int = 4,
    seed: int = 1,
) -> DSSEA:
    return DSSEA(population_size=population_size, n_sel=n_sel, n_per=n_per, seed=seed)


DSSEA_DEFINITION: Dict[str, Any] = {
    "label": "DSSEA",
    "factory": make_dssea,
    "implementation_type": "adapted_port",
    "reference": "X. Ban et al., IEEE Transactions on Cybernetics 55(5), 2486-2499 (2025)",
    "verified_against": "PlatEMO control flow, ALDVA and epsilon-SPEA2 mechanism tests; no claim of statistical equivalence",
    "requires_constraints": True,
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 4},
        "n_sel": {"default": 2, "kind": "int", "minimum": 1},
        "n_per": {"default": 4, "kind": "int", "minimum": 2},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": (
        "Standalone DSSEA for bounded real-valued constrained problems. Initialization includes "
        "D*n_sel*n_per ALDVA evaluations before the first GUI generation."
    ),
}


__all__ = ["DSSEA", "DSSEA_DEFINITION", "epsilon_spea2_fitness", "make_dssea"]
