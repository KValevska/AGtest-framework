"""
EN:
Srinivas constrained benchmark problem implementation for pymoo.
"""

# ------------------------------------------------------------------------------------
# File: srinivas.py
# Contents: Srinivas benchmark problem class for pymoo.
# What happens here: decision vectors are evaluated into two objectives and two inequality constraints.
# Role in the framework: provides a constrained bi-objective benchmark for GUI experiments.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on benchmark definitions used in jMetal / pymoo-style frameworks.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import numpy as np
from pymoo.core.problem import Problem


class SrinivasProblem(Problem):
    """
    EN:
    Two-objective constrained Srinivas benchmark.

    PL:
    Klasyczny problem z dwiema zmiennymi i dwiema funkcjami celu.
    """

    def __init__(self):
        super().__init__(
            n_var=2,
            n_obj=2,
            n_ieq_constr=2,
            xl=-20.0,
            xu=20.0,
        )

    def _evaluate(self, X, out, *args, **kwargs):
        x1 = X[:, 0]
        x2 = X[:, 1]

        f1 = 2.0 + (x1 - 2.0) ** 2 + (x2 - 1.0) ** 2
        f2 = 9.0 * x1 - (x2 - 1.0) ** 2

        g1 = x1**2 + x2**2 - 225.0
        g2 = x1 - 3.0 * x2 + 10.0

        out["F"] = np.column_stack([f1, f2])
        out["G"] = np.column_stack([g1, g2])
