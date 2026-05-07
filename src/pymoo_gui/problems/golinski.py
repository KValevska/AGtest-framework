"""
EN:
Golinski speed reducer benchmark problem implementation for pymoo.
"""

# ------------------------------------------------------------------------------------
# File: golinski.py
# Contents: Golinski benchmark problem class for pymoo.
# What happens here: decision vectors are evaluated into weight/stress objectives with eleven engineering constraints.
# Role in the framework: provides a classical constrained engineering benchmark for GUI experiments.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on benchmark definitions commonly used in the literature.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import numpy as np
from pymoo.core.problem import Problem


class GolinskiProblem(Problem):
    """
    EN:
    Two-objective constrained Golinski speed-reducer benchmark.

    PL:
    Klasyczny problem inzynierski z siedmioma zmiennymi i jedenastoma
    ograniczeniami.
    """

    def __init__(self):
        super().__init__(
            n_var=7,
            n_obj=2,
            n_ieq_constr=11,
            xl=np.array([2.6, 0.7, 17.0, 7.3, 7.3, 2.9, 5.0], dtype=float),
            xu=np.array([3.6, 0.8, 28.0, 8.3, 8.3, 3.9, 5.5], dtype=float),
        )

    def _evaluate(self, X, out, *args, **kwargs):
        x1 = X[:, 0]
        x2 = X[:, 1]
        x3 = X[:, 2]
        x4 = X[:, 3]
        x5 = X[:, 4]
        x6 = X[:, 5]
        x7 = X[:, 6]

        f1 = (
            0.7854 * x1 * x2**2 * (3.3333 * x3**2 + 14.9334 * x3 - 43.0934)
            - 1.5079 * x1 * (x6**2 + x7**2)
            + 7.477 * (x6**3 + x7**3)
            + 0.7854 * (x4 * x6**2 + x5 * x7**2)
        )
        f2 = np.sqrt((745.0 * x4 / (x2 * x3)) ** 2 + 1.69e7) / (0.1 * x6**3)

        g1 = 27.0 / (x1 * x2**2 * x3) - 1.0
        g2 = 397.5 / (x1 * x2**2 * x3**2) - 1.0
        g3 = 1.93 * x4**3 / (x2 * x3 * x6**4) - 1.0
        g4 = 1.93 * x5**3 / (x2 * x3 * x7**4) - 1.0
        g5 = np.sqrt((745.0 * x4 / (x2 * x3)) ** 2 + 1.69e7) / (110.0 * x6**3) - 1.0
        g6 = np.sqrt((745.0 * x5 / (x2 * x3)) ** 2 + 157.5e6) / (85.0 * x7**3) - 1.0
        g7 = x2 * x3 / 40.0 - 1.0
        g8 = 5.0 * x2 / x1 - 1.0
        g9 = x1 / (12.0 * x2) - 1.0
        g10 = (1.5 * x6 + 1.9) / x4 - 1.0
        g11 = (1.1 * x7 + 1.9) / x5 - 1.0

        out["F"] = np.column_stack([f1, f2])
        out["G"] = np.column_stack([g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11])
