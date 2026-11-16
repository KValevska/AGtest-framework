# Standalone MOEA/D implementation.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
# ------------------------------------------------------------------------------------
# Article: Q. Zhang, H. Li, "MOEA/D: A Multiobjective Evolutionary Algorithm Based
#          on Decomposition", IEEE Transactions on Evolutionary Computation, 2007.
# DOI: 10.1109/TEVC.2007.892759
# Implementation: own Python/NumPy implementation based on the article.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------
from typing import Any, Dict
from .article_algorithms_common import MOEADAlgorithm
from .research_common import das_dennis_reference_directions, parse_positive_int, parse_probability, problem_n_obj

class MOEAD(MOEADAlgorithm):
    """MOEA/D with Tchebycheff aggregation and neighborhood replacement."""

def make_moead(problem: Any, n_partitions: int = 12, n_neighbors: int = 15, prob_neighbor_mating: float = 0.7) -> MOEAD:
    parts = parse_positive_int(n_partitions, "n_partitions")
    size = len(das_dennis_reference_directions(problem_n_obj(problem), parts))
    return MOEAD(population_size=size, archive_size=size, n_partitions=parts,
                 n_neighbors=min(parse_positive_int(n_neighbors, "n_neighbors"), size),
                 prob_neighbor_mating=parse_probability(prob_neighbor_mating, "prob_neighbor_mating"),
                 mutation_rate=1.0 / max(1, int(problem.n_var)))

MOEAD_DEFINITION: Dict[str, Any] = {
    "label": "MOEAD", "factory": make_moead,
    "form_fields": {
        "n_partitions": {"default": 12, "kind": "int", "minimum": 1, "tooltip": "Das-Dennis partitions."},
        "n_neighbors": {"default": 15, "kind": "int", "minimum": 1, "tooltip": "Neighborhood size."},
        "prob_neighbor_mating": {"default": 0.7, "kind": "float", "minimum": 0.0, "maximum": 1.0, "tooltip": "Neighborhood mating probability."},
    },
    "form_note": "Own Python implementation of MOEA/D (DOI: 10.1109/TEVC.2007.892759).",
}
