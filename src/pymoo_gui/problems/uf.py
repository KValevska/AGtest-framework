"""
EN:
UF benchmark family adapters for pymoo.

PL:
Definiuje adaptery problemow UF1-UF10 z biblioteki Platypus.
"""

# ------------------------------------------------------------------------------------
# File: uf.py
# Contents: UF benchmark family wrappers exposing Platypus problems as pymoo problems.
# What happens here: Platypus UF problem instances are adapted to pymoo's `Problem` interface.
# Role in the framework: provides the CEC2009 UF benchmark family in the same GUI workflow as local problems.
# Author: mgr inz. Kristina Valevska
# Implementation source: Platypus
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Type

import numpy as np
from pymoo.core.problem import Problem


def _platypus_solution_class() -> Any:
    try:
        from platypus.core import Solution
    except ImportError:
        from platypus import Solution
    return Solution


def _platypus_uf_class(name: str) -> Type[Any]:
    from platypus.problems import UF1, UF2, UF3, UF4, UF5, UF6, UF7, UF8, UF9, UF10

    mapping = {
        "UF1": UF1,
        "UF2": UF2,
        "UF3": UF3,
        "UF4": UF4,
        "UF5": UF5,
        "UF6": UF6,
        "UF7": UF7,
        "UF8": UF8,
        "UF9": UF9,
        "UF10": UF10,
    }
    return mapping[name]


class PlatypusUFProblem(Problem):
    """
    EN:
    Adapt one Platypus UF benchmark to pymoo's `Problem` interface.

    PL:
    Tlumaczy wybrany problem UF z Platypus na interfejs oczekiwany przez GUI.
    """

    def __init__(self, uf_name: str, n_var: int = 30):
        uf_class = _platypus_uf_class(uf_name)
        self._platypus_problem = uf_class(nvars=int(n_var))
        self._platypus_solution_type = _platypus_solution_class()
        self._uf_name = str(uf_name)

        lower_bounds = []
        upper_bounds = []
        for var_type in self._platypus_problem.types:
            lower_bounds.append(float(getattr(var_type, "min_value")))
            upper_bounds.append(float(getattr(var_type, "max_value")))

        super().__init__(
            n_var=int(self._platypus_problem.nvars),
            n_obj=int(self._platypus_problem.nobjs),
            n_constr=int(getattr(self._platypus_problem, "nconstrs", 0)),
            xl=np.asarray(lower_bounds, dtype=float),
            xu=np.asarray(upper_bounds, dtype=float),
        )

    def _evaluate_one(self, values: np.ndarray) -> tuple[list[float], list[float]]:
        solution = self._platypus_solution_type(self._platypus_problem)
        solution.variables[:] = [float(value) for value in values.tolist()]
        self._platypus_problem.evaluate(solution)
        objectives = [float(value) for value in solution.objectives]
        constraints = [float(value) for value in getattr(solution, "constraints", [])]
        return objectives, constraints

    def _evaluate(self, X, out, *args, **kwargs):
        objectives = []
        constraints = []

        for row in np.asarray(X, dtype=float):
            row_objectives, row_constraints = self._evaluate_one(row)
            objectives.append(row_objectives)
            if row_constraints:
                constraints.append(row_constraints)

        out["F"] = np.asarray(objectives, dtype=float)
        if constraints:
            out["G"] = np.asarray(constraints, dtype=float)


class UF1Problem(PlatypusUFProblem):
    def __init__(self, n_var: int = 30):
        super().__init__("UF1", n_var=n_var)


class UF2Problem(PlatypusUFProblem):
    def __init__(self, n_var: int = 30):
        super().__init__("UF2", n_var=n_var)


class UF3Problem(PlatypusUFProblem):
    def __init__(self, n_var: int = 30):
        super().__init__("UF3", n_var=n_var)


class UF4Problem(PlatypusUFProblem):
    def __init__(self, n_var: int = 30):
        super().__init__("UF4", n_var=n_var)


class UF5Problem(PlatypusUFProblem):
    def __init__(self, n_var: int = 30):
        super().__init__("UF5", n_var=n_var)


class UF6Problem(PlatypusUFProblem):
    def __init__(self, n_var: int = 30):
        super().__init__("UF6", n_var=n_var)


class UF7Problem(PlatypusUFProblem):
    def __init__(self, n_var: int = 30):
        super().__init__("UF7", n_var=n_var)


class UF8Problem(PlatypusUFProblem):
    def __init__(self, n_var: int = 30):
        super().__init__("UF8", n_var=n_var)


class UF9Problem(PlatypusUFProblem):
    def __init__(self, n_var: int = 30):
        super().__init__("UF9", n_var=n_var)


class UF10Problem(PlatypusUFProblem):
    def __init__(self, n_var: int = 30):
        super().__init__("UF10", n_var=n_var)
