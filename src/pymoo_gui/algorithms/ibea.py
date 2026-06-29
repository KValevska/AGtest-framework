# Adaptive IBEA-epsilon+ implementation and GUI factory definition.
#
# ------------------------------------------------------------------------------------
# Module: ibea.py
# Summary: adaptive IBEA fitness assignment, environmental selection, mating and GUI factory.
# Implementation: article-style indicator-based selection uses the additive epsilon+ indicator with adaptive scaling.
# Responsibility: adds a quality-indicator-driven MOEA for dissertation experiments.
# Author: Kristina Valevska, MSc Eng.
# Implementation source: based on Zitzler, E., Künzli, S. "Indicator-Based Selection in Multiobjective Search" (PPSN VIII, 2004).
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .research_common import (
    FEASIBILITY_TOL,
    PopulationState,
    ResearchMOOAlgorithm,
    assign_rank_and_crowding,
    feasible_mask,
    parse_positive_float,
    parse_probability,
)


def _normalize_objectives(F: np.ndarray) -> np.ndarray:
    # Scale each objective to [0, 1] as in adaptive IBEA.
    F = np.asarray(F, dtype=float)
    if F.shape[0] == 0:
        return np.empty_like(F)
    lower = np.min(F, axis=0)
    upper = np.max(F, axis=0)
    span = np.where(upper > lower, upper - lower, 1.0)
    return (F - lower) / span


def _epsilon_plus_indicator(F: np.ndarray) -> np.ndarray:
    # Return singleton additive epsilon+ indicator values I({x_i}, {x_j}).
    return np.max(F[:, None, :] - F[None, :, :], axis=2)


def _indicator_scale(indicator: np.ndarray) -> float:
    # Return the adaptive absolute indicator scale c used by IBEA.
    if indicator.shape[0] <= 1:
        return 1.0
    mask = ~np.eye(indicator.shape[0], dtype=bool)
    scale = float(np.max(np.abs(indicator[mask])))
    return scale if scale > 1e-12 else 1.0


def _fitness_from_indicator(indicator: np.ndarray, kappa: float, scale: float) -> np.ndarray:
    # Compute article-style IBEA fitness values from pairwise indicator values.
    if indicator.shape[0] == 0:
        return np.zeros(0, dtype=float)
    denom = max(float(scale) * float(kappa), 1e-12)
    contribution = -np.exp(-indicator / denom)
    np.fill_diagonal(contribution, 0.0)
    return np.sum(contribution, axis=0)


