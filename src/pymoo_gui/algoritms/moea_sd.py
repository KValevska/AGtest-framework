# ------------------------------------------------------------------------------------
# File: moea_sd.py
# Contents: MOEA-SD class, shifted-density survival, factory and GUI registry definition.
# What happens here: feasible fronts are combined with reference-direction association and shifted-density estimates.
# Role in the framework: adds a decomposition-and-density-based many-objective optimizer.
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
    shifted_density,
    stable_survivor_order,
)


class MOEASD(ResearchMOOAlgorithm):
    """
    EN:
    MOEA-SD with reference-direction guidance and shifted-density truncation.
    Implementation source: own implementation based on the article.
    PL:
    MOEA-SD z kierunkami odniesienia i selekcja oparta na shifted density.
    """

    def __init__(
        self,
        population_size: int = 120,
        archive_size: int = 120,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        density_weight: float = 0.4,
        n_partitions: int = 12,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=archive_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            n_partitions=n_partitions,
            seed=seed,
        )
        self.density_weight = parse_positive_float(density_weight, "density_weight")

    def environmental_selection(self, X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> PopulationState:
        """
        EN:
        Select survivors by fronts and shifted-density-aware niching on the truncation front.

        PL:
        Wybiera osobniki na podstawie frontow oraz shifted density na froncie obcinanym.
        """
        rank, crowding = assign_rank_and_crowding(F, CV)
        feasible = feasible_mask(CV)
        feasible_idx = np.flatnonzero(feasible)
        selected: list[int] = []

        if feasible_idx.size >= int(n_survive):
            fronts = NonDominatedSorting().do(F[feasible_idx], only_non_dominated_front=False)
            for front in fronts:
                actual = feasible_idx[np.asarray(front, dtype=int)]
                if len(selected) + actual.size <= int(n_survive):
                    selected.extend(actual.tolist())
                    continue

                remaining = int(n_survive) - len(selected)
                association, perpendicular = associate_to_reference_directions(F[actual], self.reference_directions)
                density = shifted_density(F[actual])
                score = -(perpendicular + self.density_weight * density)

                used = set()
                for direction_id in np.unique(association):
                    bucket = np.flatnonzero(association == direction_id)
                    if bucket.size == 0:
                        continue
                    best_local = bucket[int(np.argmax(score[bucket]))]
                    candidate = int(actual[best_local])
                    if candidate not in used:
                        used.add(candidate)
                        selected.append(candidate)
                        if len(selected) >= int(n_survive):
                            break

                if len(selected) < int(n_survive):
                    order = np.argsort(score)[::-1]
                    for local_idx in order:
                        candidate = int(actual[local_idx])
                        if candidate in used:
                            continue
                        used.add(candidate)
                        selected.append(candidate)
                        if len(selected) >= int(n_survive):
                            break
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


def make_moea_sd(
    population_size: int = 120,
    archive_size: int = 120,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.1,
    density_weight: float = 0.4,
    n_partitions: int = 12,
    seed: int = 1,
) -> MOEASD:
    """
    EN:
    Create an MOEA-SD instance for the GUI registry.

    PL:
    Tworzy instancje MOEA-SD dla rejestru GUI.
    """
    return MOEASD(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        density_weight=density_weight,
        n_partitions=n_partitions,
        seed=seed,
    )


MOEA_SD_DEFINITION: Dict[str, Any] = {
    "label": "MOEA-SD",
    "factory": make_moea_sd,
    "form_fields": {
        "population_size": {"default": 120, "kind": "int", "minimum": 1},
        "archive_size": {"default": 120, "kind": "int", "minimum": 1},
        "crossover_rate": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "density_weight": {"default": 0.4, "kind": "float", "minimum": 1e-6},
        "n_partitions": {"default": 12, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Own implementation based on the article. Separates NSGA-II-style ranking from MOEA-SD shifted-density truncation.",
}
