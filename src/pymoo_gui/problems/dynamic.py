"""Local dynamic DF benchmarks with explicit, controllable time.

Provenance: AGtest-framework standalone implementation; not imported from pymoo.
Basis publication: S. Jiang et al., "A Benchmark Test Suite for Dynamic
Evolutionary Multiobjective Optimization," IEEE Transactions on Cybernetics
47(2), 2017, DOI: 10.1109/TCYB.2016.2519450.
"""

from __future__ import annotations

import numpy as np
from pymoo.core.problem import Problem


class DynamicDFProblem(Problem):
    """DF1--DF9 benchmark family; time changes every ``change_period`` generations."""

    variable_type = "real"
    is_dynamic = True

    def __init__(self, variant: int, n_var: int = 10, change_period: int = 20, severity: int = 10):
        if variant not in range(1, 10):
            raise ValueError("Local DynamicDFProblem supports variants 1..9")
        self.variant = int(variant)
        self.change_period = max(1, int(change_period))
        self.severity = max(1, int(severity))
        self.time = 0.0
        xl = np.zeros(int(n_var))
        xu = np.ones(int(n_var))
        if variant in {3, 5, 6, 8, 9}:
            xl[1:] = -1.0
            xu[1:] = 1.0 if variant != 3 else 2.0
        if variant == 4:
            xl[:] = -2.0
            xu[:] = 2.0
        if variant == 7:
            xl[0], xu[0] = 1.0, 4.0
        super().__init__(n_var=int(n_var), n_obj=2, xl=xl, xu=xu)

    def advance_time(self, generation: int) -> bool:
        new_time = np.floor(int(generation) / self.change_period) / self.severity
        changed = not np.isclose(new_time, self.time)
        self.time = float(new_time)
        return changed

    def _evaluate(self, X, out, *args, **kwargs):
        x = np.asarray(X, dtype=float)
        t = self.time
        v = np.sin(0.5 * np.pi * t)
        if self.variant == 1:
            H = 0.75 * v + 1.25
            g = 1 + np.sum((x[:, 1:] - abs(v)) ** 2, axis=1)
            F = (x[:, 0], g * (1 - (x[:, 0] / g) ** H))
        elif self.variant == 2:
            r = min(self.n_var - 1, int((self.n_var - 1) * abs(v)))
            idx = np.arange(self.n_var) != r
            g = 1 + np.sum((x[:, idx] - abs(v)) ** 2, axis=1)
            F = (x[:, r], g * (1 - np.sqrt(x[:, r] / g)))
        elif self.variant == 3:
            H = v + 1.5
            g = 1 + np.sum((x[:, 1:] - v - x[:, [0]] ** H) ** 2, axis=1)
            F = (x[:, 0], g * (1 - (x[:, 0] / g) ** H))
        elif self.variant == 4:
            a, b, H = v, 1 + abs(np.cos(0.5 * np.pi * t)), 1.5 + v
            c = max(abs(a), a + b)
            g = 1 + sum((x[:, i] - a * (x[:, 0] / c) ** 2 / (i + 1)) ** 2 for i in range(1, self.n_var))
            F = (g * abs(x[:, 0] - a) ** H, g * abs(x[:, 0] - a - b) ** H)
        elif self.variant == 5:
            w = np.floor(10 * v)
            g = 1 + np.sum((x[:, 1:] - v) ** 2, axis=1)
            ripple = 0.02 * np.sin(w * np.pi * x[:, 0])
            F = (g * (x[:, 0] + ripple), g * (1 - x[:, 0] + ripple))
        elif self.variant == 6:
            a = 0.2 + 2.8 * abs(v)
            y = x[:, 1:] - v
            g = 1 + np.sum(abs(v) * y**2 - 10 * np.cos(2 * np.pi * y) + 10, axis=1)
            F = (g * (x[:, 0] + 0.1 * np.sin(3 * np.pi * x[:, 0])) ** a, g * (1 - x[:, 0] + 0.1 * np.sin(3 * np.pi * x[:, 0])) ** a)
        elif self.variant == 7:
            a = 5 * np.cos(0.5 * np.pi * t)
            g = 1 + np.sum((x[:, 1:] - 1 / (1 + np.exp(a * (x[:, [0]] - 2.5)))) ** 2, axis=1)
            F = (g * (1 + t) / x[:, 0], g * x[:, 0] / (1 + t))
        elif self.variant == 8:
            a = 2.25 + 2 * np.cos(2 * np.pi * t)
            target = v * np.sin(4 * np.pi * x[:, [0]]) / (1 + abs(v))
            g = 1 + np.sum((x[:, 1:] - target) ** 2, axis=1)
            F = (g * (x[:, 0] + 0.1 * np.sin(3 * np.pi * x[:, 0])), g * (1 - x[:, 0] + 0.1 * np.sin(3 * np.pi * x[:, 0])) ** a)
        else:
            N = 1 + np.floor(10 * abs(v))
            g = np.ones(len(x))
            for i in range(1, self.n_var):
                g += (x[:, i] - np.cos(4 * t + x[:, 0] + x[:, i - 1])) ** 2
            ripple = np.maximum(0, (0.1 + 0.5 / N) * np.sin(2 * N * np.pi * x[:, 0]))
            F = (g * (x[:, 0] + ripple), g * (1 - x[:, 0] + ripple))
        out["F"] = np.column_stack(F)

    def _calc_pareto_front(self, n_pareto_points: int = 200):
        x = np.linspace(0, 1, int(n_pareto_points))
        v = np.sin(0.5 * np.pi * self.time)
        if self.variant == 1:
            return np.column_stack((x, 1 - x ** (0.75 * v + 1.25)))
        if self.variant == 2:
            return np.column_stack((x, 1 - np.sqrt(x)))
        if self.variant == 3:
            return np.column_stack((x, 1 - x ** (v + 1.5)))
        if self.variant == 4:
            a, b, H = v, 1 + abs(np.cos(0.5 * np.pi * self.time)), 1.5 + v
            z = np.linspace(a, a + b, int(n_pareto_points))
            return np.column_stack((abs(z - a) ** H, abs(z - a - b) ** H))
        if self.variant == 5:
            ripple = 0.02 * np.sin(np.floor(10 * v) * np.pi * x)
            return np.column_stack((x + ripple, 1 - x + ripple))
        if self.variant == 6:
            a = 0.2 + 2.8 * abs(v)
            return np.column_stack(((x + 0.1 * np.sin(3 * np.pi * x)) ** a, (1 - x + 0.1 * np.sin(3 * np.pi * x)) ** a))
        if self.variant == 7:
            z = np.linspace(1, 4, int(n_pareto_points))
            return np.column_stack(((1 + self.time) / z, z / (1 + self.time)))[::-1]
        if self.variant == 8:
            return np.column_stack((x + 0.1 * np.sin(3 * np.pi * x), (1 - x + 0.1 * np.sin(3 * np.pi * x)) ** (2.25 + 2 * np.cos(2 * np.pi * self.time))))
        N = 1 + np.floor(10 * abs(v))
        ripple = np.maximum(0, (0.1 + 0.5 / N) * np.sin(2 * N * np.pi * x))
        candidates = np.column_stack((x + ripple, 1 - x + ripple))
        keep = np.ones(len(candidates), dtype=bool)
        for i in range(len(candidates)):
            keep[i] = not np.any(np.all(candidates <= candidates[i], axis=1) & np.any(candidates < candidates[i], axis=1))
        return candidates[keep]

