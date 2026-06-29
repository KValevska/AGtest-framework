# Binh2 constrained benchmark problem implementation for pymoo.

# ------------------------------------------------------------------------------------
# Module: binh2.py
# Summary: Binh2 benchmark problem class for pymoo.
# Implementation: decision vectors are evaluated into two objective functions and two inequality constraints.
# Responsibility: provides a constrained bi-objective benchmark used by the GUI experiments.
# Author: Kristina Valevska, MSc Eng.
# Implementation source: own implementation based on benchmark definition used in jMetal / pymoo-style frameworks.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import numpy as np
from pymoo.core.problem import Problem


class Binh2Problem(Problem):
    # Two-objective constrained Binh2 benchmark.

    def __init__(self):
        super().__init__(
            n_var=2,
            n_obj=2,
            n_ieq_constr=2,
            xl=np.array([0.0, 0.0], dtype=float),
            xu=np.array([5.0, 3.0], dtype=float),
        )

    def _evaluate(self, X, out, *args, **kwargs):
        x1 = X[:, 0]
        x2 = X[:, 1]

        f1 = 4.0 * x1**2 + 4.0 * x2**2
        f2 = (x1 - 5.0) ** 2 + (x2 - 5.0) ** 2

        g1 = (x1 - 5.0) ** 2 + x2**2 - 25.0
        g2 = 7.7 - (x1 - 8.0) ** 2 - (x2 + 3.0) ** 2

        out["F"] = np.column_stack([f1, f2])
        out["G"] = np.column_stack([g1, g2])
