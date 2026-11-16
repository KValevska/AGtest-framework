"""Local constrained, large-scale and multimodal benchmark functions.

Provenance: AGtest-framework standalone implementations; not imported from pymoo.
Basis publications: K. Deb et al., "Scalable Multi-Objective Optimization Test
Problems," CEC 2002 (DTLZ); H. Jain and K. Deb, IEEE TEVC 2014 (constrained
DTLZ); Z. Fan et al., "Difficulty Adjustable and Scalable Constrained
Multiobjective Test Problem Toolkit," Evolutionary Computation 2020 (DAS-CMOP).
MMF1 is a local coordinate/scaling variant of the benchmark suite introduced by
Y. Liu, G. G. Yen and D. Gong, IEEE TEVC 23(4), 2019,
DOI: 10.1109/TEVC.2018.2879406.
"""

from __future__ import annotations

import math
import numpy as np
from pymoo.core.problem import Problem


def simplex_lattice(n_obj: int, partitions: int = 40) -> np.ndarray:
    rows: list[list[int]] = []
    def visit(prefix: list[int], left: int, dims: int) -> None:
        if dims == 1:
            rows.append(prefix + [left])
        else:
            for value in range(left + 1):
                visit(prefix + [value], left - value, dims - 1)
    visit([], int(partitions), int(n_obj))
    return np.asarray(rows, dtype=float) / partitions


class LocalDTLZProblem(Problem):
    """Local DTLZ1/2/3/4 implementation, also used for large-scale profiles."""

    variable_type = "real"

    def __init__(self, variant: int, n_var: int = 12, n_obj: int = 3, alpha: float = 100.0):
        if variant not in {1, 2, 3, 4}:
            raise ValueError("Local DTLZ variant must be 1, 2, 3 or 4")
        if n_var < n_obj:
            raise ValueError("DTLZ requires n_var >= n_obj")
        self.variant, self.alpha = int(variant), float(alpha)
        self.is_large_scale = int(n_var) >= 100
        super().__init__(n_var=int(n_var), n_obj=int(n_obj), xl=0.0, xu=1.0)

    def distance(self, X: np.ndarray) -> np.ndarray:
        tail = X[:, self.n_obj - 1:]
        if self.variant in {1, 3}:
            return 100 * (tail.shape[1] + np.sum((tail - 0.5) ** 2 - np.cos(20 * np.pi * (tail - 0.5)), axis=1))
        return np.sum((tail - 0.5) ** 2, axis=1)

    def _evaluate(self, X, out, *args, **kwargs):
        X = np.asarray(X, dtype=float)
        g = self.distance(X)
        if self.variant == 1:
            F = 0.5 * (1 + g[:, None]) * np.ones((len(X), self.n_obj))
            F[:, :-1] *= np.fliplr(np.cumprod(X[:, :self.n_obj - 1], axis=1))
            F[:, 1:] *= 1 - X[:, self.n_obj - 2::-1]
        else:
            alpha = self.alpha if self.variant == 4 else 1.0
            angles = X[:, :self.n_obj - 1] ** alpha * np.pi / 2
            F = (1 + g[:, None]) * np.ones((len(X), self.n_obj))
            F[:, :-1] *= np.fliplr(np.cumprod(np.cos(angles), axis=1))
            F[:, 1:] *= np.sin(angles[:, self.n_obj - 2::-1])
        out["F"] = F

    def _calc_pareto_front(self, partitions: int = 40):
        W = simplex_lattice(self.n_obj, partitions)
        if self.variant == 1:
            return W * 0.5
        return W / np.maximum(np.linalg.norm(W, axis=1, keepdims=True), 1e-15)


