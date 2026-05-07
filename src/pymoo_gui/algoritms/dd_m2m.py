# ------------------------------------------------------------------------------------
# File: dd_m2m.py
# Contents: DD-M2M class, decomposition-driven selection, factory and GUI registry definition.
# What happens here: reference-direction neighborhoods drive mating and many-to-many survivor matching.
# Role in the framework: adds a dominance-and-decomposition many-to-many matching optimizer.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on the article.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .research_common import (
    PopulationState,
    ResearchMOOAlgorithm,
    associate_to_reference_directions,
    assign_rank_and_crowding,
    feasible_mask,
    parse_positive_int,
    stable_survivor_order,
    tchebycheff_scores,
)


class DDM2M(ResearchMOOAlgorithm):
    """
    EN:
    DD-M2M with reference-direction neighborhoods and many-to-many survivor matching.
    Implementation source: own implementation based on the article.
    PL:
    DD-M2M z sasiedztwem kierunkow odniesienia i matchingiem many-to-many.
    """

    def __init__(
        self,
        population_size: int = 120,
        archive_size: int = 120,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        n_neighbors: int = 15,
        n_partitions: int = 12,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=archive_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            n_neighbors=n_neighbors,
            n_partitions=n_partitions,
            seed=seed,
        )
        self.direction_neighbors = np.empty((0, 0), dtype=int)
        self.matching_quota = 1
        self.n_neighbors = parse_positive_int(n_neighbors, "n_neighbors")

    def after_initialize(self) -> None:
        """
        EN:
        Precompute neighborhoods between reference directions.

        PL:
        Przygotowuje sasiedztwa pomiedzy kierunkami odniesienia.
        """
        distances = np.linalg.norm(
            self.reference_directions[:, None, :] - self.reference_directions[None, :, :],
            axis=2,
        )
        self.direction_neighbors = np.argsort(distances, axis=1)[:, : self.n_neighbors]
        self.matching_quota = max(1, int(np.ceil(self.population_size / self.reference_directions.shape[0])))

    def select(self) -> np.ndarray:
        """
        EN:
        Select parents inside direction neighborhoods instead of global tournaments.

        PL:
        Wybiera rodzicow w lokalnych sasiedztwach kierunkow odniesienia.
        """
        assert self.state is not None
        association, _ = associate_to_reference_directions(self.state.F, self.reference_directions)
        parents = np.zeros((self.population_size, 2), dtype=int)
        for i in range(self.population_size):
            anchor = int(self.random_state.integers(0, self.state.X.shape[0]))
            direction_id = int(association[anchor])
            neighborhood = self.direction_neighbors[direction_id]
            pool = np.flatnonzero(np.isin(association, neighborhood))
            if pool.size < 2:
                pool = np.arange(self.state.X.shape[0])
            parents[i] = self.random_state.choice(pool, size=2, replace=pool.size < 2)
        return parents

    def environmental_selection(self, X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> PopulationState:
        """
        EN:
        Match survivors to reference directions using decomposition scores.

        PL:
        Dopasowuje osobniki do kierunkow odniesienia przy pomocy wyniku dekompozycyjnego.
        """
        rank, crowding = assign_rank_and_crowding(F, CV)
        feasible_idx = np.flatnonzero(feasible_mask(CV))
        selected: list[int] = []

        if feasible_idx.size:
            scores = tchebycheff_scores(F[feasible_idx], self.reference_directions)
            for direction_id in range(self.reference_directions.shape[0]):
                order = np.argsort(scores[:, direction_id], kind="mergesort")
                assigned = 0
                for local_idx in order:
                    candidate = int(feasible_idx[local_idx])
                    if candidate in selected:
                        continue
                    selected.append(candidate)
                    assigned += 1
                    if assigned >= self.matching_quota or len(selected) >= int(n_survive):
                        break
                if len(selected) >= int(n_survive):
                    break

            if len(selected) < int(n_survive):
                best_order = feasible_idx[np.argsort(np.min(scores, axis=1), kind="mergesort")]
                for candidate in best_order:
                    candidate = int(candidate)
                    if candidate not in selected:
                        selected.append(candidate)
                    if len(selected) >= int(n_survive):
                        break

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


def make_dd_m2m(
    population_size: int = 120,
    archive_size: int = 120,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.1,
    n_neighbors: int = 15,
    n_partitions: int = 12,
    seed: int = 1,
) -> DDM2M:
    """
    EN:
    Create a DD-M2M instance for the GUI registry.

    PL:
    Tworzy instancje DD-M2M dla rejestru GUI.
    """
    return DDM2M(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        n_neighbors=n_neighbors,
        n_partitions=n_partitions,
        seed=seed,
    )


DD_M2M_DEFINITION: Dict[str, Any] = {
    "label": "DD-M2M",
    "factory": make_dd_m2m,
    "form_fields": {
        "population_size": {"default": 120, "kind": "int", "minimum": 1},
        "archive_size": {"default": 120, "kind": "int", "minimum": 1},
        "crossover_rate": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "n_neighbors": {"default": 15, "kind": "int", "minimum": 1},
        "n_partitions": {"default": 12, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Own implementation based on the article. Separates baseline variation from DD-M2M direction-neighborhood matching.",
}
