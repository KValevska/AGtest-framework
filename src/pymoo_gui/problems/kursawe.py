"""
EN:
Kursawe benchmark problem implementation for pymoo.
"""

# ------------------------------------------------------------------------------------
# File: kursawe.py
# Contents: Kursawe benchmark problem class for pymoo.
# What happens here: decision vectors are evaluated into the two Kursawe objective functions.
# Role in the framework: provides a configurable two-objective benchmark for dissertation optimization runs.
# Author: mgr inż. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations

import numpy as np
from pymoo.core.problem import Problem


class KursaweProblem(Problem):
    """
    EN:
    Two-objective Kursawe benchmark with configurable decision-variable count.
    """

    def __init__(self, n_var: int = 3):
        """
        EN:
        Initialize Kursawe bounds and objective metadata.

        PL:
        Ustawia liczbe zmiennych, dwa cele oraz zakres wartosci od -5 do 5.
        """
        super().__init__(
            n_var=int(n_var),
            n_obj=2,
            n_constr=0,
            xl=-5.0,
            xu=5.0,
        )

    def _evaluate(self, X, out, *args, **kwargs):
        """
        EN:
        Evaluate Kursawe objectives for a batch of decision vectors.

        PL:
        Liczy dwie funkcje celu Kursawe dla wielu rozwiazan naraz.
        """
        f1 = np.sum(-10.0 * np.exp(-0.2 * np.sqrt(X[:, :-1] ** 2 + X[:, 1:] ** 2)), axis=1)
        f2 = np.sum(np.abs(X) ** 0.8 + 5.0 * np.sin(X ** 3), axis=1)
        out["F"] = np.column_stack([f1, f2])
