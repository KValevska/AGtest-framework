# Standalone epsilon-MOEA implementation.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
# ------------------------------------------------------------------------------------
# Article: K. Deb, M. Mohan, S. Mishra, "Evaluating the epsilon-Domination Based
#          Multi-Objective Evolutionary Algorithm...", Evolutionary Computation, 2005.
# DOI: 10.1162/106365605774666895
# Implementation: own Python/NumPy steady-state implementation based on the article.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------
from typing import Any, Dict
import numpy as np
from .article_algorithms_common import EpsilonArchiveAlgorithm
from .research_common import (
    parse_epsilons,
    parse_positive_int,
    problem_n_obj,
    sbx_crossover,
)

class EpsMOEA(EpsilonArchiveAlgorithm):
    """Steady-state epsilon-MOEA with population and epsilon-box archive updates."""

    def create_offspring(self) -> np.ndarray:
        # The article selects one parent from the population and one from the archive.
        assert self.state is not None
        archive = self.archive if self.archive is not None and self.archive.X.size else self.state
        population_parent = int(self.select()[0, 0])
        archive_parent = int(self.random_state.integers(0, archive.X.shape[0]))
        parents = np.vstack((self.state.X[population_parent], archive.X[archive_parent]))
        child = sbx_crossover(
            parents,
            np.array([[0, 1]], dtype=int),
            self.xl,
            self.xu,
            self.crossover_eta,
            self.crossover_rate,
            self.random_state,
        )
        return self.mutation(child)

def make_eps_moea(problem: Any, population_size: int = 100, epsilons: Any = 0.01) -> EpsMOEA:
    size = parse_positive_int(population_size, "population_size")
    eps = np.asarray(parse_epsilons(epsilons, problem_n_obj(problem)), dtype=float)
    return EpsMOEA(epsilons=eps, steady_state=True, population_size=size, archive_size=size,
                   mutation_rate=1.0 / max(1, int(problem.n_var)))

EPS_MOEA_DEFINITION: Dict[str, Any] = {
    "label": "Eps-MOEA", "factory": make_eps_moea,
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 1, "tooltip": "Population size."},
        "epsilons": {"default": 0.01, "kind": "any", "tooltip": "Scalar or one epsilon per objective."},
    },
    "form_note": "Own Python epsilon-MOEA implementation (DOI: 10.1162/106365605774666895).",
}
