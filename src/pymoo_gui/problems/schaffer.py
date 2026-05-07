"""
EN:
Schaffer single-variable benchmark problem implementation for pymoo.
"""

# ------------------------------------------------------------------------------------
# File: schaffer.py
# Contents: Schaffer benchmark problem class for pymoo.
# What happens here: one decision variable is evaluated into two quadratic objective functions.
# Role in the framework: provides a simple two-objective test problem for dissertation optimization runs.
# Author: mgr inż. Kristina Valevska
# ------------------------------------------------------------------------------------

from __future__ import annotations

import numpy as np
from pymoo.core.problem import Problem


class SchafferProblem(Problem):
    """
    EN:
    Two-objective Schaffer benchmark with one decision variable.

    PL:
    Bardzo prosty problem testowy, dobry do szybkiego sprawdzenia, czy algorytm i
    wykres Pareto dzialaja poprawnie.
    """

    def __init__(self):
        """
        EN:
        Configure the one-dimensional Schaffer search space.

        PL:
        Ustawia jedna zmienna, dwa cele i szeroki zakres od -1000 do 1000.
        """
        super().__init__(
            n_var=1,
            n_obj=2,
            n_constr=0,
            xl=-1000.0,
            xu=1000.0,
        )

    def _evaluate(self, X, out, *args, **kwargs):
        """
        EN:
        Evaluate the two quadratic Schaffer objectives for a batch of inputs.

        PL:
        Liczy dwie proste funkcje kwadratowe dla podanych wartosci zmiennej.
        """
        x = X[:, 0]
        f1 = x**2
        f2 = (x - 2.0) ** 2
        out["F"] = np.column_stack([f1, f2])
