# ------------------------------------------------------------------------------------
# File: learning_edmo.py
# Contents: cross-problem memory EDMO class, factory and GUI registry definition.
# What happens here: elite patterns are cached between compatible runs and reused as warm-start and guided samples.
# Role in the framework: adds an article-inspired learning-across-problems evolutionary dynamic MOEA.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on the article.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .research_common import ResearchMOOAlgorithm, parse_positive_int, parse_probability


class LearningAcrossProblemsEDMO(ResearchMOOAlgorithm):
    """
    EN:
    EDMO variant with a simple in-process transfer memory across compatible problems.
    Implementation source: own implementation based on the article.
    PL:
    Wariant EDMO uczacy sie pomiedzy problemami o zgodnej sygnaturze.
    """

    TRANSFER_MEMORY: dict[str, list[np.ndarray]] = {}

    def __init__(
        self,
        population_size: int = 100,
        archive_size: int = 100,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        transfer_fraction: float = 0.2,
        memory_size: int = 8,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=archive_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            seed=seed,
        )
        self.transfer_fraction = parse_probability(transfer_fraction, "transfer_fraction")
        self.memory_size = parse_positive_int(memory_size, "memory_size")
        self.problem_signature = ""

    def make_signature(self) -> str:
        """
        EN:
        Build a compact signature grouping compatible problem instances.

        PL:
        Buduje skrot sygnatury grupujacej zgodne problemy.
        """
        span = np.round(self.xu - self.xl, 6)
        return f"{self.n_var}|{self.n_obj}|{tuple(span.tolist())}"

    def warm_start_candidates(self) -> np.ndarray | None:
        """
        EN:
        Reuse normalized elite points from previous compatible runs.

        PL:
        Wykorzystuje znormalizowane elity z poprzednich zgodnych uruchomien.
        """
        self.problem_signature = self.make_signature()
        memory = self.TRANSFER_MEMORY.get(self.problem_signature, [])
        if not memory:
            return None
        count = max(1, int(round(self.population_size * self.transfer_fraction)))
        selected = memory[: min(count, len(memory))]
        span = self.xu - self.xl
        return np.asarray([self.xl + np.clip(item, 0.0, 1.0) * span for item in selected], dtype=float)

    def guided_candidates(self) -> np.ndarray:
        """
        EN:
        Blend current archive elites with transferred memory samples.

        PL:
        Laczy aktualne elity z probkami z pamieci miedzypoziomowej.
        """
        memory = self.TRANSFER_MEMORY.get(self.problem_signature, [])
        if not memory:
            return np.empty((0, self.n_var), dtype=float)
        count = max(1, int(round(self.population_size * self.transfer_fraction)))
        span = self.xu - self.xl
        ids = self.random_state.integers(0, len(memory), size=count)
        memory_points = np.asarray([self.xl + np.clip(memory[i], 0.0, 1.0) * span for i in ids], dtype=float)
        archive = self.archive_elites(count)
        if archive.shape[0]:
            mix = 0.5 * memory_points + 0.5 * archive[self.random_state.integers(0, archive.shape[0], size=count)]
        else:
            mix = memory_points
        return np.clip(mix, self.xl, self.xu)

    def after_generation(self, previous, current) -> None:
        """
        EN:
        Update the transfer memory with normalized archived elite points.

        PL:
        Aktualizuje pamiec transferu znormalizowanymi elitami z archiwum.
        """
        if self.archive is None:
            return
        span = np.maximum(self.xu - self.xl, 1e-8)
        normalized = (self.archive.X[: self.memory_size] - self.xl[None, :]) / span[None, :]
        bucket = self.TRANSFER_MEMORY.setdefault(self.problem_signature, [])
        bucket[:] = [item.copy() for item in normalized] + bucket
        del bucket[self.memory_size :]


def make_learning_edmo(
    population_size: int = 100,
    archive_size: int = 100,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.1,
    transfer_fraction: float = 0.2,
    memory_size: int = 8,
    seed: int = 1,
) -> LearningAcrossProblemsEDMO:
    """
    EN:
    Create the learning-across-problems EDMO variant.

    PL:
    Tworzy wariant EDMO uczacy sie pomiedzy problemami.
    """
    return LearningAcrossProblemsEDMO(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        transfer_fraction=transfer_fraction,
        memory_size=memory_size,
        seed=seed,
    )


LEARNING_EDMO_DEFINITION: Dict[str, Any] = {
    "label": "Learning-across-problems EDMO",
    "factory": make_learning_edmo,
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 1},
        "archive_size": {"default": 100, "kind": "int", "minimum": 1},
        "crossover_rate": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "transfer_fraction": {"default": 0.2, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "memory_size": {"default": 8, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Own implementation based on the article. Keeps an in-process transfer memory across compatible problem runs.",
}