class ConstrainedDTLZProblem(LocalDTLZProblem):
    """Local C1/C2/C3 and DC1/DC2/DC3 DTLZ definitions."""

    def __init__(self, kind: str, base: int, n_var: int = 12, n_obj: int = 3):
        kind = str(kind).lower()
        counts = {"c1": 1, "c2": 1, "c3": int(n_obj), "dc1": 1, "dc2": 2, "dc3": int(n_obj)}
        if kind not in counts:
            raise ValueError(f"Unknown constrained DTLZ kind: {kind}")
        self.constraint_kind = kind
        super().__init__(base, n_var=n_var, n_obj=n_obj)
        self.n_ieq_constr = counts[kind]

    def _evaluate(self, X, out, *args, **kwargs):
        super()._evaluate(X, out)
        F = out["F"]
        kind = self.constraint_kind
        if kind == "c1":
            if self.variant == 1:
                G = -(1 - F[:, -1] / 0.6 - np.sum(F[:, :-1] / 0.5, axis=1))
            else:
                radius = np.sum(F**2, axis=1)
                r = 9.0 if self.n_obj <= 3 else 12.5
                G = -(radius - 16) * (radius - r**2)
            out["G"] = G[:, None]
        elif kind == "c2":
            r = 0.2 if self.n_obj == 2 else 0.4 if self.n_obj == 3 else 0.5
            v1 = np.min(np.column_stack([(F[:, i] - 1)**2 + np.sum(F**2, axis=1) - F[:, i]**2 - r**2 for i in range(self.n_obj)]), axis=1)
            v2 = np.sum((F - 1 / np.sqrt(self.n_obj))**2, axis=1) - r**2
            out["G"] = np.minimum(v1, v2)[:, None]
        elif kind == "c3":
            if self.variant == 1:
                out["G"] = np.column_stack([1 - F[:, i] / 0.5 - (np.sum(F, axis=1) - F[:, i]) for i in range(self.n_obj)])
            else:
                out["G"] = np.column_stack([1 - F[:, i]**2 / 4 - (np.sum(F**2, axis=1) - F[:, i]**2) for i in range(self.n_obj)])
        elif kind == "dc1":
            out["G"] = (0.95 - np.cos(5 * np.pi * np.asarray(X)[:, 0]))[:, None]
        else:
            g = self.distance(np.asarray(X, dtype=float))
            if kind == "dc2":
                out["G"] = np.column_stack((0.9 - np.cos(3 * np.pi * g / 100), 0.9 - np.exp(-g / 100)))
            else:
                head = np.asarray(X)[:, :self.n_obj - 1]
                out["G"] = np.column_stack((0.5 - np.cos(5 * np.pi * g), 0.5 - np.cos(5 * np.pi * head)))

    def _calc_pareto_front(self, n_points: int = 12000):
        """Deterministic feasible sampling of the analytical g=0 manifold."""
        rng = np.random.default_rng(240519)
        X = rng.random((int(n_points), self.n_var))
        X[:, self.n_obj - 1:] = 0.5
        # Boundary points are important for C3-DTLZ regions.
        boundary = np.full((2 * (self.n_obj - 1) + 2, self.n_var), 0.5)
        for j in range(self.n_obj - 1):
            boundary[2 * j, j] = 0.0
            boundary[2 * j + 1, j] = 1.0
        X = np.vstack((X, boundary))
        out: dict[str, np.ndarray] = {}
        self._evaluate(X, out)
        feasible = np.all(np.asarray(out["G"]) <= 1e-10, axis=1)
        return np.asarray(out["F"])[feasible]


