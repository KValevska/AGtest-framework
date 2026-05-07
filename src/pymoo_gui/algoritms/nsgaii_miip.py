# ------------------------------------------------------------------------------------
# File: nsgaii_miip.py
# Contents: NSGAII-MIIP class, interpolation-based prediction helpers, factory and GUI registry definition.
# What happens here: a baseline NSGA-II loop is extended with multi-interval interpolation and information prediction.
# Role in the framework: adds an article-inspired NSGA-II variant with explicit predictive modifications.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on the article.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .research_common import ResearchMOOAlgorithm, parse_positive_float, parse_probability


class NSGAIIMIIP(ResearchMOOAlgorithm):
    """
    EN:
    NSGAII-MIIP with explicit NSGA-II base selection and MIIP predictive injections.
    Implementation source: own implementation based on the article.
    PL:
    NSGAII-MIIP z bazowa selekcja NSGA-II oraz dodatkowymi wstrzyknieciami MIIP.
    """

    def __init__(
        self,
        population_size: int = 100,
        archive_size: int = 100,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        guided_fraction: float = 0.25,
        interpolation_weight: float = 0.5,
        prediction_factor: float = 0.7,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=archive_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            seed=seed,
        )
        self.guided_fraction = parse_probability(guided_fraction, "guided_fraction")
        self.interpolation_weight = parse_positive_float(interpolation_weight, "interpolation_weight")
        self.prediction_factor = parse_positive_float(prediction_factor, "prediction_factor")

    def predict_center(self) -> np.ndarray:
        """
        EN:
        Predict the next elite center from multi-interval centroid interpolation.

        PL:
        Przewiduje kolejne centrum elit przez interpolacje centroidow z wielu krokow.
        """
        if len(self.history) < 2:
            return self.state_centroid()
        c0 = self.history[-1]["centroid"]
        c1 = self.history[-2]["centroid"]
        velocity = c0 - c1
        prediction = c0 + self.prediction_factor * velocity
        if len(self.history) >= 3:
            c2 = self.history[-3]["centroid"]
            acceleration = c0 - 2.0 * c1 + c2
            prediction += self.interpolation_weight * acceleration
        return np.clip(prediction, self.xl, self.xu)

    def guided_candidates(self) -> np.ndarray:
        """
        EN:
        Inject interpolated samples between archived elites and the predicted center.

        PL:
        Wstrzykuje probki interpolowane pomiedzy elitami archiwum a przewidzianym centrum.
        """
        count = int(round(self.population_size * self.guided_fraction))
        if count <= 0:
            return np.empty((0, self.n_var), dtype=float)

        center = self.predict_center()
        spread = self.state_spread()
        elites = self.archive_elites(max(2, count))
        if elites.shape[0] == 0:
            base = np.repeat(center[None, :], count, axis=0)
        else:
            base = elites[self.random_state.integers(0, elites.shape[0], size=count)]
        alpha = self.random_state.random((count, 1))
        interpolated = alpha * base + (1.0 - alpha) * center[None, :]
        interpolated += self.random_state.normal(0.0, 0.2, size=(count, self.n_var)) * spread[None, :]
        return np.clip(interpolated, self.xl, self.xu)


def make_nsgaii_miip(
    population_size: int = 100,
    archive_size: int = 100,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.1,
    guided_fraction: float = 0.25,
    interpolation_weight: float = 0.5,
    prediction_factor: float = 0.7,
    seed: int = 1,
) -> NSGAIIMIIP:
    """
    EN:
    Create an NSGAII-MIIP instance for the GUI registry.

    PL:
    Tworzy instancje NSGAII-MIIP dla rejestru GUI.
    """
    return NSGAIIMIIP(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        guided_fraction=guided_fraction,
        interpolation_weight=interpolation_weight,
        prediction_factor=prediction_factor,
        seed=seed,
    )


NSGAII_MIIP_DEFINITION: Dict[str, Any] = {
    "label": "NSGAII-MIIP",
    "factory": make_nsgaii_miip,
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 1},
        "archive_size": {"default": 100, "kind": "int", "minimum": 1},
        "crossover_rate": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "guided_fraction": {"default": 0.25, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "interpolation_weight": {"default": 0.5, "kind": "float", "minimum": 1e-6},
        "prediction_factor": {"default": 0.7, "kind": "float", "minimum": 1e-6},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Own implementation based on the article. Base part: NSGA-II-style rank/crowding. MIIP part: predictive interpolation injections.",
}
