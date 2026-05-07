# ------------------------------------------------------------------------------------
# File: ql_imoga.py
# Contents: Q-learning-guided IMOGA class, operator-selection logic, factory and GUI registry definition.
# What happens here: a compact Q-table chooses among multiple search operators based on progress and diversity states.
# Role in the framework: adds a reinforcement-learning-guided multiobjective genetic algorithm variant.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on the article.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .research_common import ResearchMOOAlgorithm, gaussian_mutation, parse_positive_float, parse_probability


class QLIMOGA(ResearchMOOAlgorithm):
    """
    EN:
    QL-IMOGA with Q-learning-based operator selection.
    Implementation source: own implementation based on the article.
    PL:
    QL-IMOGA z wyborem operatorow sterowanym uczeniem Q-learning.
    """

    def __init__(
        self,
        population_size: int = 100,
        archive_size: int = 100,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        exploration_rate: float = 0.15,
        learning_rate: float = 0.25,
        discount_factor: float = 0.9,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=archive_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            seed=seed,
        )
        self.exploration_rate = parse_probability(exploration_rate, "exploration_rate")
        self.learning_rate = parse_positive_float(learning_rate, "learning_rate")
        self.discount_factor = parse_probability(discount_factor, "discount_factor")
        self.q_table = np.zeros((9, 4), dtype=float)
        self.pending_state = 0
        self.pending_action = 0

    def state_id(self) -> int:
        """
        EN:
        Encode diversity and recent progress into a compact discrete state.

        PL:
        Koduje roznorodnosc i ostatni postep do dyskretnego stanu.
        """
        diversity = self.diversity_score()
        if diversity < 0.08:
            d_bin = 0
        elif diversity < 0.18:
            d_bin = 1
        else:
            d_bin = 2

        progress = 0.0
        if len(self.history) >= 2:
            progress = float(np.linalg.norm(self.history[-1]["ideal"] - self.history[-2]["ideal"]))
        if progress < 1e-4:
            p_bin = 0
        elif progress < 5e-3:
            p_bin = 1
        else:
            p_bin = 2
        return d_bin * 3 + p_bin

    def choose_action(self) -> int:
        """
        EN:
        Choose the next search operator with epsilon-greedy Q-learning.

        PL:
        Wybiera kolejny operator przeszukiwania metoda epsilon-greedy.
        """
        state = self.state_id()
        self.pending_state = state
        if self.random_state.random() < self.exploration_rate:
            self.pending_action = int(self.random_state.integers(0, self.q_table.shape[1]))
        else:
            self.pending_action = int(np.argmax(self.q_table[state]))
        return self.pending_action

    def create_offspring(self) -> np.ndarray:
        """
        EN:
        Generate offspring using the operator selected by the Q-table.

        PL:
        Tworzy potomkow operatorem wybranym przez Q-learning.
        """
        action = self.choose_action()
        parents = self.crossover(self.select())
        spread = self.state_spread()

        if action == 0:
            return super().mutation(parents)
        if action == 1:
            return gaussian_mutation(parents, self.xl, self.xu, 0.4, 0.18, self.random_state)
        if action == 2:
            elites = self.archive_elites(max(2, parents.shape[0]))
            if elites.shape[0]:
                partner = elites[self.random_state.integers(0, elites.shape[0], size=parents.shape[0])]
                blended = 0.5 * parents + 0.5 * partner
            else:
                blended = parents
            return super().mutation(blended)

        center = self.state_centroid()
        guided = center[None, :] + self.random_state.normal(0.0, 0.3, size=parents.shape) * spread[None, :]
        mixed = 0.5 * parents + 0.5 * np.clip(guided, self.xl, self.xu)
        return np.clip(mixed, self.xl, self.xu)

    def after_generation(self, previous, current) -> None:
        """
        EN:
        Update the Q-table from the observed generation reward.

        PL:
        Aktualizuje tablice Q na podstawie nagrody za ostatnia generacje.
        """
        reward = self.progress_score(previous, current)
        next_state = self.state_id()
        old = self.q_table[self.pending_state, self.pending_action]
        target = reward + self.discount_factor * float(np.max(self.q_table[next_state]))
        self.q_table[self.pending_state, self.pending_action] = old + self.learning_rate * (target - old)


def make_ql_imoga(
    population_size: int = 100,
    archive_size: int = 100,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.1,
    exploration_rate: float = 0.15,
    learning_rate: float = 0.25,
    discount_factor: float = 0.9,
    seed: int = 1,
) -> QLIMOGA:
    """
    EN:
    Create a QL-IMOGA instance for the GUI registry.

    PL:
    Tworzy instancje QL-IMOGA dla rejestru GUI.
    """
    return QLIMOGA(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        exploration_rate=exploration_rate,
        learning_rate=learning_rate,
        discount_factor=discount_factor,
        seed=seed,
    )


QL_IMOGA_DEFINITION: Dict[str, Any] = {
    "label": "QL-IMOGA",
    "factory": make_ql_imoga,
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 1},
        "archive_size": {"default": 100, "kind": "int", "minimum": 1},
        "crossover_rate": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "exploration_rate": {"default": 0.15, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "learning_rate": {"default": 0.25, "kind": "float", "minimum": 1e-6},
        "discount_factor": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Own implementation based on the article. Uses Q-learning to switch between four search operators.",
}
