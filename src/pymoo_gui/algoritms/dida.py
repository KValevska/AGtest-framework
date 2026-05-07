# ------------------------------------------------------------------------------------
# File: dida.py
# Contents: DIDA class, diversity-improvement survival, factory and GUI registry definition.
# What happens here: mutation intensity and last-front truncation adapt to objective-space diversity deficits.
# Role in the framework: adds a diversity-improvement article-inspired dynamic MOEA variant.
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


def angle_diversity(F: np.ndarray) -> np.ndarray:
    """
    EN:
    Approximate diversity by the minimum angular separation in normalized objective space.

    PL:
    Przybliza roznorodnosc przez minimalny kat w znormalizowanej przestrzeni celow.
    """
    if F.shape[0] == 0:
        return np.zeros(0, dtype=float)
    Fn, _, _ = normalized_objectives(F)
    norms = np.linalg.norm(Fn, axis=1, keepdims=True)
    unit = Fn / np.where(norms > 0.0, norms, 1.0)
    cosine = np.clip(unit @ unit.T, -1.0, 1.0)
    angles = np.arccos(cosine)
    angles += np.eye(F.shape[0]) * np.inf
    return np.min(angles, axis=1)


class DIDA(ResearchMOOAlgorithm):
    """
    EN:
    DIDA with diversity-aware mutation and angle-based last-front truncation.
    Implementation source: own implementation based on the article.
    PL:
    DIDA z mutacja zaleznia od roznorodnosci i obcinaniem frontu po katach.
    """

    def __init__(
        self,
        population_size: int = 100,
        archive_size: int = 100,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        diversity_target: float = 0.15,
        adaptation_gain: float = 2.0,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=archive_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            seed=seed,
        )
        self.diversity_target = parse_positive_float(diversity_target, "diversity_target")
        self.adaptation_gain = parse_positive_float(adaptation_gain, "adaptation_gain")

    def mutation(self, offspring: np.ndarray) -> np.ndarray:
        """
        EN:
        Increase polynomial-mutation strength when diversity drops below target.

        PL:
        Zwieksza sile mutacji wielomianowej, gdy roznorodnosc spada ponizej celu.
        """
        current_diversity = self.diversity_score()
        deficit = max(0.0, self.diversity_target - current_diversity)
        strength = 1.0 + self.adaptation_gain * deficit
        from .research_common import polynomial_mutation

        return polynomial_mutation(
            offspring,
            self.xl,
            self.xu,
            self.mutation_eta,
            self.mutation_rate,
            self.random_state,
            strength=strength,
        )

    def environmental_selection(self, X: np.ndarray, F: np.ndarray, CV: np.ndarray, n_survive: int) -> PopulationState:
        """
        EN:
        Select survivors by fronts and angle diversity on the truncation front.

        PL:
        Wybiera osobniki przez fronty oraz katowa roznorodnosc na froncie obcinanym.
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
                score = crowding[actual] + angle_diversity(F[actual])
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


def make_dida(
    population_size: int = 100,
    archive_size: int = 100,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.1,
    diversity_target: float = 0.15,
    adaptation_gain: float = 2.0,
    seed: int = 1,
) -> DIDA:
    """
    EN:
    Create a DIDA instance for the GUI registry.

    PL:
    Tworzy instancje DIDA dla rejestru GUI.
    """
    return DIDA(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        diversity_target=diversity_target,
        adaptation_gain=adaptation_gain,
        seed=seed,
    )


DIDA_DEFINITION: Dict[str, Any] = {
    "label": "DIDA",
    "factory": make_dida,
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 1},
        "archive_size": {"default": 100, "kind": "int", "minimum": 1},
        "crossover_rate": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "diversity_target": {"default": 0.15, "kind": "float", "minimum": 1e-6},
        "adaptation_gain": {"default": 2.0, "kind": "float", "minimum": 1e-6},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Own implementation based on the article. Separates baseline variation from DIDA diversity-improvement adaptations.",
}
