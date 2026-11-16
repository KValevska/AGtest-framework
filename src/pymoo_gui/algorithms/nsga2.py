# Standalone NSGA-II implementation.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
# ------------------------------------------------------------------------------------
# Article: K. Deb et al., "A Fast and Elitist Multiobjective Genetic Algorithm:
#          NSGA-II", IEEE Transactions on Evolutionary Computation, 2002.
# DOI: 10.1109/4235.996017
# Implementation: own Python/NumPy implementation based on the article.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------
from typing import Any, Dict
from .research_common import ResearchMOOAlgorithm, parse_positive_int

class NSGA2(ResearchMOOAlgorithm):
    """NSGA-II with binary tournament, SBX, polynomial mutation and crowding."""

def make_nsga2(pop_size: int = 100) -> NSGA2:
    size = parse_positive_int(pop_size, "pop_size")
    return NSGA2(population_size=size, archive_size=size)

NSGA2_DEFINITION: Dict[str, Any] = {
    "label": "NSGA-II", "factory": make_nsga2,
    "form_note": "Own Python implementation of NSGA-II (DOI: 10.1109/4235.996017).",
}
