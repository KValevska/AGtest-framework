"""
EN:
Tanaka constrained benchmark problem implementation for pymoo.
"""

# ------------------------------------------------------------------------------------
# File: tanaka.py
# Contents: Tanaka benchmark problem class for pymoo.
# What happens here: decision vectors are evaluated into two identity objectives and two nonlinear constraints.
# Role in the framework: provides a classical nonlinear constrained benchmark for GUI experiments.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on benchmark definitions used in jMetal / pymoo-style frameworks.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import numpy as np
from pymoo.core.problem import Problem


class TanakaProblem(Problem):
    """
    EN:
    Two-objective constrained Tanaka benchmark.

    PL:
    Problem z silnie nieliniowym obszarem dopuszczalnym.
    """

    def __init__(self):
        super().__init__(
            n_var=2,
            n_obj=2,
            n_ieq_constr=2,
            xl=np.array([1e-4, 1e-4], dtype=float),
            xu=np.array([np.pi, np.pi], dtype=float),
        )

    def _evaluate(self, X, out, *args, **kwargs):
        x1 = X[:, 0]
        x2 = X[:, 1]

        f1 = x1
        f2 = x2

        angle = np.arctan(x1 / x2)
        g1 = 1.0 + 0.1 * np.cos(16.0 * angle) - x1**2 - x2**2
        g2 = (x1 - 0.5) ** 2 + (x2 - 0.5) ** 2 - 0.5

        out["F"] = np.column_stack([f1, f2])
        out["G"] = np.column_stack([g1, g2])
