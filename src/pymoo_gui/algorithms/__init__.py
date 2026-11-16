# Algorithm registry and minimize dispatcher used by the GUI runtime.
# Provenance: AGtest-framework infrastructure; dispatches pymoo-compatible and local algorithms.

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
from pymoo_gui.problems.capabilities import algorithm_capabilities, infer_problem_variable_type

from .age import AGE_DEFINITION
from .cmoea_cd import CMOEA_CD_DEFINITION
from .cmobr import CMOBR_DEFINITION
from .common import GenerationPayload, known_pareto_front, make_generation_callback
from .disk import DISK_DEFINITION
from .diskplus import DISKPLUS_DEFINITION
from .dssea import DSSEA_DEFINITION
from .dvcea import DVCEA_DEFINITION
from .eps_moea import EPS_MOEA_DEFINITION
from .eps_nsga2 import EPS_NSGA2_DEFINITION
from .gde3 import GDE3_DEFINITION
from .ibea import IBEA_DEFINITION
from .lmoea_ds import LMOEA_DS_DEFINITION
from .maotspp import MAOTSPP_DEFINITION
from .moead import MOEAD_DEFINITION
from .learning_edmo import LEARNING_EDMO_DEFINITION
from .nsga2 import NSGA2_DEFINITION
from .nsga3 import NSGA3_DEFINITION
from .moead_iepsilon import MOEAD_IEPSILON_DEFINITION
from .pimd import PIMD_DEFINITION
from .piea import PIEA_DEFINITION
from .peaplus import PEAPLUS_DEFINITION
from .rnn_guided_dmo import RNN_GUIDED_DMO_DEFINITION
from .rnsga3 import RNSGA3_DEFINITION
from .rvea import RVEA_DEFINITION
from .spea2 import SPEA2_DEFINITION
from .ssde import SSDE_DEFINITION
from .ts_nsga import TS_NSGA_DEFINITION
from .tea import TEA_DEFINITION
from .tspp import TSPP_DEFINITION
from .umaoea import UMAOEA_DEFINITION

try:
    from .hype import HYPE_DEFINITION
except ImportError:
    HYPE_DEFINITION = None


ALGORITHMS: Dict[str, Dict[str, Any]] = {
    "age": AGE_DEFINITION,
    "cmoea_cd": CMOEA_CD_DEFINITION,
    "cmobr": CMOBR_DEFINITION,
    "disk": DISK_DEFINITION,
    "diskplus": DISKPLUS_DEFINITION,
    "dssea": DSSEA_DEFINITION,
    "dvcea": DVCEA_DEFINITION,
    "eps_moea": EPS_MOEA_DEFINITION,
    "eps_nsga2": EPS_NSGA2_DEFINITION,
    "gde3": GDE3_DEFINITION,
    "ibea": IBEA_DEFINITION,
    "learning_edmo": LEARNING_EDMO_DEFINITION,
    "lmoea_ds": LMOEA_DS_DEFINITION,
    "maotspp": MAOTSPP_DEFINITION,
    "moead": MOEAD_DEFINITION,
    "nsga2": NSGA2_DEFINITION,
    "nsga3": NSGA3_DEFINITION,
    "moead_iepsilon": MOEAD_IEPSILON_DEFINITION,
    "pimd": PIMD_DEFINITION,
    "piea": PIEA_DEFINITION,
    "peaplus": PEAPLUS_DEFINITION,
    "rnn_guided_dmo": RNN_GUIDED_DMO_DEFINITION,
    "rnsga3": RNSGA3_DEFINITION,
    "rvea": RVEA_DEFINITION,
    "spea2": SPEA2_DEFINITION,
    "ssde": SSDE_DEFINITION,
    "ts_nsga": TS_NSGA_DEFINITION,
    "tea": TEA_DEFINITION,
    "tspp": TSPP_DEFINITION,
    "umaoea": UMAOEA_DEFINITION,
}
if HYPE_DEFINITION is not None:
    ALGORITHMS["hype"] = HYPE_DEFINITION

# References missing from older per-module definitions are completed here so
# every registry entry exposes one uniform, auditable provenance schema.
_ALGORITHM_REFERENCES = {
    "age": "A. Panichella, GECCO 2019, DOI 10.1145/3321707.3321839",
    "eps_moea": "K. Deb, M. Mohan and S. Mishra, Evolutionary Computation 13(4), 2005, DOI 10.1162/106365605774666895",
    "gde3": "S. Kukkonen and J. Lampinen, CEC 2005, DOI 10.1109/CEC.2005.1554717",
    "ibea": "E. Zitzler and S. Künzli, Indicator-Based Selection in Multiobjective Search, PPSN VIII, 2004",
    "lmoea_ds": "S. Qin et al., Large-scale Evolutionary Multi-objective Optimization Assisted by Directed Sampling, IEEE TEVC, 2021",
    "moead": "Q. Zhang and H. Li, IEEE TEVC 11(6), 2007, DOI 10.1109/TEVC.2007.892759",
    "nsga2": "K. Deb et al., IEEE TEVC 6(2), 2002, DOI 10.1109/4235.996017",
    "nsga3": "K. Deb and H. Jain, IEEE TEVC 18(4), 2014, DOI 10.1109/TEVC.2013.2281535",
    "rnsga3": "Y. Vesikar, K. Deb and J. Blank, IEEE SSCI 2018, DOI 10.1109/SSCI.2018.8628819",
    "rvea": "R. Cheng et al., IEEE TEVC 20(5), 2016, DOI 10.1109/TEVC.2016.2519378",
    "spea2": "E. Zitzler, M. Laumanns and L. Thiele, TIK Report 103, 2001, DOI 10.3929/ethz-a-004284029",
    "hype": "J. Bader and E. Zitzler, Evolutionary Computation 19(1), 2011, DOI 10.1162/EVCO_A_00009",
}
_IMPLEMENTATION_TYPES = {"pymoo", "adapter", "faithful_port", "adapted_port", "framework_variant"}

