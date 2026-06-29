# GDE3 implementation and GUI factory definition.
#
# ------------------------------------------------------------------------------------
# Module: gde3.py
# Summary: GDE3 mutation, selection, population reduction and GUI factory definition.
# Implementation: article-style DE/rand/1/bin offspring are pairwise compared to parents and incomparable feasible pairs are both preserved.
# Responsibility: adds a constrained multiobjective differential-evolution baseline for dissertation experiments.
# Author: Kristina Valevska, MSc Eng.
# Implementation source: based on Kukkonen, S., Lampinen, J. "GDE3: The third evolution step of generalized differential evolution" (CEC 2005).
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

from .research_common import (
    FEASIBILITY_TOL,
    PopulationState,
    ResearchMOOAlgorithm,
    assign_rank_and_crowding,
    crowding_distance,
    feasible_mask,
    parse_positive_float,
    parse_probability,
    project_to_bounds,
)


def _dominates(lhs: np.ndarray, rhs: np.ndarray) -> bool:
    # Return whether lhs dominates rhs in objective space for minimization.
    return bool(np.all(lhs <= rhs + FEASIBILITY_TOL) and np.any(lhs < rhs - FEASIBILITY_TOL))


def _weakly_constraint_dominates(lhs_f: np.ndarray, lhs_cv: float, rhs_f: np.ndarray, rhs_cv: float) -> bool:
    # Apply the GDE3 pairwise selection rule with constraints.
    lhs_feasible = float(lhs_cv) <= FEASIBILITY_TOL
    rhs_feasible = float(rhs_cv) <= FEASIBILITY_TOL
    if lhs_feasible and not rhs_feasible:
        return True
    if rhs_feasible and not lhs_feasible:
        return False
    if not lhs_feasible and not rhs_feasible:
        return float(lhs_cv) <= float(rhs_cv) + FEASIBILITY_TOL
    return bool(np.all(lhs_f <= rhs_f + FEASIBILITY_TOL))


def _parse_de_weight(value: Any, field_name: str) -> float:
    # Parse the DE differential weight F from the interval (0, 1].
    parsed = parse_positive_float(value, field_name)
    if parsed > 1.0:
        raise ValueError(f"{field_name} must be <= 1.0, got {parsed}")
    return parsed


