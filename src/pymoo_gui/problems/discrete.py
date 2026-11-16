"""Local binary and integer multi-objective benchmark definitions.

Provenance: AGtest-framework standalone implementations; not imported from pymoo.
ZDT5 basis: E. Zitzler, K. Deb and L. Thiele, "Comparison of Multiobjective
Evolutionary Algorithms: Empirical Results," Evolutionary Computation 8(2), 2000,
DOI: 10.1162/106365600568202. IntegerPortfolio and MixedDesign are explicitly
framework-defined synthetic integration benchmarks and have no claimed source paper.
"""

from __future__ import annotations

import numpy as np
from pymoo.core.problem import Problem


class ZDT5Problem(Problem):
    """Binary ZDT5 with the original 30-bit head and ten 5-bit blocks."""

    variable_type = "binary"

    def __init__(self, blocks: int = 11, block_size: int = 5, normalize: bool = True):
        if blocks < 2 or block_size < 1:
            raise ValueError("ZDT5 requires blocks >= 2 and block_size >= 1")
        self.blocks = int(blocks)
        self.block_size = int(block_size)
        self.normalize = bool(normalize)
        super().__init__(
            n_var=30 + self.block_size * (self.blocks - 1),
            n_obj=2,
            xl=0,
            xu=1,
            vtype=bool,
        )

    def _evaluate(self, X, out, *args, **kwargs):
        bits = np.asarray(X, dtype=bool)
        head = bits[:, :30].sum(axis=1)
        tails = bits[:, 30:].reshape(len(bits), self.blocks - 1, self.block_size).sum(axis=2)
        deceptive = np.where(tails < self.block_size, 2 + tails, 1)
        f1 = 1.0 + head
        f2 = deceptive.sum(axis=1) / f1
        if self.normalize:
            f1 = (f1 - 1.0) / 30.0
            lo = (self.blocks - 1) / 31.0
            hi = float(self.blocks - 1)
            f2 = (f2 - lo) / (hi - lo)
        out["F"] = np.column_stack((f1, f2))

    def _calc_pareto_front(self, n_pareto_points: int = 31):
        raw_f1 = np.arange(1.0, 32.0)
        raw_f2 = (self.blocks - 1) / raw_f1
        if not self.normalize:
            return np.column_stack((raw_f1, raw_f2))
        lo = (self.blocks - 1) / 31.0
        hi = float(self.blocks - 1)
        return np.column_stack(((raw_f1 - 1.0) / 30.0, (raw_f2 - lo) / (hi - lo)))


class IntegerPortfolioProblem(Problem):
    """Small integer allocation benchmark with cost and imbalance objectives."""

    variable_type = "integer"

    def __init__(self, n_var: int = 8, upper: int = 10, budget: int = 30):
        self.budget = int(budget)
        super().__init__(n_var=int(n_var), n_obj=2, n_ieq_constr=1, xl=0, xu=int(upper), vtype=int)

    def _evaluate(self, X, out, *args, **kwargs):
        values = np.rint(np.asarray(X)).astype(int)
        weights = np.linspace(1.0, 2.0, self.n_var)
        targets = np.linspace(2.0, 7.0, self.n_var)
        out["F"] = np.column_stack((-values @ weights, np.sum((values - targets) ** 2, axis=1)))
        out["G"] = (values.sum(axis=1) - self.budget)[:, None]


class MixedDesignProblem(Problem):
    """Controlled mixed benchmark encoded in one array with an explicit type mask."""

    variable_type = "mixed"
    variable_types = ("real", "real", "integer", "integer", "binary", "binary")

    def __init__(self):
        super().__init__(n_var=6, n_obj=2, n_ieq_constr=1, xl=[0, 0, 0, 0, 0, 0], xu=[1, 1, 5, 5, 1, 1])

    def repair(self, X: np.ndarray) -> np.ndarray:
        Y = np.asarray(X, dtype=float).copy()
        Y[:, 2:4] = np.rint(Y[:, 2:4])
        Y[:, 4:6] = Y[:, 4:6] >= 0.5
        return Y

    def _evaluate(self, X, out, *args, **kwargs):
        Y = self.repair(X)
        out["F"] = np.column_stack((Y[:, 0] + Y[:, 2] + 2 * Y[:, 4], (1 - Y[:, 1]) ** 2 + (5 - Y[:, 3]) + Y[:, 5]))
        out["G"] = (Y[:, 0] + Y[:, 1] + Y[:, 2] + Y[:, 3] - 7.0)[:, None]

