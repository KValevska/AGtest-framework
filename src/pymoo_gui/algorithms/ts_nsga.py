# ------------------------------------------------------------------------------------
# Module: ts_nsga.py
# Summary: TS-NSGA class, factory and GUI registry definition.
# Implementation: baseline NSGA-style evolution is extended with a second local-search stage around elite regions.
# Responsibility: adds the TS-NSGA article-inspired variant for comparative experiments.
# Author: Kristina Valevska, MSc Eng.
# Implementation source: own implementation based on the article.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .research_common import (
    ResearchMOOAlgorithm,
    parse_positive_float,
    parse_probability,
)


class TSNSGA(ResearchMOOAlgorithm):
    # TS-NSGA with a second local-search stage around archived elites.
    # Implementation source: own implementation based on the article.
    # TS-NSGA z drugim etapem lokalnego przeszukiwania wokol elit archiwum.

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
        # Perform the second stage by locally perturbing elite archived solutions.
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


def make_ts_nsga(
    population_size: int = 100,
    archive_size: int = 100,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.1,
    stage_fraction: float = 0.3,
    local_search_scale: float = 0.15,
    seed: int = 1,
) -> TSNSGA:
    # Create a TS-NSGA instance for the GUI registry.
    return TSNSGA(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        stage_fraction=stage_fraction,
        local_search_scale=local_search_scale,
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
