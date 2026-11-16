# Standalone TS-NSGA-II implementation.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
# ------------------------------------------------------------------------------------
# Article: F. Ming, W. Gong, and L. Wang, "A Two-Stage Evolutionary Algorithm
#          With Balanced Convergence and Diversity for Many-Objective Optimization,"
#          IEEE Transactions on Systems, Man, and Cybernetics: Systems, 2022.
# DOI: 10.1109/TSMC.2022.3143657
# Implementation: own Python/NumPy implementation of SPD, LPD, restricted mating
#                 and the two-stage environmental selection defined in the article.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np

from .research_common import (
    FEASIBILITY_TOL,
    PopulationState,
    ResearchMOOAlgorithm,
    assign_rank_and_crowding,
    parse_positive_float,
    parse_positive_int,
    termination_generations,
)


def _rank_relation(relation: np.ndarray) -> np.ndarray:
    # Assign front numbers to an arbitrary strict dominance relation.
    relation = np.asarray(relation, dtype=bool).copy()
    np.fill_diagonal(relation, False)
    n = relation.shape[0]
    ranks = np.full(n, n, dtype=int)
    remaining = np.ones(n, dtype=bool)
    front = 0
    while np.any(remaining):
        ids = np.flatnonzero(remaining)
        incoming = np.sum(relation[np.ix_(ids, ids)], axis=0)
        chosen = ids[incoming == 0]
        if chosen.size == 0:
            chosen = ids[np.argmin(incoming) : np.argmin(incoming) + 1]
        ranks[chosen] = front
        remaining[chosen] = False
        front += 1
    return ranks


