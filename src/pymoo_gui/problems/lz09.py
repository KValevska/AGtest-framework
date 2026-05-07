"""
EN:
LZ09 benchmark family implementation for pymoo.
"""

# ------------------------------------------------------------------------------------
# File: lz09.py
# Contents: LZ09 benchmark family for pymoo.
# What happens here: the Li-Zhang problem family is evaluated using the original shape and distance functions.
# Role in the framework: provides the LZ09 research benchmark family used by the GUI experiments.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on the jMetalPy source and the original LZ09 article.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import math

import numpy as np
from pymoo.core.problem import Problem


class LZ09Problem(Problem):
    """
    EN:
    Base class for the LZ09 benchmark family.

    PL:
    Wspolna implementacja rodziny LZ09 z parametrami ksztaltu i odleglosci.
    """

    def __init__(self, n_var: int, n_obj: int, ptype: int, dtype: int, ltype: int):
        super().__init__(
            n_var=int(n_var),
            n_obj=int(n_obj),
            n_constr=0,
            xl=0.0,
            xu=1.0,
        )
        self.ptype = int(ptype)
        self.dtype = int(dtype)
        self.ltype = int(ltype)

    def _ps_func2(self, x: float, t1: float, dim: int, curve_type: int, css: int) -> float:
        beta = 0.0
        dim += 1
        if curve_type == 21:
            xy = 2.0 * (x - 0.5)
            beta = xy - math.pow(t1, 0.5 * (self.n_var + 3 * dim - 8) / (self.n_var - 2))
        if curve_type == 22:
            theta = 6.0 * math.pi * t1 + dim * math.pi / self.n_var
            xy = 2.0 * (x - 0.5)
            beta = xy - math.sin(theta)
        if curve_type == 23:
            theta = 6.0 * math.pi * t1 + dim * math.pi / self.n_var
            ra = 0.8 * t1
            xy = 2.0 * (x - 0.5)
            if css == 1:
                beta = xy - ra * math.cos(theta)
            else:
                beta = xy - ra * math.sin(theta)
        if curve_type == 24:
            theta = 6.0 * math.pi * t1 + dim * math.pi / self.n_var
            xy = 2.0 * (x - 0.5)
            ra = 0.8 * t1
            if css == 1:
                beta = xy - ra * math.cos(theta / 3.0)
            else:
                beta = xy - ra * math.sin(theta)
        if curve_type == 25:
            rho = 0.8
            phi = math.pi * t1
            theta = 6.0 * math.pi * t1 + dim * math.pi / self.n_var
            xy = 2.0 * (x - 0.5)
            if css == 1:
                beta = xy - rho * math.sin(phi) * math.sin(theta)
            elif css == 2:
                beta = xy - rho * math.sin(phi) * math.cos(theta)
            else:
                beta = xy - rho * math.cos(phi)
        if curve_type == 26:
            theta = 6.0 * math.pi * t1 + dim * math.pi / self.n_var
            ra = 0.3 * t1 * (t1 * math.cos(4.0 * theta) + 2.0)
            xy = 2.0 * (x - 0.5)
            if css == 1:
                beta = xy - ra * math.cos(theta)
            else:
                beta = xy - ra * math.sin(theta)
        return beta

    def _ps_func3(self, x: float, t1: float, t2: float, dim: int, curve_type: int) -> float:
        beta = 0.0
        dim += 1
        if curve_type == 31:
            xy = 4.0 * (x - 0.5)
            rate = float(dim) / self.n_var
            beta = xy - 4.0 * (t1 * t1 * rate + t2 * (1.0 - rate)) + 2.0
        if curve_type == 32:
            theta = 2.0 * math.pi * t1 + dim * math.pi / self.n_var
            xy = 4.0 * (x - 0.5)
            beta = xy - 2.0 * t2 * math.sin(theta)
        return beta

    def _alpha_func(self, values: list[float], dim: int, pf_type: int) -> list[float]:
        alpha = [0.0] * dim
        if dim == 2:
            if pf_type == 21:
                alpha[0] = values[0]
                alpha[1] = 1.0 - math.sqrt(values[0])
            if pf_type == 22:
                alpha[0] = values[0]
                alpha[1] = 1.0 - values[0] * values[0]
            if pf_type == 23:
                alpha[0] = values[0]
                alpha[1] = 1.0 - math.sqrt(alpha[0]) - alpha[0] * math.sin(10.0 * alpha[0] * alpha[0] * math.pi)
            if pf_type == 24:
                alpha[0] = values[0]
                alpha[1] = 1.0 - values[0] - 0.05 * math.sin(4.0 * math.pi * values[0])
        else:
            if pf_type == 31:
                alpha[0] = math.cos(values[0] * math.pi / 2.0) * math.cos(values[1] * math.pi / 2.0)
                alpha[1] = math.cos(values[0] * math.pi / 2.0) * math.sin(values[1] * math.pi / 2.0)
                alpha[2] = math.sin(values[0] * math.pi / 2.0)
            if pf_type == 32:
                alpha[0] = 1.0 - math.cos(values[0] * math.pi / 2.0) * math.cos(values[1] * math.pi / 2.0)
                alpha[1] = 1.0 - math.cos(values[0] * math.pi / 2.0) * math.sin(values[1] * math.pi / 2.0)
                alpha[2] = 1.0 - math.sin(values[0] * math.pi / 2.0)
            if pf_type == 33:
                alpha[0] = values[0]
                alpha[1] = values[1]
                alpha[2] = 3.0 - (math.sin(3.0 * math.pi * values[0]) + math.sin(3.0 * math.pi * values[1]) - 2.0 * (values[0] + values[1]))
            if pf_type == 34:
                alpha[0] = values[0] - values[1]
                alpha[1] = values[0] * (1.0 - values[1])
                alpha[2] = 1.0 - values[0]
        return alpha

    def _beta_func(self, values: list[float], distance_type: int) -> float:
        beta = 0.0
        dim = len(values)
        if dim == 0:
            return 0.0
        if distance_type == 1:
            beta = 2.0 * sum(value * value for value in values) / dim
        if distance_type == 2:
            beta = 2.0 * sum(math.sqrt(i + 1) * value * value for i, value in enumerate(values)) / dim
        if distance_type == 3:
            total = 0.0
            for value in values:
                xx = 2.0 * value
                total += xx * xx - math.cos(4.0 * math.pi * xx) + 1.0
            beta = 2.0 * total / dim
        if distance_type == 4:
            total = 0.0
            prod = 1.0
            for i, value in enumerate(values):
                xx = 2.0 * value
                total += xx * xx
                prod *= math.cos(10.0 * math.pi * xx / math.sqrt(i + 1))
            beta = 2.0 * (total - 2.0 * prod + 2.0) / dim
        return beta

    def objective(self, values: list[float]) -> list[float]:
        aa: list[float] = []
        bb: list[float] = []
        cc: list[float] = []
        objectives = [0.0] * self.n_obj

        if self.n_obj == 2:
            if self.ltype in [21, 22, 23, 24, 26]:
                for n in range(1, self.n_var):
                    if n % 2 == 0:
                        aa.append(self._ps_func2(values[n], values[0], n, self.ltype, 1))
                    else:
                        bb.append(self._ps_func2(values[n], values[0], n, self.ltype, 2))
                g = self._beta_func(aa, self.dtype)
                h = self._beta_func(bb, self.dtype)
                alpha = self._alpha_func(values, 2, self.ptype)
                objectives[0] = alpha[0] + h
                objectives[1] = alpha[1] + g
            if self.ltype == 25:
                for n in range(1, self.n_var):
                    if n % 3 == 0:
                        aa.append(self._ps_func2(values[n], values[0], n, self.ltype, 1))
                    elif n % 3 == 1:
                        bb.append(self._ps_func2(values[n], values[n], n, self.ltype, 2))
                    else:
                        item = self._ps_func2(values[n], values[0], n, self.ltype, 3)
                        if n % 2 == 0:
                            aa.append(item)
                        else:
                            bb.append(item)
                g = self._beta_func(aa, self.dtype)
                h = self._beta_func(bb, self.dtype)
                alpha = self._alpha_func(values, 2, self.ptype)
                objectives[0] = alpha[0] + h
                objectives[1] = alpha[1] + g

        if self.n_obj == 3 and self.ltype in [31, 32]:
            for n in range(2, self.n_var):
                value = self._ps_func3(values[n], values[0], values[1], n, self.ltype)
                if n % 3 == 0:
                    aa.append(value)
                elif n % 3 == 1:
                    bb.append(value)
                else:
                    cc.append(value)
            g = self._beta_func(aa, self.dtype)
            h = self._beta_func(bb, self.dtype)
            e = self._beta_func(cc, self.dtype)
            alpha = self._alpha_func(values, 3, self.ptype)
            objectives[0] = alpha[0] + h
            objectives[1] = alpha[1] + g
            objectives[2] = alpha[2] + e

        return objectives

    def _evaluate(self, X, out, *args, **kwargs):
        out["F"] = np.asarray([self.objective(row.tolist()) for row in np.asarray(X, dtype=float)], dtype=float)


