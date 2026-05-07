"""
EN:
Viennet2 benchmark problem implementation for pymoo.
"""

# ------------------------------------------------------------------------------------
# File: viennet2.py
# Contents: Viennet2 benchmark problem class for pymoo.
# What happens here: two-dimensional decision vectors are evaluated into three objective functions.
# Role in the framework: provides a three-objective continuous benchmark for GUI experiments.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on the jMetal benchmark definition.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import numpy as np
from pymoo.core.problem import Problem


class Viennet2Problem(Problem):
    """
    EN:
    Three-objective Viennet2 benchmark.

    PL:
    Trojkryterialny problem ciagly z dwiema zmiennymi decyzyjnymi.
    """

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
