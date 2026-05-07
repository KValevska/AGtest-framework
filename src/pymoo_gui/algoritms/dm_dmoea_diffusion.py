# ------------------------------------------------------------------------------------
# File: dm_dmoea_diffusion.py
# Contents: diffusion-style predictive DM-DMOEA class, factory and GUI registry definition.
# What happens here: elite-history prediction and denoising-style sampling guide extra offspring generation.
# Role in the framework: adds a dynamic article-inspired DM-DMOEA variant beyond baseline NSGA-II behavior.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on the article.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .research_common import ResearchMOOAlgorithm, parse_positive_float, parse_probability


class DMDMOEADiffusion(ResearchMOOAlgorithm):
    """
    EN:
    DM-DMOEA variant using diffusion-style denoising around a predicted elite centroid.
    Implementation source: own implementation based on the article.
    PL:
    Wariant DM-DMOEA z predykcja polozenia elit i probkowaniem typu diffusion.
    """

    def __init__(
        self,
        population_size: int = 100,
        archive_size: int = 100,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        diffusion_scale: float = 0.12,
        guided_fraction: float = 0.25,
        prediction_weight: float = 0.65,
        history_window: int = 3,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=archive_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            seed=seed,
        )
        self.diffusion_scale = parse_positive_float(diffusion_scale, "diffusion_scale")
        self.guided_fraction = parse_probability(guided_fraction, "guided_fraction")
        self.prediction_weight = parse_probability(prediction_weight, "prediction_weight")
        self.history_window = max(1, int(history_window))

    def predict_center(self) -> np.ndarray:
        """
        EN:
        Predict the next elite centroid from recent centroid displacements.

        PL:
        Przewiduje nastepny srodek elit na podstawie ostatnich przesuniec.
        """
        if not self.history:
            return self.state_centroid()
        centroids = np.asarray([item["centroid"] for item in self.history[-self.history_window :]], dtype=float)
        predicted = centroids[-1].copy()
        if centroids.shape[0] >= 2:
            predicted += self.prediction_weight * (centroids[-1] - centroids[-2])
        if centroids.shape[0] >= 3:
            predicted += 0.25 * (centroids[-2] - centroids[-3])
        return np.clip(predicted, self.xl, self.xu)

    def guided_candidates(self) -> np.ndarray:
        """
        EN:
        Generate denoised samples around a predicted elite center.

        PL:
        Tworzy dodatkowe probki odszumiane wzgledem przewidzianego centrum elit.
        """
        count = int(round(self.population_size * self.guided_fraction))
        if count <= 0:
            return np.empty((0, self.n_var), dtype=float)

        center = self.predict_center()
        spread = self.state_spread()
        elite_pool = self.archive_elites(max(2, count))
        if elite_pool.shape[0] == 0:
            base = np.repeat(center[None, :], count, axis=0)
        else:
            ids = self.random_state.integers(0, elite_pool.shape[0], size=count)
            base = elite_pool[ids]

        noisy = base + self.random_state.normal(0.0, self.diffusion_scale, size=(count, self.n_var)) * spread[None, :]
        denoised = noisy - self.prediction_weight * (noisy - center[None, :])
        return np.clip(denoised, self.xl, self.xu)


def make_dm_dmoea_diffusion(
    population_size: int = 100,
    archive_size: int = 100,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.1,
    diffusion_scale: float = 0.12,
    guided_fraction: float = 0.25,
    prediction_weight: float = 0.65,
    history_window: int = 3,
    seed: int = 1,
) -> DMDMOEADiffusion:
    """
    EN:
    Create the diffusion/prediction DM-DMOEA variant for the GUI registry.

    PL:
    Tworzy wariant DM-DMOEA oparty na diffusion i predykcji.
    """
    return DMDMOEADiffusion(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        diffusion_scale=diffusion_scale,
        guided_fraction=guided_fraction,
        prediction_weight=prediction_weight,
        history_window=history_window,
        seed=seed,
    )


DM_DMOEA_DIFFUSION_DEFINITION: Dict[str, Any] = {
    "label": "DM-DMOEA (Diffusion / Prediction Strategy)",
    "factory": make_dm_dmoea_diffusion,
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 1},
        "archive_size": {"default": 100, "kind": "int", "minimum": 1},
        "crossover_rate": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "diffusion_scale": {"default": 0.12, "kind": "float", "minimum": 1e-6},
        "guided_fraction": {"default": 0.25, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "prediction_weight": {"default": 0.65, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "history_window": {"default": 3, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Own implementation based on the article. Uses NSGA-II-style base survival plus diffusion-like predictive injections.",
}
