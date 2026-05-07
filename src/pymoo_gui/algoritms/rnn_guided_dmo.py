# ------------------------------------------------------------------------------------
# File: rnn_guided_dmo.py
# Contents: lightweight recurrent-guided DMO class, factory and GUI registry definition.
# What happens here: a small deterministic recurrent state predicts motion of elite centroids and guides new samples.
# Role in the framework: adds an RNN-guided dynamic MOEA variant without external deep-learning dependencies.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on the article.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .research_common import ResearchMOOAlgorithm, parse_positive_float, parse_positive_int, parse_probability


class RNNGuidedDMO(ResearchMOOAlgorithm):
    """
    EN:
    Lightweight RNN-guided dynamic MOEA.
    Implementation source: own implementation based on the article.
    PL:
    Lekki wariant dynamicznego MOEA sterowany rekurencyjna predykcja.
    """

    def __init__(
        self,
        population_size: int = 100,
        archive_size: int = 100,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        hidden_size: int = 16,
        guided_fraction: float = 0.2,
        prediction_scale: float = 0.35,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=archive_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            seed=seed,
        )
        self.hidden_size = parse_positive_int(hidden_size, "hidden_size")
        self.guided_fraction = parse_probability(guided_fraction, "guided_fraction")
        self.prediction_scale = parse_positive_float(prediction_scale, "prediction_scale")
        self.hidden = np.zeros(self.hidden_size, dtype=float)
        self.Wx = np.empty((0, 0), dtype=float)
        self.Wh = np.empty((0, 0), dtype=float)
        self.Wo = np.empty((0, 0), dtype=float)

    def after_initialize(self) -> None:
        """
        EN:
        Create deterministic recurrent weights after `n_var` becomes known.

        PL:
        Tworzy deterministyczne wagi rekurencyjne po poznaniu liczby zmiennych.
        """
        scale_x = 1.0 / max(self.n_var, 1)
        scale_h = 1.0 / max(self.hidden_size, 1)
        self.Wx = self.random_state.normal(0.0, scale_x, size=(self.hidden_size, self.n_var))
        self.Wh = self.random_state.normal(0.0, scale_h, size=(self.hidden_size, self.hidden_size))
        self.Wo = self.random_state.normal(0.0, scale_h, size=(self.n_var, self.hidden_size))
        self.hidden = np.zeros(self.hidden_size, dtype=float)
        self._update_hidden(self.state_centroid())

    def _update_hidden(self, centroid: np.ndarray) -> None:
        """
        EN:
        Update the recurrent hidden state from the latest elite centroid.

        PL:
        Aktualizuje stan ukryty na podstawie najnowszego centroidu elit.
        """
        self.hidden = np.tanh(self.Wx @ centroid + self.Wh @ self.hidden)

    def predict_center(self) -> np.ndarray:
        """
        EN:
        Predict the next center from the recurrent hidden state.

        PL:
        Przewiduje kolejne centrum z wykorzystaniem stanu ukrytego.
        """
        base = self.state_centroid()
        span = self.xu - self.xl
        delta = np.tanh(self.Wo @ self.hidden) * span * self.prediction_scale
        return np.clip(base + delta, self.xl, self.xu)

    def guided_candidates(self) -> np.ndarray:
        """
        EN:
        Generate RNN-guided candidate solutions.

        PL:
        Tworzy kandydatow prowadzonych przez predykcje rekurencyjna.
        """
        count = int(round(self.population_size * self.guided_fraction))
        if count <= 0:
            return np.empty((0, self.n_var), dtype=float)
        center = self.predict_center()
        spread = self.state_spread()
        samples = center[None, :] + self.random_state.normal(0.0, 0.25, size=(count, self.n_var)) * spread[None, :]
        return np.clip(samples, self.xl, self.xu)

    def after_generation(self, previous, current) -> None:
        """
        EN:
        Refresh the recurrent state after each generation.

        PL:
        Odswieza stan rekurencyjny po kazdej generacji.
        """
        self._update_hidden(self.state_centroid(current))


def make_rnn_guided_dmo(
    population_size: int = 100,
    archive_size: int = 100,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.1,
    hidden_size: int = 16,
    guided_fraction: float = 0.2,
    prediction_scale: float = 0.35,
    seed: int = 1,
) -> RNNGuidedDMO:
    """
    EN:
    Create the RNN-guided dynamic MOEA variant for the GUI registry.

    PL:
    Tworzy wariant dynamicznego MOEA sterowany przez lekki model RNN.
    """
    return RNNGuidedDMO(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        hidden_size=hidden_size,
        guided_fraction=guided_fraction,
        prediction_scale=prediction_scale,
        seed=seed,
    )


RNN_GUIDED_DMO_DEFINITION: Dict[str, Any] = {
    "label": "RNN-guided DMO",
    "factory": make_rnn_guided_dmo,
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 1},
        "archive_size": {"default": 100, "kind": "int", "minimum": 1},
        "crossover_rate": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "hidden_size": {"default": 16, "kind": "int", "minimum": 1},
        "guided_fraction": {"default": 0.2, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "prediction_scale": {"default": 0.35, "kind": "float", "minimum": 1e-6},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Own implementation based on the article. Uses a deterministic lightweight recurrent predictor, not an external ML dependency.",
}