class DASCMOPProblem(Problem):
    """Local DAS-CMOP1--9 definition with the standard 16 difficulty settings."""

    variable_type = "real"
    DIFFICULTIES = ((.25,0,0),(0,.25,0),(0,0,.25),(.25,.25,.25),(.5,0,0),(0,.5,0),(0,0,.5),(.5,.5,.5),(.75,0,0),(0,.75,0),(0,0,.75),(.75,.75,.75),(0,1,0),(.5,1,0),(0,1,.5),(.5,1,.5))

    def __init__(self, variant: int, difficulty: int = 1):
        if variant not in range(1, 10) or difficulty not in range(1, 17):
            raise ValueError("DAS-CMOP variant=1..9 and difficulty=1..16 required")
        self.variant, self.difficulty = int(variant), int(difficulty)
        self.eta, self.zeta, self.gamma = self.DIFFICULTIES[difficulty - 1]
        super().__init__(n_var=30, n_obj=2 if variant <= 6 else 3, n_ieq_constr=11 if variant <= 6 else 7, xl=0.0, xu=1.0)

    def _distance(self, X):
        if self.variant <= 3:
            return np.sum((X[:, self.n_obj-1:] - np.sin(.5*np.pi*X[:, [0]]))**2, axis=1)
        if self.variant <= 8:
            z = X[:, self.n_obj-1:] - .5
            return self.n_var-self.n_obj+1 + np.sum(z*z-np.cos(20*np.pi*z), axis=1)
        j = np.arange(self.n_obj-1, self.n_var)+1
        return np.sum((X[:, self.n_obj-1:] - np.cos(.25*j/self.n_var*np.pi*(X[:,[0]]+X[:,[1]])))**2, axis=1)

    def _constraints2(self, X, F, g):
        b, d = 2*self.eta-1, .5 if self.zeta else 0.0
        e = d-np.log(self.zeta) if self.zeta > 0 else 1e30
        p=np.array([0,1,0,1,2,0,1,2,3]); q=np.array([1.5,.5,2.5,1.5,.5,3.5,2.5,1.5,.5]); t=-.25*np.pi
        c0=np.sin(20*np.pi*X[:,0])-b
        c1=1e-4-np.abs(e-g) if self.zeta==1 else (e-g)*(g-d)
        ell=((F[:,[0]]-p)*np.cos(t)-(F[:,[1]]-q)*np.sin(t))**2/.3+((F[:,[0]]-p)*np.sin(t)+(F[:,[1]]-q)*np.cos(t))**2/1.2-.5*self.gamma
        return -np.column_stack((c0,c1,ell))

    def _constraints3(self, X, F, g):
        b, d = 2*self.eta-1, .5 if self.zeta else 0.0
        e = d-np.log(self.zeta) if self.zeta > 0 else 1e30
        centers=np.array([[1,0,0],[0,1,0],[0,0,1],[1/np.sqrt(3)]*3])
        c0=np.sin(20*np.pi*X[:,0])-b; c1=np.cos(20*np.pi*X[:,1])-b
        c2=1e-4-np.abs(e-g) if self.zeta==1 else (e-g)*(g-d)
        spheres=np.sum((F[:,None,:]-centers[None,:,:])**2,axis=2)-(.5*self.gamma)**2
        return -np.column_stack((c0,c1,c2,spheres))

    def _evaluate(self, X, out, *args, **kwargs):
        X=np.asarray(X,float); g=self._distance(X)
        if self.variant <= 6:
            f0=X[:,0]+g
            if self.variant in {1,4}: f1=1-X[:,0]**2+g
            else: f1=1-np.sqrt(X[:,0])+(0.5*np.abs(np.sin(5*np.pi*X[:,0])) if self.variant in {3,6} else 0)+g
            F=np.column_stack((f0,f1)); G=self._constraints2(X,F,g)
        elif self.variant == 7:
            F=np.column_stack((X[:,0]*X[:,1]+g, X[:,1]*(1-X[:,0])+g, 1-X[:,1]+g)); G=self._constraints3(X,F,g)
        else:
            F=np.column_stack((np.cos(.5*np.pi*X[:,0])*np.cos(.5*np.pi*X[:,1])+g,np.cos(.5*np.pi*X[:,0])*np.sin(.5*np.pi*X[:,1])+g,np.sin(.5*np.pi*X[:,0])+g)); G=self._constraints3(X,F,g)
        out["F"],out["G"]=F,G

    def _calc_pareto_front(self, n_points: int = 4000):
        rng=np.random.default_rng(12345)
        X=rng.random((int(n_points),self.n_var)); X[:,self.n_obj-1:]=.5
        if self.variant <= 3: X[:,self.n_obj-1:]=np.sin(.5*np.pi*X[:,[0]])
        if self.variant == 9:
            j=np.arange(self.n_obj-1,self.n_var)+1; X[:,self.n_obj-1:]=np.cos(.25*j/self.n_var*np.pi*(X[:,[0]]+X[:,[1]]))
        out={}; self._evaluate(X,out); feasible=np.all(out["G"]<=1e-10,axis=1); F=out["F"][feasible]
        if not len(F): return None
        keep=np.ones(len(F),bool)
        for i in range(len(F)): keep[i]=not np.any(np.all(F<=F[i],axis=1)&np.any(F<F[i],axis=1))
        return F[keep]


class MMF1Problem(Problem):
    """MMF1: two disconnected Pareto sets mapped onto one objective front."""

    variable_type = "real"
    is_multimodal = True

    def __init__(self):
        super().__init__(n_var=2,n_obj=2,xl=[-1,-1],xu=[1,1])

    def _evaluate(self,X,out,*args,**kwargs):
        X=np.asarray(X,float); f1=np.abs(X[:,0]); target=np.sin(6*np.pi*f1+np.pi)
        out["F"]=np.column_stack((f1,1-np.sqrt(f1)+(X[:,1]-target)**2))

    def _calc_pareto_front(self,n_pareto_points:int=500):
        x=np.linspace(0,1,int(n_pareto_points)); return np.column_stack((x,1-np.sqrt(x)))

    def pareto_set(self,n_points:int=500):
        x=np.linspace(0,1,int(n_points)); y=np.sin(6*np.pi*x+np.pi)
        return np.vstack((np.column_stack((x,y)),np.column_stack((-x,y))))

