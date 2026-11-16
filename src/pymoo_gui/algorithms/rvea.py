# Standalone RVEA implementation.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
# ------------------------------------------------------------------------------------
# Article: R. Cheng et al., "A Reference Vector Guided Evolutionary Algorithm for
#          Many-Objective Optimization", IEEE TEC, 2016.
# DOI: 10.1109/TEVC.2016.2519378
# Implementation: own Python/NumPy implementation based on the article.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------
from typing import Any, Dict, Optional
import numpy as np
from .research_common import (
    PopulationState, ResearchMOOAlgorithm, assign_rank_and_crowding, feasible_mask,
    parse_positive_float, parse_positive_int, problem_n_obj, termination_generations,
)

class RVEA(ResearchMOOAlgorithm):
    """RVEA with angle-penalized distance and adaptive reference vectors."""
    def __init__(self, alpha: float = 2.0, adapt_freq: float = 0.1, **kwargs):
        super().__init__(**kwargs)
        self.alpha = parse_positive_float(alpha, "alpha")
        self.adapt_freq = parse_positive_float(adapt_freq, "adapt_freq")
        self.base_vectors = np.empty((0, 0))
        self.maximum_generations = 100

    def gui_minimize(self, *, problem, termination, **kwargs):
        # APD uses the actual run horizon t/t_max from the article.
        self.maximum_generations = termination_generations(termination) or 100
        return super().gui_minimize(problem=problem, termination=termination, **kwargs)

    def after_initialize(self) -> None:
        assert self.reference_directions is not None
        if self.reference_directions.shape[0] > self.population_size:
            ids = np.linspace(0, self.reference_directions.shape[0] - 1, self.population_size).astype(int)
            self.reference_directions = self.reference_directions[ids]
        self.base_vectors = self.reference_directions.copy()

    def environmental_selection(self, X, F, CV, n_survive):
        assert self.reference_directions is not None
        feasible = np.flatnonzero(feasible_mask(CV))
        candidates = feasible if feasible.size else np.argsort(CV)[:n_survive]
        Y = F[candidates] - np.min(F[candidates], axis=0)
        norms = np.maximum(np.linalg.norm(Y, axis=1), 1e-15)
        vectors = self.reference_directions / np.maximum(np.linalg.norm(self.reference_directions, axis=1, keepdims=True), 1e-15)
        cosine = np.clip((Y / norms[:, None]) @ vectors.T, -1.0, 1.0)
        angles = np.arccos(cosine)
        association = np.argmin(angles, axis=1)
        vector_angles = np.arccos(np.clip(vectors @ vectors.T, -1.0, 1.0))
        np.fill_diagonal(vector_angles, np.inf)
        gamma = np.maximum(np.min(vector_angles, axis=1), 1e-12)
        progress = min(1.0, (self.n_gen + 1) / max(1, self.maximum_generations))
        penalty = F.shape[1] * progress ** self.alpha * angles[np.arange(candidates.size), association] / gamma[association]
        apd = norms * (1.0 + penalty)
        chosen = []
        for niche in np.unique(association):
            local = np.flatnonzero(association == niche)
            chosen.append(int(candidates[local[np.argmin(apd[local])]]))
        if len(chosen) < n_survive:
            remaining = [int(i) for i in candidates[np.argsort(apd)] if int(i) not in chosen]
            chosen.extend(remaining[: n_survive - len(chosen)])
        if len(chosen) < n_survive:
            remaining = [int(i) for i in np.argsort(CV) if int(i) not in chosen]
            chosen.extend(remaining[: n_survive - len(chosen)])
        ids = np.asarray(chosen[:n_survive], dtype=int)
        rank, crowding = assign_rank_and_crowding(F[ids], CV[ids])
        return PopulationState(X[ids], F[ids], CV[ids], rank, crowding)

    def after_generation(self, previous, current) -> None:
        interval = max(1, int(round(min(self.adapt_freq, 1.0) * self.maximum_generations)))
        if self.n_gen % interval == 0:
            span = np.maximum(np.max(current.F, axis=0) - np.min(current.F, axis=0), 1e-12)
            adapted = self.base_vectors * span[None, :]
            self.reference_directions = adapted / np.maximum(np.linalg.norm(adapted, axis=1, keepdims=True), 1e-15)

def make_rvea(problem: Any, pop_size: Optional[int] = 100, n_partitions: int = 99,
              alpha: float = 2.0, adapt_freq: float = 0.1) -> RVEA:
    problem_n_obj(problem)
    size = 100 if pop_size is None else parse_positive_int(pop_size, "pop_size")
    return RVEA(population_size=size, archive_size=size,
                n_partitions=parse_positive_int(n_partitions, "n_partitions"),
                alpha=alpha, adapt_freq=adapt_freq,
                mutation_rate=1.0 / max(1, int(problem.n_var)))

RVEA_DEFINITION: Dict[str, Any] = {
    "label": "RVEA", "factory": make_rvea,
    "form_fields": {
        "pop_size": {"default": 100, "kind": "int", "minimum": 1, "tooltip": "Population size."},
        "n_partitions": {"default": 99, "kind": "int", "minimum": 1, "tooltip": "Reference-vector partitions."},
        "alpha": {"default": 2.0, "kind": "float", "minimum": 1e-10, "tooltip": "APD alpha."},
        "adapt_freq": {"default": 0.1, "kind": "float", "minimum": 1e-10, "tooltip": "Adaptation frequency."},
    },
    "form_note": "Own Python implementation of RVEA (DOI: 10.1109/TEVC.2016.2519378).",
}
