# Viennet2 benchmark problem implementation for pymoo.

# ------------------------------------------------------------------------------------
# Module: viennet2.py
# Summary: Viennet2 benchmark problem class for pymoo.
# Implementation: two-dimensional decision vectors are evaluated into three objective functions.
# Responsibility: provides a three-objective continuous benchmark for GUI experiments.
# Author: Kristina Valevska, MSc Eng.
# Implementation source: own implementation based on the jMetal benchmark definition.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import numpy as np
from pymoo.core.problem import Problem


class Viennet2Problem(Problem):
    # Three-objective Viennet2 benchmark.
    # Trojkryterialny problem ciagly z dwiema zmiennymi decyzyjnymi.

    def __init__(self):
        super().__init__(
            n_var=2,
            n_obj=3,
            n_constr=0,
            xl=-4.0,
            xu=4.0,
        )

    def _evaluate(self, X, out, *args, **kwargs):
        x1 = X[:, 0]
        x2 = X[:, 1]

        f1 = (x1 - 2.0) ** 2 / 2.0 + (x2 + 1.0) ** 2 / 13.0 + 3.0
        f2 = (x1 + x2 - 3.0) ** 2 / 36.0 + (-x1 + x2 + 2.0) ** 2 / 8.0 - 17.0
        f3 = (x1 + 2.0 * x2 - 1.0) ** 2 / 175.0 + (2.0 * x2 - x1) ** 2 / 17.0 - 13.0

        out["F"] = np.column_stack([f1, f2, f3])
