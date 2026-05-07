# ------------------------------------------------------------------------------------
# File: ts_nsga.py
# Contents: two-stage NSGA variants, factories and GUI registry definitions.
# What happens here: baseline NSGA-style evolution is extended with a second local-search stage around elite regions.
# Role in the framework: adds TS-NSGA and TS-NSGA-III article-inspired variants for comparative experiments.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on the article.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

from .research_common import (
    PopulationState,
    ResearchMOOAlgorithm,
    associate_to_reference_directions,
    assign_rank_and_crowding,
    feasible_mask,
    parse_positive_float,
    parse_probability,
    stable_survivor_order,
)


class TSNSGA(ResearchMOOAlgorithm):
    """
    EN:
    TS-NSGA with a second local-search stage around archived elites.
    Implementation source: own implementation based on the article.
    PL:
    TS-NSGA z drugim etapem lokalnego przeszukiwania wokol elit archiwum.
    """

    def __init__(
        self,
        population_size: int = 100,
        archive_size: int = 100,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        stage_fraction: float = 0.3,
        local_search_scale: float = 0.15,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=archive_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            seed=seed,
        )
        self.stage_fraction = parse_probability(stage_fraction, "stage_fraction")
        self.local_search_scale = parse_positive_float(local_search_scale, "local_search_scale")

    def guided_candidates(self) -> np.ndarray:
        """
        EN:
        Perform the second stage by locally perturbing elite archived solutions.

        PL:
        Wykonuje drugi etap przez lokalne perturbacje elit z archiwum.
        """
        count = int(round(self.population_size * self.stage_fraction))
        if count <= 0:
            return np.empty((0, self.n_var), dtype=float)
        elites = self.archive_elites(max(2, count))
        if elites.shape[0] == 0:
            return np.empty((0, self.n_var), dtype=float)
        base = elites[self.random_state.integers(0, elites.shape[0], size=count)]
        spread = self.state_spread() * self.local_search_scale
        guided = base + self.random_state.normal(0.0, 1.0, size=(count, self.n_var)) * spread[None, :]
        return np.clip(guided, self.xl, self.xu)


class TSNSGA3(TSNSGA):
    """
    EN:
    TS-NSGA-III with reference-direction niching on the truncation front.
    Implementation source: own implementation based on the article.
    PL:
    TS-NSGA-III z nichingiem opartym o kierunki odniesienia.
    """

    def __init__(
        self,
        population_size: int = 120,
        archive_size: int = 120,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        stage_fraction: float = 0.3,
        local_search_scale: float = 0.15,
        n_partitions: int = 12,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=archive_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            stage_fraction=stage_fraction,
            local_search_scale=local_search_scale,
            seed=seed,
        )
        self.n_partitions = int(n_partitions)

    def environmental_selection(self, X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> PopulationState:
        """
        EN:
        Use NSGA-III-style reference-direction truncation after the TS local-search stage.

        PL:
        Uzywa obcinania w stylu NSGA-III po drugim etapie lokalnego przeszukiwania.
        """
        rank, crowding = assign_rank_and_crowding(F, CV)
        feasible_idx = np.flatnonzero(feasible_mask(CV))
        selected: list[int] = []

        if feasible_idx.size >= int(n_survive):
            fronts = NonDominatedSorting().do(F[feasible_idx], only_non_dominated_front=False)
            for front in fronts:
                actual = feasible_idx[np.asarray(front, dtype=int)]
                if len(selected) + actual.size <= int(n_survive):
                    selected.extend(actual.tolist())
                    continue
                remaining = int(n_survive) - len(selected)
                association, distance = associate_to_reference_directions(F[actual], self.reference_directions)
                used_dirs: set[int] = set()
                while len(selected) < int(n_survive):
                    available = [
                        idx for idx in range(actual.size)
                        if int(actual[idx]) not in selected and (int(association[idx]) not in used_dirs or len(used_dirs) >= self.reference_directions.shape[0])
                    ]
                    if not available:
                        break
                    best_local = min(available, key=lambda idx: (distance[idx], rank[int(actual[idx])], -crowding[int(actual[idx])]))
                    selected.append(int(actual[best_local]))
                    used_dirs.add(int(association[best_local]))
                break
        else:
            selected.extend(feasible_idx.tolist())

        if len(selected) < int(n_survive):
            fallback = stable_survivor_order(rank, crowding, CV)
            for idx in fallback:
                idx = int(idx)
                if idx not in selected:
                    selected.append(idx)
                if len(selected) >= int(n_survive):
                    break

        chosen = np.asarray(selected[: int(n_survive)], dtype=int)
        return PopulationState(X=X[chosen], F=F[chosen], CV=CV[chosen], rank=rank[chosen], crowding=crowding[chosen])


def make_ts_nsga(
    population_size: int = 100,
    archive_size: int = 100,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.1,
    stage_fraction: float = 0.3,
    local_search_scale: float = 0.15,
    seed: int = 1,
) -> TSNSGA:
    """
    EN:
    Create a TS-NSGA instance for the GUI registry.

    PL:
    Tworzy instancje TS-NSGA dla rejestru GUI.
    """
    return TSNSGA(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        stage_fraction=stage_fraction,
        local_search_scale=local_search_scale,
        seed=seed,
    )


def make_ts_nsga3(
    population_size: int = 120,
    archive_size: int = 120,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.1,
    stage_fraction: float = 0.3,
    local_search_scale: float = 0.15,
    n_partitions: int = 12,
    seed: int = 1,
) -> TSNSGA3:
    """
    EN:
    Create a TS-NSGA-III instance for the GUI registry.

    PL:
    Tworzy instancje TS-NSGA-III dla rejestru GUI.
    """
    return TSNSGA3(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        stage_fraction=stage_fraction,
        local_search_scale=local_search_scale,
        n_partitions=n_partitions,
        seed=seed,
    )


TS_NSGA_DEFINITION: Dict[str, Any] = {
    "label": "TS-NSGA",
    "factory": make_ts_nsga,
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 1},
        "archive_size": {"default": 100, "kind": "int", "minimum": 1},
        "crossover_rate": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "stage_fraction": {"default": 0.3, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "local_search_scale": {"default": 0.15, "kind": "float", "minimum": 1e-6},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Own implementation based on the article. Base part: NSGA-style rank/crowding. TS part: second local-search stage around elites.",
}


TS_NSGA3_DEFINITION: Dict[str, Any] = {
    "label": "TS-NSGA-III",
    "factory": make_ts_nsga3,
    "form_fields": {
        "population_size": {"default": 120, "kind": "int", "minimum": 1},
        "archive_size": {"default": 120, "kind": "int", "minimum": 1},
        "crossover_rate": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "stage_fraction": {"default": 0.3, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "local_search_scale": {"default": 0.15, "kind": "float", "minimum": 1e-6},
        "n_partitions": {"default": 12, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Own implementation based on the article. Base part: reference-direction niching. TS part: second local-search stage around elites.",
}
