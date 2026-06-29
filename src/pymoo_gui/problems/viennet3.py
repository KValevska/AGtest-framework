# Viennet3 benchmark problem implementation for pymoo.( 3 criterion)

# ------------------------------------------------------------------------------------
# Module: viennet3.py
# Summary: Viennet3 benchmark problem class for pymoo.
# Implementation: two-dimensional decision vectors are evaluated into three nonlinear objective functions.
# Responsibility: provides a three-objective continuous benchmark for GUI experiments.
# Author: Kristina Valevska, MSc Eng.
# Implementation source: own implementation based on classical Viennet3 benchmark definitions.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import numpy as np
from pymoo.core.problem import Problem


class Viennet3Problem(Problem):
    # Three-objective Viennet3 benchmark.

    def __init__(self):
        super().__init__(
            n_var=2,
            n_obj=3,
            n_constr=0,
            xl=-3.0,
            xu=3.0,
        )

    def _evaluate(self, X, out, *args, **kwargs):
        x1 = X[:, 0]
        x2 = X[:, 1]

        radius_sq = x1**2 + x2**2
        f1 = 0.5 * radius_sq + np.sin(radius_sq)
        f2 = (3.0 * x1 - 2.0 * x2 + 4.0) ** 2 / 8.0 + (x1 - x2 + 1.0) ** 2 / 27.0 + 15.0
        f3 = 1.0 / (radius_sq + 1.0) - 1.1 * np.exp(-radius_sq)

        out["F"] = np.column_stack([f1, f2, f3])
