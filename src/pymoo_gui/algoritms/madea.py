# ------------------------------------------------------------------------------------
# File: madea.py
# Contents: adaptive differential-evolution multiobjective algorithm, factory and GUI registry definition.
# What happens here: current-to-pbest DE offspring and simple success-history parameter memories drive variation.
# Role in the framework: adds an adaptive DE-based article-inspired many-objective optimizer.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on the article.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .research_common import (
    PopulationState,
    ResearchMOOAlgorithm,
    assign_rank_and_crowding,
    parse_positive_int,
    parse_probability,
    project_to_bounds,
    stable_survivor_order,
)


class MADEA(ResearchMOOAlgorithm):
    """
    EN:
    MADEA with adaptive DE parameters and success-history memories.
    Implementation source: own implementation based on the article.
    PL:
    MADEA z adaptacyjnymi parametrami DE i pamiecia skutecznych ustawien.
    """

    def __init__(
        self,
        population_size: int = 100,
        archive_size: int = 100,
        mutation_rate: float = 0.1,
        memory_size: int = 6,
        p_best_fraction: float = 0.2,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=archive_size,
            crossover_rate=1.0,
            mutation_rate=mutation_rate,
            seed=seed,
        )
        self.memory_size = parse_positive_int(memory_size, "memory_size")
        self.p_best_fraction = parse_probability(p_best_fraction, "p_best_fraction")
        self.memory_f = np.full(self.memory_size, 0.5, dtype=float)
        self.memory_cr = np.full(self.memory_size, 0.5, dtype=float)

    def _sample_parameters(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        EN:
        Draw adaptive F and CR values from success-history memories.

        PL:
        Losuje adaptacyjne wartosci F i CR z pamieci sukcesow.
        """
        slots = self.random_state.integers(0, self.memory_size, size=self.population_size)
        F_weight = np.clip(self.random_state.normal(self.memory_f[slots], 0.1), 0.1, 1.0)
        CR = np.clip(self.random_state.normal(self.memory_cr[slots], 0.1), 0.0, 1.0)
        return slots, F_weight, CR

    def _de_offspring(self, F_weight: np.ndarray, CR: np.ndarray) -> np.ndarray:
        """
        EN:
        Generate offspring with a current-to-pbest DE strategy.

        PL:
        Tworzy potomkow strategia current-to-pbest DE.
        """
        assert self.state is not None
        X = self.state.X
        n_pop = X.shape[0]
        pbest_count = max(2, int(np.ceil(self.population_size * self.p_best_fraction)))
        pbest_pool = X[:pbest_count]
        pool = np.vstack([X, self.archive.X if self.archive is not None else X])
        children = np.zeros_like(X)

        for i in range(n_pop):
            pbest = pbest_pool[int(self.random_state.integers(0, pbest_pool.shape[0]))]
            choices = np.delete(np.arange(n_pop), i)
            r1 = int(self.random_state.choice(choices))
            r2 = pool[int(self.random_state.integers(0, pool.shape[0]))]
            mutant = X[i] + F_weight[i] * (pbest - X[i]) + F_weight[i] * (X[r1] - r2)
            trial = X[i].copy()
            j_rand = int(self.random_state.integers(0, self.n_var))
            for j in range(self.n_var):
                if self.random_state.random() <= CR[i] or j == j_rand:
                    trial[j] = mutant[j]
            children[i] = trial

        return project_to_bounds(children, self.xl, self.xu)

    def step(self) -> None:
        """
        EN:
        Execute one MADEA generation and update DE parameter memories from successful trials.

        PL:
        Wykonuje jedna generacje MADEA i aktualizuje pamieci F/CR na podstawie sukcesow.
        """
        if self.state is None:
            raise RuntimeError("Algorithm must be initialized before step().")

        previous = self.state
        slots, F_weight, CR = self._sample_parameters()
        offspring = self._de_offspring(F_weight, CR)
        off_F, off_CV = self.evaluate(offspring)

        candidate_X = np.vstack([previous.X, offspring])
        candidate_F = np.vstack([previous.F, off_F])
        candidate_CV = np.concatenate([previous.CV, off_CV])
        rank, crowding = assign_rank_and_crowding(candidate_F, candidate_CV)
        order = stable_survivor_order(rank, crowding, candidate_CV)[: self.population_size]

        successful = order[order >= previous.X.shape[0]] - previous.X.shape[0]
        if successful.size:
            for slot in np.unique(slots[successful]):
                mask = successful[slots[successful] == slot]
                self.memory_f[slot] = float(np.mean(F_weight[mask]))
                self.memory_cr[slot] = float(np.mean(CR[mask]))

        self.state = PopulationState(
            X=candidate_X[order],
            F=candidate_F[order],
            CV=candidate_CV[order],
            rank=rank[order],
            crowding=crowding[order],
        )
        self.archive = self.build_archive(self.state)
        self.n_gen += 1
        self._update_population_view()
        self._remember_state()
        self.after_generation(previous, self.state)


def make_madea(
    population_size: int = 100,
    archive_size: int = 100,
    mutation_rate: float = 0.1,
    memory_size: int = 6,
    p_best_fraction: float = 0.2,
    seed: int = 1,
) -> MADEA:
    """
    EN:
    Create a MADEA instance for the GUI registry.

    PL:
    Tworzy instancje MADEA dla rejestru GUI.
    """
    return MADEA(
        population_size=population_size,
        archive_size=archive_size,
        mutation_rate=mutation_rate,
        memory_size=memory_size,
        p_best_fraction=p_best_fraction,
        seed=seed,
    )


MADEA_DEFINITION: Dict[str, Any] = {
    "label": "MADEA",
    "factory": make_madea,
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 1},
        "archive_size": {"default": 100, "kind": "int", "minimum": 1},
        "mutation_rate": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "memory_size": {"default": 6, "kind": "int", "minimum": 1},
        "p_best_fraction": {"default": 0.2, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Own implementation based on the article. Uses adaptive current-to-pbest differential evolution with success-history memories.",
}
