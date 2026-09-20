# Template module for implementing a custom pymoo-compatible benchmark problem.

# ------------------------------------------------------------------------------------
# Module: empty_benchmark_template.py
# Summary: template benchmark class, factory, Pareto-front hook and optional GUI definition.
# Implementation: the module provides a working many-objective skeleton with explicit
# extension points for bounds, objective functions, constraints and reference-front data.
# Responsibility: serves as the starting point for implementing a new benchmark problem
# that remains compatible with the GUI, metrics, exports and pymoo execution flow.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import math
from typing import Any, Dict, Optional

import numpy as np
from pymoo.core.problem import Problem


class EmptyBenchmarkTemplate(Problem):
    # Minimal vectorized benchmark template compatible with pymoo and the GUI.

    implementation_source = "template for user implementation"

    def __init__(
        self,
        n_var: int = 10,
        n_obj: int = 2,
        lower_bound: float = -1.0,
        upper_bound: float = 1.0,
    ) -> None:
        # Validate dimensions and initialize the benchmark metadata and bounds.
        # Args:
        # n_var (int): Number of decision variables.
        # n_obj (int): Number of objective functions.
        # lower_bound (float): Shared lower bound for every decision variable.
        # upper_bound (float): Shared upper bound for every decision variable.
        parsed_n_var = int(n_var)
        parsed_n_obj = int(n_obj)
        parsed_lower_bound = float(lower_bound)
        parsed_upper_bound = float(upper_bound)
        if parsed_n_var < 1:
            raise ValueError("n_var must be at least 1")
        if parsed_n_obj < 2:
            raise ValueError("n_obj must be at least 2")
        if not math.isfinite(parsed_lower_bound) or not math.isfinite(parsed_upper_bound):
            raise ValueError("Bounds must be finite")
        if parsed_lower_bound >= parsed_upper_bound:
            raise ValueError("lower_bound must be smaller than upper_bound")

        super().__init__(
            n_var=parsed_n_var,
            n_obj=parsed_n_obj,
            n_ieq_constr=0,
            n_eq_constr=0,
            xl=np.full(parsed_n_var, parsed_lower_bound, dtype=float),
            xu=np.full(parsed_n_var, parsed_upper_bound, dtype=float),
        )

    def _evaluate(self, X, out, *args, **kwargs) -> None:
        # Evaluate a batch of decision vectors and write an objective matrix to out["F"].
        # Args:
        # X: Decision matrix with shape (n_points, n_var).
        # out: Output dictionary populated with objective and optional constraint matrices.
        # *args: Additional positional arguments accepted for pymoo compatibility.
        # **kwargs: Additional keyword arguments accepted for pymoo compatibility.
        decision_matrix = np.asarray(X, dtype=float)
        if decision_matrix.ndim != 2 or decision_matrix.shape[1] != self.n_var:
            raise ValueError(f"X must have shape (n_points, {self.n_var})")

        # Replace this placeholder objective block with the benchmark equations.
        # Each generated objective is a sphere centered at a different scalar value.
        centers = np.linspace(0.0, 1.0, self.n_obj, dtype=float)
        objectives = [
            np.sum((decision_matrix - center) ** 2, axis=1)
            for center in centers
        ]
        out["F"] = np.column_stack(objectives)

        # To add inequality constraints, set n_ieq_constr in __init__ and write out["G"].
        # Pymoo treats an inequality constraint as feasible when its value is <= 0.
        # Example for sum(x) <= 0: out["G"] = np.sum(decision_matrix, axis=1)[:, None]

        # To add equality constraints, set n_eq_constr in __init__ and write out["H"].
        # Equality residuals should be zero for feasible solutions.


def empty_benchmark_known_pf(
    problem: EmptyBenchmarkTemplate,
    n_points: int = 200,
) -> Optional[np.ndarray]:
    # Return reference Pareto-front points after the custom benchmark defines them.
    # Args:
    # problem (EmptyBenchmarkTemplate): Configured benchmark instance.
    # n_points (int): Requested number of reference points.
    # Returns:
    # Optional[np.ndarray]: Matrix with shape (n_points, n_obj), or None when unavailable.
    # Replace this placeholder with an analytical generator or load a local .pf file.
    _ = problem, n_points
    return None


def make_empty_benchmark_template(
    n_var: int = 10,
    n_obj: int = 2,
    lower_bound: float = -1.0,
    upper_bound: float = 1.0,
) -> EmptyBenchmarkTemplate:
    # Factory creating a ready-to-edit benchmark template instance.
    return EmptyBenchmarkTemplate(
        n_var=n_var,
        n_obj=n_obj,
        lower_bound=lower_bound,
        upper_bound=upper_bound,
    )


EMPTY_BENCHMARK_TEMPLATE_DEFINITION: Dict[str, Any] = {
    "label": "Empty Benchmark Template",
    "factory": make_empty_benchmark_template,
    "form_fields": {
        "n_var": {
            "default": 10,
            "kind": "int",
            "minimum": 1,
            "tooltip": "Number of decision variables used by the benchmark.",
        },
        "n_obj": {
            "default": 2,
            "kind": "int",
            "minimum": 2,
            "tooltip": "Number of objective functions returned by the benchmark.",
        },
        "lower_bound": {
            "default": -1.0,
            "kind": "float",
            "tooltip": "Shared lower bound for all decision variables.",
        },
        "upper_bound": {
            "default": 1.0,
            "kind": "float",
            "tooltip": "Shared upper bound for all decision variables.",
        },
    },
    "form_note": (
        "Template for implementing a new pymoo-compatible benchmark. "
        "Register this definition in problems/registry.py only after replacing the placeholder equations."
    ),
    "known_pf_factory": empty_benchmark_known_pf,
}
