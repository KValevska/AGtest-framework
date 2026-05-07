"""
EN:
Water resource planning benchmark problem implementation for pymoo. (5 criterion)
"""

# ------------------------------------------------------------------------------------
# File: water.py
# Contents: Water benchmark problem class for pymoo.
# What happens here: decision vectors are evaluated into five planning objectives and seven inequality constraints.
# Role in the framework: provides a classical constrained many-objective engineering benchmark for GUI experiments.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on benchmark definitions commonly used in the literature.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import numpy as np
from pymoo.core.problem import Problem


class WaterProblem(Problem):
    """
    EN:
    Five-objective constrained water resource planning benchmark.
    """

    def __init__(self):
        super().__init__(
            n_var=3,
            n_obj=5,
            n_ieq_constr=7,
            xl=np.array([0.01, 0.01, 0.01], dtype=float),
            xu=np.array([0.45, 0.10, 0.10], dtype=float),
        )

    def _evaluate(self, X, out, *args, **kwargs):
        x1 = X[:, 0]
        x2 = X[:, 1]
        x3 = X[:, 2]

        f1 = 106780.37 * (x2 + x3) + 61704.67
        f2 = 3000.0 * x1
        f3 = 305700.0 * 2289.0 * x2 / ((0.06 * 2289.0) ** 0.65)
        f4 = 250.0 * 2289.0 * np.exp(-39.75 * x2 + 9.9 * x3 + 2.74)
        f5 = 25.0 * (1.39 / (x1 * x2) + 4940.0 * x3 - 80.0)

        g1 = 1.39 / (x1 * x2) + 4.94 * x3 - 0.08 - 1.0
        g2 = 0.000306 / (x1 * x2) + 1.082 * x3 - 0.0986 - 1.0
        g3 = 12.307 / (x1 * x2) + 49408.24 * x3 + 4051.02 - 50000.0
        g4 = 2.098 / (x1 * x2) + 8046.33 * x3 - 696.71 - 16000.0
        g5 = 2.138 / (x1 * x2) + 7883.39 * x3 - 705.04 - 10000.0
        g6 = 0.417 * x1 * x2 + 1721.26 * x3 - 136.54 - 2000.0
        g7 = 0.164 / (x1 * x2) + 631.13 * x3 - 54.48 - 550.0

        out["F"] = np.column_stack([f1, f2, f3, f4, f5])
        out["G"] = np.column_stack([g1, g2, g3, g4, g5, g6, g7])
