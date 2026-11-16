# Standalone NSGA-III implementation.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
# ------------------------------------------------------------------------------------
# Article: K. Deb, H. Jain, "An Evolutionary Many-Objective Optimization Algorithm
#          Using Reference-Point-Based Nondominated Sorting Approach, Part I", 2014.
# DOI: 10.1109/TEVC.2013.2281535
# Implementation: own Python/NumPy implementation based on the article.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------
from typing import Any, Dict
from .article_algorithms_common import NSGA3Algorithm
from .research_common import parse_positive_int, problem_n_obj

class NSGA3(NSGA3Algorithm):
    """NSGA-III with Deb-Jain normalization and reference-line niching."""

def make_nsga3(problem: Any, pop_size: int = 100, n_partitions: int = 12) -> NSGA3:
    n_obj = problem_n_obj(problem)
    size = parse_positive_int(pop_size, "pop_size")
    parts = parse_positive_int(n_partitions, "n_partitions")
    return NSGA3(population_size=size, archive_size=size, n_partitions=parts)

NSGA3_DEFINITION: Dict[str, Any] = {
    "label": "NSGA-III", "factory": make_nsga3,
    "form_fields": {
        "pop_size": {"default": 100, "kind": "int", "minimum": 1, "tooltip": "Population size."},
        "n_partitions": {"default": 12, "kind": "int", "minimum": 1, "tooltip": "Das-Dennis partitions."},
    },
    "form_note": "Own Python implementation of NSGA-III (DOI: 10.1109/TEVC.2013.2281535).",
}