class GDE3(ResearchMOOAlgorithm):
    # Article-style GDE3 using DE/rand/1/bin and constrained nondominated reduction.

    def __init__(
        self,
        pop_size: int = 100,
        f_weight: float = 0.5,
        crossover_rate: float = 0.3,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=pop_size,
            archive_size=pop_size,
            crossover_rate=crossover_rate,
            mutation_rate=0.0,
            seed=seed,
        )
        self.f_weight = _parse_de_weight(f_weight, "f_weight")

    def _trial_population(self) -> np.ndarray:
        # Generate DE/rand/1/bin trial vectors for all current population members.
        assert self.state is not None
        X = np.asarray(self.state.X, dtype=float)
        n_pop, n_var = X.shape
        children = np.zeros_like(X)
        indices = np.arange(n_pop)

        for i in range(n_pop):
            pool = np.delete(indices, i)
            r1, r2, r3 = self.random_state.choice(pool, size=3, replace=False)
            mutant = X[r3] + self.f_weight * (X[r1] - X[r2])
            trial = X[i].copy()
            j_rand = int(self.random_state.integers(0, n_var))
            mask = self.random_state.random(n_var) < self.crossover_rate
            mask[j_rand] = True
            trial[mask] = mutant[mask]
            children[i] = trial
        return project_to_bounds(children, self.xl, self.xu)

    def _pruning_crowding(self, F: np.ndarray, n_survive: int) -> np.ndarray:
        # Iteratively prune the most crowded members from one nondominated front.
        active = list(range(F.shape[0]))
        while len(active) > int(n_survive):
            active_arr = np.asarray(active, dtype=int)
            cd = crowding_distance(F[active_arr])
            worst_local = np.flatnonzero(cd == np.min(cd))
            if worst_local.size > 1:
                sums = np.sum(F[active_arr[worst_local]], axis=1)
                worst = int(worst_local[np.argmax(sums)])
            else:
                worst = int(worst_local[0])
            del active[worst]
        return np.asarray(active, dtype=int)

    def _reduce_population(
        self,
        X: np.ndarray,
        F: np.ndarray,
        CV: np.ndarray,
        n_survive: int,
    ) -> PopulationState:
        # Reduce a mixed parent-trial population back to the original size.
        X = np.asarray(X, dtype=float)
        F = np.asarray(F, dtype=float)
        CV = np.asarray(CV, dtype=float).reshape(-1)
        feasible = feasible_mask(CV)
        feasible_idx = np.flatnonzero(feasible)
        selected: list[int] = []

        if feasible_idx.size:
            fronts = NonDominatedSorting().do(F[feasible_idx], only_non_dominated_front=False)
            for front in fronts:
                actual = feasible_idx[np.asarray(front, dtype=int)]
                if len(selected) + actual.size <= int(n_survive):
                    selected.extend(actual.tolist())
                    continue
                remaining = int(n_survive) - len(selected)
                keep_local = self._pruning_crowding(F[actual], remaining)
                selected.extend(actual[keep_local].tolist())
                break

        if len(selected) < int(n_survive):
            infeasible_idx = np.flatnonzero(~feasible)
            infeasible_order = infeasible_idx[np.argsort(CV[infeasible_idx], kind="mergesort")]
            selected.extend(infeasible_order[: int(n_survive) - len(selected)].tolist())

        chosen = np.asarray(selected[: int(n_survive)], dtype=int)
        rank, crowding = assign_rank_and_crowding(F[chosen], CV[chosen])
        return PopulationState(X=X[chosen], F=F[chosen], CV=CV[chosen], rank=rank, crowding=crowding)

    def step(self) -> None:
        # Execute one GDE3 generation with pairwise DE selection and optional population reduction.
        if self.state is None:
            raise RuntimeError("Algorithm must be initialized before step().")

        previous = self.state
        trials = self._trial_population()
        trial_F, trial_CV = self.evaluate(trials)

        kept_X: list[np.ndarray] = []
        kept_F: list[np.ndarray] = []
        kept_CV: list[float] = []
        extras_X: list[np.ndarray] = []
        extras_F: list[np.ndarray] = []
        extras_CV: list[float] = []

        for i in range(previous.X.shape[0]):
            parent_x = previous.X[i]
            parent_f = previous.F[i]
            parent_cv = float(previous.CV[i])
            trial_x = trials[i]
            child_f = trial_F[i]
            child_cv = float(trial_CV[i])

            if _weakly_constraint_dominates(child_f, child_cv, parent_f, parent_cv):
                kept_X.append(trial_x)
                kept_F.append(child_f)
                kept_CV.append(child_cv)
                continue

            kept_X.append(parent_x)
            kept_F.append(parent_f)
            kept_CV.append(parent_cv)

            both_feasible = parent_cv <= FEASIBILITY_TOL and child_cv <= FEASIBILITY_TOL
            if both_feasible and not _dominates(parent_f, child_f) and not _dominates(child_f, parent_f):
                extras_X.append(trial_x)
                extras_F.append(child_f)
                extras_CV.append(child_cv)

        candidate_X = np.asarray(kept_X, dtype=float)
        candidate_F = np.asarray(kept_F, dtype=float)
        candidate_CV = np.asarray(kept_CV, dtype=float)
        if extras_X:
            candidate_X = np.vstack([candidate_X, np.asarray(extras_X, dtype=float)])
            candidate_F = np.vstack([candidate_F, np.asarray(extras_F, dtype=float)])
            candidate_CV = np.concatenate([candidate_CV, np.asarray(extras_CV, dtype=float)])

        self.state = self._reduce_population(candidate_X, candidate_F, candidate_CV, self.population_size)
        self.archive = self.build_archive(self.state)
        self.n_gen += 1
        self._update_population_view()
        self._remember_state()
        self.after_generation(previous, self.state)


def make_gde3(
    pop_size: int = 100,
    f_weight: float = 0.5,
    crossover_rate: float = 0.3,
    seed: int = 1,
) -> GDE3:
    # Create a configured GDE3 instance for the GUI registry.
    return GDE3(
        pop_size=pop_size,
        f_weight=f_weight,
        crossover_rate=parse_probability(crossover_rate, "crossover_rate"),
        seed=seed,
    )


GDE3_DEFINITION: Dict[str, Any] = {
    "label": "GDE3",
    "factory": make_gde3,
    "form_fields": {
        "pop_size": {"default": 100, "kind": "int", "minimum": 4},
        "f_weight": {"default": 0.5, "kind": "float", "minimum": 1e-9, "maximum": 1.0},
        "crossover_rate": {"default": 0.3, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "GDE3 z CEC 2005: DE/rand/1/bin, zachowanie obu rozwiazan gdy sa wykonalne i wzajemnie sie nie dominuja, a potem redukcja przez constrained sorting i crowding.",
}
GDE3_DEFINITION["form_note"] = (
    "GDE3 from CEC 2005: DE/rand/1/bin, keeps both solutions when they are feasible and mutually non-dominating, "
    "then reduces by constrained sorting and crowding."
)
