# ------------------------------------------------------------------------------------
# File: sea.py
# Contents: entropy-aware SEA class, factory and GUI registry definition.
# What happens here: front truncation favors sparse objective-space regions measured by local entropy-like distances.
# Role in the framework: adds a sparsity- and entropy-aware MOEA variant under the SEA label.
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
    assign_rank_and_crowding,
    feasible_mask,
    normalized_objectives,
    parse_positive_float,
    stable_survivor_order,
)


def local_entropy_score(F: np.ndarray, k: int = 5) -> np.ndarray:
    """
    EN:
    Approximate objective-space entropy from k-nearest-neighbor distances.

    PL:
    Przybliza entropie w przestrzeni celow przez odleglosci do najblizszych sasiadow.
    """
    if F.shape[0] == 0:
        return np.zeros(0, dtype=float)
    Fn, _, _ = normalized_objectives(F)
    distances = np.linalg.norm(Fn[:, None, :] - Fn[None, :, :], axis=2)
    distances += np.eye(F.shape[0]) * np.inf
    k = max(1, min(int(k), F.shape[0] - 1)) if F.shape[0] > 1 else 1
    nearest = np.sort(distances, axis=1)[:, :k]
    return np.mean(np.log1p(nearest), axis=1)


class SEA(ResearchMOOAlgorithm):
    """
    EN:
    SEA with entropy-aware truncation on the last surviving front.
    Implementation source: own implementation based on the article.
    PL:
    SEA z obcinaniem frontu opartym na lokalnej entropii.
    """

    def __init__(
        self,
        population_size: int = 100,
        archive_size: int = 100,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        entropy_weight: float = 0.5,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=archive_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            seed=seed,
        )
        self.entropy_weight = parse_positive_float(entropy_weight, "entropy_weight")

    def environmental_selection(self, X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> PopulationState:
        """
        EN:
        Select survivors by fronts and local entropy on the truncation front.

        PL:
        Wybiera osobniki przez fronty Pareto i lokalna entropie na froncie obcinanym.
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
                entropy = local_entropy_score(F[actual])
                score = crowding[actual] + self.entropy_weight * entropy
                order = np.argsort(score)[::-1]
                selected.extend(actual[order[:remaining]].tolist())
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


def make_sea(
    population_size: int = 100,
    archive_size: int = 100,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.1,
    entropy_weight: float = 0.5,
    seed: int = 1,
) -> SEA:
    """
    EN:
    Create a SEA instance for the GUI registry.

    PL:
    Tworzy instancje SEA dla rejestru GUI.
    """
    return SEA(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        entropy_weight=entropy_weight,
        seed=seed,
    )


SEA_DEFINITION: Dict[str, Any] = {
    "label": "SEA",
    "factory": make_sea,
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 1},
        "archive_size": {"default": 100, "kind": "int", "minimum": 1},
        "crossover_rate": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "entropy_weight": {"default": 0.5, "kind": "float", "minimum": 1e-6},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Own implementation based on the article. Uses entropy-aware objective-space sparsity when truncating the last front.",
}