def _objective_geometry(
    objectives: np.ndarray,
    reference_vectors: np.ndarray,
    theta: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    # Compute M2M subregions and the d1, d2 and PBI quantities from Equations 2-6.
    F = np.asarray(objectives, dtype=float)
    normalized = (F - np.min(F, axis=0)) / np.maximum(np.ptp(F, axis=0), 1e-15)
    W = np.asarray(reference_vectors, dtype=float)
    W = W / np.maximum(np.linalg.norm(W, axis=1, keepdims=True), 1e-15)
    lengths = np.linalg.norm(normalized, axis=1, keepdims=True)
    cosine = normalized @ W.T / np.maximum(lengths, 1e-15)
    subregions = np.argmax(cosine, axis=1)
    selected_W = W[subregions]
    d1 = np.abs(np.sum(normalized * selected_W, axis=1))
    d2 = np.linalg.norm(normalized - d1[:, None] * selected_W, axis=1)
    return subregions, d1, d2, d1 + float(theta) * d2


def spd_ranks(
    objectives: np.ndarray,
    constraints: np.ndarray,
    reference_vectors: np.ndarray,
    theta: float = 5.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Rank by subregion PBI dominance (Definition 1).
    subregions, _, d2, pbi = _objective_geometry(objectives, reference_vectors, theta)
    relation = (subregions[:, None] == subregions[None, :]) & (pbi[:, None] < pbi[None, :])
    CV = np.asarray(constraints, dtype=float)
    relation |= (CV[:, None] <= FEASIBILITY_TOL) & (CV[None, :] > FEASIBILITY_TOL)
    both_infeasible = (CV[:, None] > FEASIBILITY_TOL) & (CV[None, :] > FEASIBILITY_TOL)
    relation |= both_infeasible & (CV[:, None] < CV[None, :])
    return _rank_relation(relation), d2, subregions


def lpd_ranks(
    objectives: np.ndarray,
    constraints: np.ndarray,
    division_level: int,
) -> np.ndarray:
    # Rank by level-based Pareto dominance (Definition 2, Equations 8-9).
    F = np.asarray(objectives, dtype=float)
    normalized = (F - np.min(F, axis=0)) / np.maximum(np.ptp(F, axis=0), 1e-15)
    intervals = np.minimum((normalized * division_level).astype(int), division_level - 1)
    levels = np.max(intervals, axis=1)
    pareto = np.all(F[:, None, :] <= F[None, :, :], axis=2) & np.any(
        F[:, None, :] < F[None, :, :], axis=2
    )
    equivalent = ~pareto & ~pareto.T
    relation = pareto | (equivalent & (levels[:, None] < levels[None, :]))
    CV = np.asarray(constraints, dtype=float)
    relation |= (CV[:, None] <= FEASIBILITY_TOL) & (CV[None, :] > FEASIBILITY_TOL)
    both_infeasible = (CV[:, None] > FEASIBILITY_TOL) & (CV[None, :] > FEASIBILITY_TOL)
    relation |= both_infeasible & (CV[:, None] < CV[None, :])
    return _rank_relation(relation)


def _snapshot(X: np.ndarray, F: np.ndarray, CV: np.ndarray, ranks: np.ndarray) -> PopulationState:
    # Expose article ranks while retaining a GUI-compatible crowding vector.
    _, crowding = assign_rank_and_crowding(F, CV)
    return PopulationState(X, F, CV, ranks, crowding)


class TSNSGA(ResearchMOOAlgorithm):
    """Two-stage NSGA-II for many-objective optimization."""

    def __init__(
        self,
        *,
        theta: float = 5.0,
        stage_parameter: float = 5.0,
        division_level: Optional[int] = None,
        automatic_mutation_rate: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.theta = parse_positive_float(theta, "theta")
        self.stage_parameter = parse_positive_float(stage_parameter, "stage_parameter")
        self.division_level_input = division_level
        self.automatic_mutation_rate = bool(automatic_mutation_rate)
        self.division_level = 1
        self.maximum_generations = 100
        self.stage = 1

    def gui_minimize(self, *, problem, termination, **kwargs):
        # Preserve the actual horizon used by the stage-switch equation.
        self.maximum_generations = termination_generations(termination) or 100
        return super().gui_minimize(problem=problem, termination=termination, **kwargs)

    def after_initialize(self) -> None:
        # The article uses polynomial mutation with probability 1 / n.
        if self.automatic_mutation_rate:
            self.mutation_rate = 1.0 / max(1, self.n_var)
        self.division_level = (
            parse_positive_int(self.division_level_input, "division_level")
            if self.division_level_input is not None
            else 2 * self.n_obj
        )

    def _current_stage(self) -> int:
        threshold = (1.0 - 3.0 / (self.stage_parameter * self.n_obj)) * self.maximum_generations
        return 1 if (self.n_gen + 1) < threshold else 2

    def _measures(self, F: np.ndarray, CV: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        assert self.reference_directions is not None
        vectors = self.reference_directions[: self.population_size]
        self.stage = self._current_stage()
        if self.stage == 1:
            ranks, d2, _ = spd_ranks(F, CV, vectors, self.theta)
            return ranks, d2
        ranks = lpd_ranks(F, CV, self.division_level)
        subregions, _, _, _ = _objective_geometry(F, vectors, self.theta)
        density = np.bincount(subregions, minlength=vectors.shape[0])[subregions].astype(float)
        return ranks, density

    def select(self) -> np.ndarray:
        # Apply the restricted mating selection from Algorithm 3.
        assert self.state is not None
        ranks, diversity = self._measures(self.state.F, self.state.CV)
        pairs = np.empty((self.population_size, 2), dtype=int)
        for row in range(self.population_size):
            contestants = self.random_state.integers(0, self.population_size, size=(2, 2))
            for col, (left, right) in enumerate(contestants):
                if ranks[left] < ranks[right]:
                    winner = left
                elif ranks[right] < ranks[left]:
                    winner = right
                elif diversity[left] < diversity[right]:
                    winner = left
                elif diversity[right] < diversity[left]:
                    winner = right
                else:
                    winner = left if self.random_state.random() < 0.5 else right
                pairs[row, col] = winner
        return pairs

    def environmental_selection(self, X, F, CV, n_survive):
        # Apply Algorithm 2 with d2 truncation in stage 1 and vector selection in stage 2.
        assert self.reference_directions is not None
        vectors = self.reference_directions[: self.population_size]
        self.stage = self._current_stage()
        if self.stage == 1:
            ranks, d2, _ = spd_ranks(F, CV, vectors, self.theta)
        else:
            ranks = lpd_ranks(F, CV, self.division_level)
            d2 = np.zeros(len(F))

        selected: list[int] = []
        split: list[int] = []
        for front in np.unique(ranks):
            ids = np.flatnonzero(ranks == front).tolist()
            if len(selected) + len(ids) <= n_survive:
                selected.extend(ids)
            else:
                split = ids
                break

        if len(selected) < n_survive:
            pool = selected + split
            if self.stage == 1:
                remaining = sorted(split, key=lambda idx: d2[idx])
                selected.extend(remaining[: n_survive - len(selected)])
            else:
                Fp = np.asarray(F)[pool]
                normalized = (Fp - np.min(Fp, axis=0)) / np.maximum(np.ptp(Fp, axis=0), 1e-15)
                W = vectors / np.maximum(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-15)
                unit = normalized / np.maximum(np.linalg.norm(normalized, axis=1, keepdims=True), 1e-15)
                distance = 1.0 - unit @ W.T
                available = list(range(len(pool)))
                chosen: list[int] = []
                for direction in range(min(len(W), n_survive)):
                    if not available:
                        break
                    local = min(available, key=lambda idx: distance[idx, direction])
                    chosen.append(pool[local])
                    available.remove(local)
                if len(chosen) < n_survive:
                    remainder = sorted((pool[idx] for idx in available), key=lambda idx: ranks[idx])
                    chosen.extend(remainder[: n_survive - len(chosen)])
                selected = chosen[:n_survive]

        ids = np.asarray(selected[:n_survive], dtype=int)
        return _snapshot(np.asarray(X)[ids], np.asarray(F)[ids], np.asarray(CV)[ids], ranks[ids])


def make_ts_nsga(
    population_size: int = 100,
    crossover_rate: float = 1.0,
    mutation_rate: Optional[float] = None,
    theta: float = 5.0,
    stage_parameter: float = 5.0,
    division_level: Optional[int] = None,
    n_partitions: int = 12,
    seed: int = 1,
) -> TSNSGA:
    # Create the article-defined TS-NSGA-II algorithm.
    return TSNSGA(
        population_size=population_size,
        archive_size=population_size,
        crossover_rate=crossover_rate,
        mutation_rate=0.1 if mutation_rate is None else mutation_rate,
        automatic_mutation_rate=mutation_rate is None,
        crossover_eta=20.0,
        mutation_eta=20.0,
        theta=theta,
        stage_parameter=stage_parameter,
        division_level=division_level,
        n_partitions=n_partitions,
        seed=seed,
    )


TS_NSGA_DEFINITION: Dict[str, Any] = {
    "label": "TS-NSGA-II",
    "factory": make_ts_nsga,
    "implementation_type": "adapted_port",
    "reference": "F. Ming, W. Gong and L. Wang, IEEE TSMC: Systems 52(10), 6222-6234 (2022), DOI 10.1109/TSMC.2022.3143657",
    "verified_against": "SPD, LPD, stage-switch, mating and environmental-selection mechanism tests; no claim of statistical equivalence",
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 2},
        "crossover_rate": {"default": 1.0, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": None, "kind": "float", "minimum": 0.0, "maximum": 1.0, "tooltip": "Defaults to 1 / number of variables, as in the article."},
        "theta": {"default": 5.0, "kind": "float", "minimum": 1e-9},
        "stage_parameter": {"default": 5.0, "kind": "float", "minimum": 1e-9},
        "division_level": {"default": None, "kind": "int", "minimum": 1, "tooltip": "Defaults to twice the number of objectives."},
        "n_partitions": {"default": 12, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Article-defined TS-NSGA-II using SPD in stage 1 and LPD in stage 2.",
}