class IBEA(ResearchMOOAlgorithm):
    # Adaptive IBEA using the additive epsilon+ indicator from the original paper.

    def __init__(
        self,
        pop_size: int = 100,
        kappa: float = 0.05,
        crossover_rate: float = 1.0,
        mutation_rate: float = 0.01,
        crossover_eta: float = 20.0,
        mutation_eta: float = 20.0,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=pop_size,
            archive_size=pop_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            crossover_eta=crossover_eta,
            mutation_eta=mutation_eta,
            seed=seed,
        )
        self.kappa = parse_positive_float(kappa, "kappa")
        self._selection_fitness = np.zeros(self.population_size, dtype=float)

    def _fitness_for_population(self, F: np.ndarray) -> np.ndarray:
        # Calculate adaptive IBEA fitness values for one feasible population.
        normalized = _normalize_objectives(np.asarray(F, dtype=float))
        indicator = _epsilon_plus_indicator(normalized)
        scale = _indicator_scale(indicator)
        return _fitness_from_indicator(indicator, self.kappa, scale)

    def _select_feasible_by_ibea(self, F: np.ndarray, n_survive: int) -> tuple[np.ndarray, np.ndarray]:
        # Iteratively remove the worst feasible individual and update fitness values.
        if F.shape[0] <= int(n_survive):
            fitness = self._fitness_for_population(F)
            order = np.lexsort((np.arange(F.shape[0]), -fitness))
            return order.astype(int, copy=False), fitness[order]

        normalized = _normalize_objectives(F)
        indicator = _epsilon_plus_indicator(normalized)
        scale = _indicator_scale(indicator)
        denom = max(scale * self.kappa, 1e-12)
        fitness = _fitness_from_indicator(indicator, self.kappa, scale)
        active = list(range(F.shape[0]))

        while len(active) > int(n_survive):
            active_arr = np.asarray(active, dtype=int)
            worst_local = int(np.argmin(fitness[active_arr]))
            worst = int(active_arr[worst_local])
            del active[worst_local]
            if active:
                remaining = np.asarray(active, dtype=int)
                fitness[remaining] += np.exp(-indicator[worst, remaining] / denom)

        active_arr = np.asarray(active, dtype=int)
        order = np.lexsort((active_arr, -fitness[active_arr]))
        selected = active_arr[order]
        return selected.astype(int, copy=False), fitness[selected]

    def select(self) -> np.ndarray:
        # Perform binary tournament selection using IBEA fitness on feasible solutions.
        assert self.state is not None
        n = self.state.X.shape[0]
        parents = np.zeros((self.population_size, 2), dtype=int)
        feasible = self.state.CV <= FEASIBILITY_TOL

        for i in range(self.population_size):
            for j in range(2):
                a, b = self.random_state.integers(0, n, size=2)
                winner = int(a)
                if feasible[a] and not feasible[b]:
                    winner = int(a)
                elif feasible[b] and not feasible[a]:
                    winner = int(b)
                elif not feasible[a] and not feasible[b]:
                    if self.state.CV[a] > self.state.CV[b]:
                        winner = int(b)
                    elif self.state.CV[b] > self.state.CV[a]:
                        winner = int(a)
                    else:
                        winner = int(a if self.random_state.random() < 0.5 else b)
                else:
                    fit_a = float(self._selection_fitness[a])
                    fit_b = float(self._selection_fitness[b])
                    if fit_a > fit_b:
                        winner = int(a)
                    elif fit_b > fit_a:
                        winner = int(b)
                    else:
                        winner = int(a if self.random_state.random() < 0.5 else b)
                parents[i, j] = winner
        return parents

    def environmental_selection(
        self,
        X: np.ndarray,
        F: np.ndarray,
        CV: np.ndarray,
        n_survive: int,
    ) -> PopulationState:
        # Apply adaptive IBEA on feasible solutions and CV-based fallback for infeasible ones.
        X = np.asarray(X, dtype=float)
        F = np.asarray(F, dtype=float)
        CV = np.asarray(CV, dtype=float).reshape(-1)
        feasible_idx = np.flatnonzero(feasible_mask(CV))

        selected: list[int] = []
        if feasible_idx.size >= int(n_survive):
            chosen_local, feasible_fitness = self._select_feasible_by_ibea(F[feasible_idx], int(n_survive))
            chosen = feasible_idx[chosen_local]
            selected.extend(chosen.tolist())
            selection_fitness = feasible_fitness
        else:
            selected.extend(feasible_idx.tolist())
            infeasible_idx = np.flatnonzero(~feasible_mask(CV))
            order = infeasible_idx[np.argsort(CV[infeasible_idx], kind="mergesort")]
            need = int(n_survive) - len(selected)
            chosen_infeasible = order[:need]
            selected.extend(chosen_infeasible.tolist())
            selection_fitness = np.concatenate(
                [
                    self._fitness_for_population(F[feasible_idx]) if feasible_idx.size else np.zeros(0, dtype=float),
                    np.full(chosen_infeasible.shape[0], -np.inf, dtype=float),
                ]
            )

        chosen = np.asarray(selected, dtype=int)
        rank, crowding = assign_rank_and_crowding(F[chosen], CV[chosen])
        self._selection_fitness = np.asarray(selection_fitness, dtype=float)
        return PopulationState(
            X=X[chosen],
            F=F[chosen],
            CV=CV[chosen],
            rank=rank,
            crowding=crowding,
        )


def make_ibea(
    pop_size: int = 100,
    kappa: float = 0.05,
    crossover_rate: float = 1.0,
    mutation_rate: float = 0.01,
    crossover_eta: float = 20.0,
    mutation_eta: float = 20.0,
    seed: int = 1,
) -> IBEA:
    # Create a configured adaptive IBEA-epsilon+ instance for the GUI registry.
    return IBEA(
        pop_size=pop_size,
        kappa=kappa,
        crossover_rate=parse_probability(crossover_rate, "crossover_rate"),
        mutation_rate=parse_probability(mutation_rate, "mutation_rate"),
        crossover_eta=parse_positive_float(crossover_eta, "crossover_eta"),
        mutation_eta=parse_positive_float(mutation_eta, "mutation_eta"),
        seed=seed,
    )


IBEA_DEFINITION: Dict[str, Any] = {
    "label": "IBEA",
    "factory": make_ibea,
    "form_fields": {
        "pop_size": {"default": 100, "kind": "int", "minimum": 1},
        "kappa": {"default": 0.05, "kind": "float", "minimum": 1e-9},
        "crossover_rate": {"default": 1.0, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.01, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "crossover_eta": {"default": 20.0, "kind": "float", "minimum": 1e-6},
        "mutation_eta": {"default": 20.0, "kind": "float", "minimum": 1e-6},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Adaptive IBEA z additive epsilon+ indicator zgodnie z PPSN VIII (2004).",
}
IBEA_DEFINITION["form_note"] = "Adaptive IBEA with the additive epsilon+ indicator, following PPSN VIII (2004)."