for _key, _entry in ALGORITHMS.items():
    # All currently registered optimizers are local article-based ports. None
    # has evidence sufficient for the stronger `faithful_port` classification.
    if _entry.get("implementation_type") in (None, "standalone_python_implementation"):
        _entry["implementation_type"] = "adapted_port"
    _entry.setdefault("reference", _ALGORITHM_REFERENCES.get(_key))
    _entry.setdefault("source_commit", None)
    _entry.setdefault(
        "verified_against",
        "Article mechanisms and deterministic runtime tests; no claim of statistical equivalence",
    )
    if not _entry["reference"]:
        raise ValueError(f"Algorithm '{_key}' is missing a bibliographic reference.")
    if _entry["implementation_type"] not in _IMPLEMENTATION_TYPES:
        raise ValueError(f"Algorithm '{_key}' has an unsupported implementation_type.")

for _entry in ALGORITHMS.values():
    _entry.setdefault("capabilities", algorithm_capabilities(variable_types=("real",)))

# Dynamic algorithms implement their own change-response policies and must remain
# selectable for the local DF benchmark family.
for _key in ("learning_edmo", "rnn_guided_dmo"):
    if _key in ALGORITHMS:
        ALGORITHMS[_key]["capabilities"]["dynamic"] = True

# These two standalone algorithms use the encoding-aware variation layer.
for _key in ("nsga2", "spea2"):
    if _key in ALGORITHMS:
        ALGORITHMS[_key]["capabilities"] = algorithm_capabilities(
            variable_types=("real", "binary", "integer", "mixed"),
            constraints=True,
            dynamic=True,
        )


class AlgorithmProblemCompatibilityError(ValueError):
    # Raised when an algorithm cannot operate on the selected problem class.

    pass


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


def validate_algorithm_problem(algorithm_entry: Dict[str, Any], problem: Any) -> None:
    # Reject unsupported algorithm/problem combinations before a run is started.
    try:
        n_constraints = int(getattr(problem, "n_ieq_constr", 0) or 0) + int(
            getattr(problem, "n_eq_constr", 0) or 0
        )
        if n_constraints == 0:
            n_constraints = int(getattr(problem, "n_constr", 0) or 0)
    except (TypeError, ValueError):
        n_constraints = 0
    if algorithm_entry.get("requires_constraints"):
        if n_constraints <= 0:
            label = str(algorithm_entry.get("label") or "Selected algorithm")
            raise AlgorithmProblemCompatibilityError(
                f"{label} requires a benchmark with at least one inequality constraint."
            )
    if algorithm_entry.get("supports_constraints") is False and n_constraints > 0:
        label = str(algorithm_entry.get("label") or "Selected algorithm")
        raise AlgorithmProblemCompatibilityError(
            f"{label} supports only unconstrained benchmarks."
        )
    capabilities = algorithm_entry.get("capabilities") or {}
    variable_type = infer_problem_variable_type(problem)
    supported = set(capabilities.get("variable_types") or {"real"})
    if variable_type not in supported:
        label = str(algorithm_entry.get("label") or "Selected algorithm")
        raise AlgorithmProblemCompatibilityError(
            f"{label} does not provide {variable_type} variation operators; supported encodings: {', '.join(sorted(supported))}."
        )
    if n_constraints > 0 and capabilities.get("constraints", True) is False:
        label = str(algorithm_entry.get("label") or "Selected algorithm")
        raise AlgorithmProblemCompatibilityError(f"{label} does not support constrained benchmarks.")
    if bool(getattr(problem, "is_dynamic", False)) and not capabilities.get("dynamic", False):
        label = str(algorithm_entry.get("label") or "Selected algorithm")
        raise AlgorithmProblemCompatibilityError(
            f"{label} has no validated dynamic-response policy; use NSGA-II or SPEA2 as a restart/reevaluation baseline."
        )


def compatibility_matrix(problems: Dict[str, Dict[str, Any]]) -> list[Dict[str, str]]:
    """Build an auditable algorithm/problem matrix including rejection reasons."""
    rows: list[Dict[str, str]] = []
    for problem_key, problem_entry in problems.items():
        defaults = {
            name: spec.get("default")
            for name, spec in (problem_entry.get("form_fields") or {}).items()
            if isinstance(spec, dict) and "default" in spec and not spec.get("read_only")
        }
        factory = problem_entry["factory"]
        try:
            problem = factory(**defaults)
        except TypeError:
            problem = factory()
        for algorithm_key, algorithm_entry in ALGORITHMS.items():
            try:
                validate_algorithm_problem(algorithm_entry, problem)
                status, reason = "supported", "capabilities match"
            except AlgorithmProblemCompatibilityError as exc:
                status, reason = "blocked", str(exc)
            rows.append({"algorithm": algorithm_key, "problem": problem_key, "status": status, "reason": reason})
    return rows


__all__ = [
    "ALGORITHMS",
    "AlgorithmProblemCompatibilityError",
    "GenerationPayload",
    "known_pareto_front",
    "make_generation_callback",
    "minimize",
    "validate_algorithm_problem",
    "compatibility_matrix",
]
