# Osyczka2 constrained benchmark problem implementation for pymoo.

# ------------------------------------------------------------------------------------
# Module: osyczka2.py
# Summary: Osyczka2 benchmark problem class for pymoo.
# Implementation: decision vectors are evaluated into two objectives and six inequality constraints.
# Responsibility: provides a classical constrained six-variable benchmark for GUI experiments.
# Author: Kristina Valevska, MSc Eng.
# Implementation source: own implementation based on benchmark definitions used in jMetal / pymoo-style frameworks.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import numpy as np
from pymoo.core.problem import Problem


class Osyczka2Problem(Problem):
    # Two-objective constrained Osyczka2 benchmark.
    # Problem z szescioma zmiennymi i zlozonym obszarem dopuszczalnym.

    def __init__(self):
        super().__init__(
            n_var=6,
            n_obj=2,
            n_ieq_constr=6,
            xl=np.array([0.0, 0.0, 1.0, 0.0, 1.0, 0.0], dtype=float),
            xu=np.array([10.0, 10.0, 5.0, 6.0, 5.0, 10.0], dtype=float),
        )

    def _evaluate(self, X, out, *args, **kwargs):
        x1 = X[:, 0]
        x2 = X[:, 1]
        x3 = X[:, 2]
        x4 = X[:, 3]
        x5 = X[:, 4]
        x6 = X[:, 5]

        f1 = -(25.0 * (x1 - 2.0) ** 2 + (x2 - 2.0) ** 2 + (x3 - 1.0) ** 2 + (x4 - 4.0) ** 2 + (x5 - 1.0) ** 2)
        f2 = x1**2 + x2**2 + x3**2 + x4**2 + x5**2 + x6**2

        g1 = 2.0 - x1 - x2
        g2 = x1 + x2 - 6.0
        g3 = x2 - x1 - 2.0
        g4 = x1 - 3.0 * x2 - 2.0
        g5 = (x3 - 3.0) ** 2 + x4 - 4.0
        g6 = 4.0 - (x5 - 3.0) ** 2 - x6

        out["F"] = np.column_stack([f1, f2])
        out["G"] = np.column_stack([g1, g2, g3, g4, g5, g6])
