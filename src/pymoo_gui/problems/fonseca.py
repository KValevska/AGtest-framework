"""
EN:
Fonseca benchmark problem implementation for pymoo.
"""

# ------------------------------------------------------------------------------------
# File: fonseca.py
# Contents: Fonseca benchmark problem class for pymoo.
# What happens here: decision vectors are evaluated into two smooth Fonseca-Fleming objective functions.
# Role in the framework: provides a compact two-objective continuous benchmark for GUI experiments.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on the Fonseca-Fleming benchmark definition.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import math

import numpy as np
from pymoo.core.problem import Problem


class FonsecaProblem(Problem):
    """
    EN:
    Two-objective Fonseca-Fleming benchmark with configurable variable count.

    PL:
    Gladki problem testowy, czesto uzywany do sprawdzania zbieznosci i rozkladu
    rozwiazan na froncie.
    """

    def __init__(self, n_var: int = 3):
        parsed_n_var = int(n_var)
        super().__init__(
            n_var=parsed_n_var,
            n_obj=2,
            n_constr=0,
            xl=-4.0,
            xu=4.0,
        )
        self._offset = 1.0 / math.sqrt(parsed_n_var)

    def _evaluate(self, X, out, *args, **kwargs):
        shifted_minus = X - self._offset
        shifted_plus = X + self._offset

        f1 = 1.0 - np.exp(-np.sum(shifted_minus**2, axis=1))
        f2 = 1.0 - np.exp(-np.sum(shifted_plus**2, axis=1))

        out["F"] = np.column_stack([f1, f2])
