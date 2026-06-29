# Kursawe benchmark problem implementation for pymoo.

# ------------------------------------------------------------------------------------
# Module: kursawe.py
# Summary: Kursawe benchmark problem class for pymoo.
# Implementation: decision vectors are evaluated into the two Kursawe objective functions.
# Responsibility: provides a configurable two-objective benchmark for dissertation optimization runs.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import numpy as np
from pymoo.core.problem import Problem


class KursaweProblem(Problem):
    # Two-objective Kursawe benchmark with configurable decision-variable count.

    def __init__(self, n_var: int = 3):
        # Initialize Kursawe bounds and objective metadata.
        super().__init__(
            n_var=int(n_var),
            n_obj=2,
            n_constr=0,
            xl=-5.0,
            xu=5.0,
        )

    def _evaluate(self, X, out, *args, **kwargs):
        # Evaluate Kursawe objectives for a batch of decision vectors.
        f1 = np.sum(-10.0 * np.exp(-0.2 * np.sqrt(X[:, :-1] ** 2 + X[:, 1:] ** 2)), axis=1)
        f2 = np.sum(np.abs(X) ** 0.8 + 5.0 * np.sin(X ** 3), axis=1)
        out["F"] = np.column_stack([f1, f2])
