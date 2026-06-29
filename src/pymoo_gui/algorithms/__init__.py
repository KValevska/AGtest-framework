# Algorithm registry and minimize dispatcher used by the GUI runtime.

# ------------------------------------------------------------------------------------
# Module: __init__.py
# Summary: algorithm registry, shared payload exports and pymoo minimize dispatch wrapper.
# Implementation: available algorithm definitions are assembled and custom gui_minimize runners are honored.
# Responsibility: centralizes optimization algorithm access for the dissertation GUI workflow.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

from pymoo.optimize import minimize as _pymoo_minimize

from .age import AGE_DEFINITION
from .common import GenerationPayload, known_pareto_front, make_generation_callback
from .eps_moea import EPS_MOEA_DEFINITION
from .eps_nsga2 import EPS_NSGA2_DEFINITION
from .gde3 import GDE3_DEFINITION
from .ibea import IBEA_DEFINITION
from .lmoea_ds import LMOEA_DS_DEFINITION
from .moead import MOEAD_DEFINITION
from .learning_edmo import LEARNING_EDMO_DEFINITION
from .nsga2 import NSGA2_DEFINITION
from .nsga3 import NSGA3_DEFINITION
from .platypus_moead import PLATYPUS_MOEAD_DEFINITION
from .rnn_guided_dmo import RNN_GUIDED_DMO_DEFINITION
from .rnsga3 import RNSGA3_DEFINITION
from .rvea import RVEA_DEFINITION
from .spea2 import SPEA2_DEFINITION
from .ts_nsga import TS_NSGA_DEFINITION

try:
    from .hype import HYPE_DEFINITION
except ImportError:
    HYPE_DEFINITION = None


ALGORITHMS: Dict[str, Dict[str, Any]] = {
    "age": AGE_DEFINITION,
    "eps_moea": EPS_MOEA_DEFINITION,
    "eps_nsga2": EPS_NSGA2_DEFINITION,
    "gde3": GDE3_DEFINITION,
    "ibea": IBEA_DEFINITION,
    "learning_edmo": LEARNING_EDMO_DEFINITION,
    "lmoea_ds": LMOEA_DS_DEFINITION,
    "moead": MOEAD_DEFINITION,
    "nsga2": NSGA2_DEFINITION,
    "nsga3": NSGA3_DEFINITION,
    "platypus_moead": PLATYPUS_MOEAD_DEFINITION,
    "rnn_guided_dmo": RNN_GUIDED_DMO_DEFINITION,
    "rnsga3": RNSGA3_DEFINITION,
    "rvea": RVEA_DEFINITION,
    "spea2": SPEA2_DEFINITION,
    "ts_nsga": TS_NSGA_DEFINITION,
}
if HYPE_DEFINITION is not None:
    ALGORITHMS["hype"] = HYPE_DEFINITION


def minimize(problem: Any, algorithm: Any, termination: Any, **kwargs: Any) -> Any:
    # Dispatch optimization to an algorithm-specific GUI runner when available,
    # otherwise fall back to `pymoo.optimize.minimize`.
    # Args:
    # problem (Any): Optimization problem passed to the optimizer.
    # algorithm (Any): Configured pymoo-compatible algorithm instance.
    # termination (Any): Termination criterion accepted by pymoo or adapter code.
    # **kwargs (Any): Additional optimizer options, such as seed, verbosity or callback.
    # Returns:
    # Any: Optimization result returned by pymoo or the adapter.
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
