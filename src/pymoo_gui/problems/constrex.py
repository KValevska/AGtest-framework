# ConstrEx constrained benchmark problem implementation for pymoo.

# ------------------------------------------------------------------------------------
# Module: constrex.py
# Summary: ConstrEx benchmark problem class for pymoo.
# Implementation: decision vectors are evaluated into the classical two-objective ConstrEx formulation.
# Responsibility: provides a constrained non-convex-search benchmark for GUI experiments.
# Author: Kristina Valevska, MSc Eng.
# Implementation source: own implementation based on benchmark definition used in the literature.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import numpy as np
from pymoo.core.problem import Problem


class ConstrExProblem(Problem):
    # Two-objective constrained ConstrEx benchmark.
    # Problem z nieciaglym obszarem dopuszczalnym i wypuklym frontem Pareto.

    def __init__(self):
        super().__init__(
            n_var=2,
            n_obj=2,
            n_ieq_constr=2,
            xl=np.array([0.1, 0.0], dtype=float),
            xu=np.array([1.0, 5.0], dtype=float),
        )

    def _evaluate(self, X, out, *args, **kwargs):
        x1 = X[:, 0]
        x2 = X[:, 1]

        f1 = x1
        f2 = (1.0 + x2) / x1

        g1 = 6.0 - 9.0 * x1 - x2
        g2 = x2 - 9.0 * x1 - 1.0

        out["F"] = np.column_stack([f1, f2])
        out["G"] = np.column_stack([g1, g2])