class LZ09F1Problem(LZ09Problem):
    def __init__(self, n_var: int = 10):
        super().__init__(n_var=n_var, n_obj=2, dtype=1, ltype=21, ptype=21)


class LZ09F2Problem(LZ09Problem):
    def __init__(self, n_var: int = 30):
        super().__init__(n_var=n_var, n_obj=2, dtype=1, ltype=22, ptype=21)


class LZ09F3Problem(LZ09Problem):
    def __init__(self, n_var: int = 30):
        super().__init__(n_var=n_var, n_obj=2, dtype=1, ltype=23, ptype=21)


class LZ09F4Problem(LZ09Problem):
    def __init__(self, n_var: int = 30):
        super().__init__(n_var=n_var, n_obj=2, dtype=1, ltype=24, ptype=21)


class LZ09F5Problem(LZ09Problem):
    def __init__(self, n_var: int = 30):
        super().__init__(n_var=n_var, n_obj=2, dtype=1, ltype=26, ptype=21)


class LZ09F6Problem(LZ09Problem):
    def __init__(self, n_var: int = 10):
        super().__init__(n_var=n_var, n_obj=3, dtype=1, ltype=32, ptype=31)


class LZ09F7Problem(LZ09Problem):
    def __init__(self, n_var: int = 10):
        super().__init__(n_var=n_var, n_obj=2, dtype=3, ltype=21, ptype=21)


class LZ09F8Problem(LZ09Problem):
    def __init__(self, n_var: int = 10):
        super().__init__(n_var=n_var, n_obj=2, dtype=4, ltype=21, ptype=21)


class LZ09F9Problem(LZ09Problem):
    def __init__(self, n_var: int = 30):
        super().__init__(n_var=n_var, n_obj=2, dtype=1, ltype=22, ptype=22)
