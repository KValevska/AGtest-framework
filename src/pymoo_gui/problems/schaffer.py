# Schaffer single-variable benchmark problem implementation for pymoo.

# ------------------------------------------------------------------------------------
# Module: schaffer.py
# Summary: Schaffer benchmark problem class for pymoo.
# Implementation: one decision variable is evaluated into two quadratic objective functions.
# Responsibility: provides a simple two-objective test problem for dissertation optimization runs.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import numpy as np
from pymoo.core.problem import Problem


class SchafferProblem(Problem):
    # Two-objective Schaffer benchmark with one decision variable.

    def __init__(self):
        # Configure the one-dimensional Schaffer search space.
        super().__init__(
            n_var=1,
            n_obj=2,
            n_constr=0,
            xl=-1000.0,
            xu=1000.0,
        )

    def _evaluate(self, X, out, *args, **kwargs):
        # Evaluate the two quadratic Schaffer objectives for a batch of inputs.
        x = X[:, 0]
        f1 = x**2
        f2 = (x - 2.0) ** 2
        out["F"] = np.column_stack([f1, f2])
