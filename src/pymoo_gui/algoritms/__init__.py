"""
EN: Algorithm registry and minimize dispatcher used by the GUI runtime.
"""

# ------------------------------------------------------------------------------------
# File: __init__.py
# Contents: algorithm registry, shared payload exports and pymoo minimize dispatch wrapper.
# What happens here: available algorithm definitions are assembled and custom gui_minimize runners are honored.
# Role in the framework: centralizes optimization algorithm access for the dissertation GUI workflow.
# Author: mgr inż. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

from pymoo.optimize import minimize as _pymoo_minimize

from .age import AGE_DEFINITION
from .cm_moea import CM_MOEA_DEFINITION
from .common import GenerationPayload, known_pareto_front, make_generation_callback
from .dd_m2m import DD_M2M_DEFINITION
from .dida import DIDA_DEFINITION
from .dm_dmoea_diffusion import DM_DMOEA_DIFFUSION_DEFINITION
from .dm_dmoea_dual_mutation import DM_DMOEA_DUAL_MUTATION_DEFINITION
from .eps_moea import EPS_MOEA_DEFINITION
from .eps_nsga2 import EPS_NSGA2_DEFINITION
from .moead import MOEAD_DEFINITION
from .madea import MADEA_DEFINITION
from .learning_edmo import LEARNING_EDMO_DEFINITION
from .moea_sd import MOEA_SD_DEFINITION
from .nsga2 import NSGA2_DEFINITION
from .nsgaii_miip import NSGAII_MIIP_DEFINITION
from .nsga3 import NSGA3_DEFINITION
from .platypus_moead import PLATYPUS_MOEAD_DEFINITION
from .ql_imoga import QL_IMOGA_DEFINITION
from .rnn_guided_dmo import RNN_GUIDED_DMO_DEFINITION
from .rnsga3 import RNSGA3_DEFINITION
from .rvea import RVEA_DEFINITION
from .sea import SEA_DEFINITION
from .spea2 import SPEA2_DEFINITION
from .ts_nsga import TS_NSGA3_DEFINITION, TS_NSGA_DEFINITION
from .vare import VARE_DEFINITION

try:
    from .hype import HYPE_DEFINITION
except ImportError:
    HYPE_DEFINITION = None


ALGORITHMS: Dict[str, Dict[str, Any]] = {
    "age": AGE_DEFINITION,
    "cm_moea": CM_MOEA_DEFINITION,
    "dd_m2m": DD_M2M_DEFINITION,
    "dida": DIDA_DEFINITION,
    "dm_dmoea_diffusion": DM_DMOEA_DIFFUSION_DEFINITION,
    "dm_dmoea_dual_mutation": DM_DMOEA_DUAL_MUTATION_DEFINITION,
    "eps_moea": EPS_MOEA_DEFINITION,
    "eps_nsga2": EPS_NSGA2_DEFINITION,
    "learning_edmo": LEARNING_EDMO_DEFINITION,
    "madea": MADEA_DEFINITION,
    "moead": MOEAD_DEFINITION,
    "moea_sd": MOEA_SD_DEFINITION,
    "nsga2": NSGA2_DEFINITION,
    "nsgaii_miip": NSGAII_MIIP_DEFINITION,
    "nsga3": NSGA3_DEFINITION,
    "platypus_moead": PLATYPUS_MOEAD_DEFINITION,
    "ql_imoga": QL_IMOGA_DEFINITION,
    "rnn_guided_dmo": RNN_GUIDED_DMO_DEFINITION,
    "rnsga3": RNSGA3_DEFINITION,
    "rvea": RVEA_DEFINITION,
    "sea": SEA_DEFINITION,
    "spea2": SPEA2_DEFINITION,
    "ts_nsga": TS_NSGA_DEFINITION,
    "ts_nsga3": TS_NSGA3_DEFINITION,
    "vare": VARE_DEFINITION,
}
if HYPE_DEFINITION is not None:
    ALGORITHMS["hype"] = HYPE_DEFINITION


def minimize(problem: Any, algorithm: Any, termination: Any, **kwargs: Any) -> Any:
    """
    EN:
    Dispatch optimization to an algorithm-specific GUI runner when available,
    otherwise fall back to `pymoo.optimize.minimize`.
    Args:
        problem (Any): EN: Optimization problem passed to the optimizer.
                       PL: Problem, dla ktorego szukane sa najlepsze rozwiazania.
        algorithm (Any): EN: Configured pymoo-compatible algorithm instance.
                         PL: Wybrany i skonfigurowany algorytm.
        termination (Any): EN: Termination criterion accepted by pymoo or adapter code.
                           PL: Warunek okreslajacy, kiedy obliczenia maja sie zakonczyc.
        **kwargs (Any): EN: Additional optimizer options, such as seed, verbosity or callback.
                        PL: Dodatkowe ustawienia uruchomienia, np. ziarno losowe lub callback.

    Returns:
        Any: EN: Optimization result returned by pymoo or the adapter.
             PL: Wynik optymalizacji zawierajacy znalezione rozwiazania.
    """
    runner = getattr(algorithm, "gui_minimize", None)
    if callable(runner):
        return runner(problem=problem, termination=termination, **kwargs)
    return _pymoo_minimize(problem, algorithm, termination, **kwargs)


__all__ = [
    "ALGORITHMS",
    "GenerationPayload",
    "known_pareto_front",
    "make_generation_callback",
    "minimize",
]
