# ------------------------------------------------------------------------------------
# File: dm_dmoea_dual_mutation.py
# Contents: dual-mutation dynamic MOEA class, factory and GUI registry definition.
# What happens here: local polynomial and global Gaussian mutation are blended according to observed population drift.
# Role in the framework: adds a DM-DMOEA variant with explicit article-style dual mutation logic.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on the article.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import math
from typing import Any, Dict

import numpy as np

from .research_common import ResearchMOOAlgorithm, gaussian_mutation, parse_positive_float, parse_probability


class DMDMOEADualMutation(ResearchMOOAlgorithm):
    """
    EN:
    DM-DMOEA variant with dual mutation and change-sensitive global exploration.
    Implementation source: own implementation based on the article.
    PL:
    Wariant DM-DMOEA z podwojna mutacja.
    """

    def __init__(
        self,
        population_size: int = 100,
        archive_size: int = 100,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        local_mutation_rate: float = 0.15,
        global_mutation_rate: float = 0.25,
        global_sigma: float = 0.18,
        change_response: float = 1.5,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=archive_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            seed=seed,
        )
        self.local_mutation_rate = parse_probability(local_mutation_rate, "local_mutation_rate")
        self.global_mutation_rate = parse_probability(global_mutation_rate, "global_mutation_rate")
        self.global_sigma = parse_positive_float(global_sigma, "global_sigma")
        self.change_response = parse_positive_float(change_response, "change_response")

    def change_intensity(self) -> float:
        """
        EN:
        Estimate recent population drift from centroid movement.

        PL:
        Szacuje ostatnia intensywnosc zmian na podstawie ruchu centroidu.
        """
        if len(self.history) < 2:
            return 0.0
        span = np.maximum(self.xu - self.xl, 1e-8)
        delta = self.history[-1]["centroid"] - self.history[-2]["centroid"]
        return float(np.linalg.norm(delta / span) / math.sqrt(self.n_var))

    def mutation(self, offspring: np.ndarray) -> np.ndarray:
        """
        EN:
        Blend local and global mutation, increasing global search after detected drift.

        PL:
        Laczy mutacje lokalna i globalna, zwiekszajac eksploracje po wykryciu zmian.
        """
        local = super().mutation(offspring)
        intensity = self.change_intensity()
        global_share = min(0.85, self.global_mutation_rate + self.change_response * intensity)
        global_mask = self.random_state.random(local.shape[0]) < global_share
        if not np.any(global_mask):
            return local
        mutated = local.copy()
        mutated[global_mask] = gaussian_mutation(
            mutated[global_mask],
            self.xl,
            self.xu,
            self.local_mutation_rate,
            self.global_sigma * (1.0 + intensity),
            self.random_state,
        )
        return mutated


def make_dm_dmoea_dual_mutation(
    population_size: int = 100,
    archive_size: int = 100,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.1,
    local_mutation_rate: float = 0.15,
    global_mutation_rate: float = 0.25,
    global_sigma: float = 0.18,
    change_response: float = 1.5,
    seed: int = 1,
) -> DMDMOEADualMutation:
    """
    EN:
    Create the dual-mutation DM-DMOEA variant for the GUI registry.

    PL:
    Tworzy wariant DM-DMOEA z podwojna mutacja.
    """
    return DMDMOEADualMutation(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        local_mutation_rate=local_mutation_rate,
        global_mutation_rate=global_mutation_rate,
        global_sigma=global_sigma,
        change_response=change_response,
        seed=seed,
    )


DM_DMOEA_DUAL_MUTATION_DEFINITION: Dict[str, Any] = {
    "label": "DM-DMOEA (Dual Mutation-based)",
    "factory": make_dm_dmoea_dual_mutation,
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 1},
        "archive_size": {"default": 100, "kind": "int", "minimum": 1},
        "crossover_rate": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "local_mutation_rate": {"default": 0.15, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "global_mutation_rate": {"default": 0.25, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "global_sigma": {"default": 0.18, "kind": "float", "minimum": 1e-6},
        "change_response": {"default": 1.5, "kind": "float", "minimum": 1e-6},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Own implementation based on the article. Uses NSGA-II-style base selection plus explicit local/global mutation switching.",
}
