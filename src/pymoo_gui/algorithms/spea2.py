# Standalone SPEA2 implementation.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
# ------------------------------------------------------------------------------------
# Article: E. Zitzler, M. Laumanns, L. Thiele, "SPEA2: Improving the Strength
#          Pareto Evolutionary Algorithm", TIK Report 103, ETH Zurich, 2001.
# DOI: 10.3929/ethz-a-004284029
# Implementation: own Python/NumPy implementation based on the article.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------
from typing import Any, Dict
from .article_algorithms_common import SPEA2Algorithm
from .research_common import parse_positive_int

class SPEA2(SPEA2Algorithm):
    """SPEA2 strength/raw fitness, density estimation and archive truncation."""

def make_spea2(pop_size: int = 100) -> SPEA2:
    size = parse_positive_int(pop_size, "pop_size")
    return SPEA2(population_size=size, archive_size=size)

SPEA2_DEFINITION: Dict[str, Any] = {
    "label": "SPEA2", "factory": make_spea2,
    "form_note": "Own Python implementation of SPEA2 (DOI: 10.3929/ethz-a-004284029).",
}
