# ------------------------------------------------------------------------------------
# File: vare.py
# Contents: vector-autoregressive evolution class, factory and GUI registry definition.
# What happens here: recent centroid trajectories are fitted with a small autoregressive model that guides offspring.
# Role in the framework: adds a trajectory-prediction MOEA variant for dynamic and drifting Pareto fronts.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on the article.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .research_common import ResearchMOOAlgorithm, parse_positive_float, parse_positive_int, parse_probability


class VARE(ResearchMOOAlgorithm):
    """
    EN:
    Vector Autoregressive Evolution algorithm.
    Implementation source: own implementation based on the article.
    PL:
    Algorytm Vector Autoregressive Evolution.
    """

    def __init__(
        self,
        population_size: int = 100,
        archive_size: int = 100,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        ar_order: int = 2,
        guided_fraction: float = 0.25,
        prediction_strength: float = 0.6,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=archive_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            seed=seed,
        )
        self.ar_order = parse_positive_int(ar_order, "ar_order")
        self.guided_fraction = parse_probability(guided_fraction, "guided_fraction")
        self.prediction_strength = parse_positive_float(prediction_strength, "prediction_strength")

    def predict_center(self) -> np.ndarray:
        """
        EN:
        Predict the next centroid with a vector autoregressive least-squares fit.

        PL:
        Przewiduje nastepny centroid przez dopasowanie modelu autoregresyjnego.
        """
        centroids = np.asarray([item["centroid"] for item in self.history], dtype=float)
        if centroids.shape[0] <= 1:
            return self.state_centroid()

        order = min(self.ar_order, centroids.shape[0] - 1)
        if order <= 0:
            return centroids[-1]

        Y = centroids[order:]
        features = []
        for lag in range(1, order + 1):
            features.append(centroids[order - lag : centroids.shape[0] - lag])
        Phi = np.hstack(features + [np.ones((Y.shape[0], 1), dtype=float)])
        coef, _, _, _ = np.linalg.lstsq(Phi, Y, rcond=None)
        latest = np.hstack([centroids[-lag] for lag in range(1, order + 1)] + [1.0])
        predicted = latest @ coef
        blended = centroids[-1] + self.prediction_strength * (predicted - centroids[-1])
        return np.clip(blended, self.xl, self.xu)

    def guided_candidates(self) -> np.ndarray:
        """
        EN:
        Sample candidates around the VAR-predicted centroid.

        PL:
        Probkuje kandydatow wokol centroidu przewidzianego przez model VAR.
        """
        count = int(round(self.population_size * self.guided_fraction))
        if count <= 0:
            return np.empty((0, self.n_var), dtype=float)

        center = self.predict_center()
        spread = self.state_spread()
        velocity = center - self.state_centroid()
        candidates = center[None, :] + self.random_state.normal(0.0, 0.35, size=(count, self.n_var)) * spread[None, :]
        candidates += 0.5 * velocity[None, :]
        return np.clip(candidates, self.xl, self.xu)


def make_vare(
    population_size: int = 100,
    archive_size: int = 100,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.1,
    ar_order: int = 2,
    guided_fraction: float = 0.25,
    prediction_strength: float = 0.6,
    seed: int = 1,
) -> VARE:
    """
    EN:
    Create a VARE instance for the GUI registry.

    PL:
    Tworzy instancje VARE dla rejestru GUI.
    """
    return VARE(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        ar_order=ar_order,
        guided_fraction=guided_fraction,
        prediction_strength=prediction_strength,
        seed=seed,
    )


VARE_DEFINITION: Dict[str, Any] = {
    "label": "VARE",
    "factory": make_vare,
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 1},
        "archive_size": {"default": 100, "kind": "int", "minimum": 1},
        "crossover_rate": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "ar_order": {"default": 2, "kind": "int", "minimum": 1},
        "guided_fraction": {"default": 0.25, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "prediction_strength": {"default": 0.6, "kind": "float", "minimum": 1e-6},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Own implementation based on the article. Uses a vector-autoregressive prediction of elite centroids.",
}
