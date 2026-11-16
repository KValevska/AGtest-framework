# Shared numerical primitives and GUI adapter for recent surrogate algorithms.
# Provenance: AGtest-framework infrastructure using NumPy/SciPy numerical primitives;
#             algorithmic bases are the publications cited in the individual modules.
#
# ------------------------------------------------------------------------------------
# Module: surrogate_common.py
# Summary: Kriging, probabilistic dominance, variation, survival and runtime adaptation.
# Implementation: reusable numerical primitives for DISK, DISK+, PEA+, TSPP and
# MaO-TSP+ together with the project's GUI execution facade.
# Responsibility: integrates expensive research methods with callbacks and metrics.
# Author: Kristina Valevska, MSc Eng.
# Article references: the DISK, constrained probabilistic Pareto dominance,
# and two-stage probabilistic penalty articles cited in the algorithm modules.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import comb
from types import SimpleNamespace
from typing import Any, Callable, Optional

import numpy as np
from pymoo.core.result import Result
from scipy.linalg import cho_factor, cho_solve
from scipy.optimize import minimize as scipy_minimize
from scipy.special import ndtr
from scipy.spatial.distance import cdist
from scipy.stats import qmc

from .platypus_common import termination_generations
from .research_common import ArrayPopulationView, problem_bounds, select_survivors_nsga2


@dataclass
class SurrogateResult:
    # Complete archive returned by one standalone surrogate method.

    X: np.ndarray
    F: np.ndarray
    G: np.ndarray
    n_eval: int
    termination: str = "generations"


class SurrogateProblem:
    # Evaluation archive and strict budget used by the imported numerical loops.

    def __init__(
        self,
        function: Callable[[np.ndarray], Any],
        lower: np.ndarray,
        upper: np.ndarray,
        budget: int,
    ) -> None:
        self.function = function
        self.lower = np.asarray(lower, dtype=float)
        self.upper = np.asarray(upper, dtype=float)
        if (
            self.lower.ndim != 1
            or self.lower.shape != self.upper.shape
            or not np.all(np.isfinite(np.vstack((self.lower, self.upper))))
            or np.any(self.upper <= self.lower)
        ):
            raise ValueError("Expected finite vector bounds lower < upper")
        self.budget = int(budget)
        self.n_eval = 0
        self.X: Optional[np.ndarray] = None
        self.F: Optional[np.ndarray] = None
        self.G: Optional[np.ndarray] = None

    def evaluate(self, decisions: np.ndarray) -> None:
        # Evaluate only points that fit in the remaining exact-evaluation budget.
        decisions = np.atleast_2d(decisions)[: self.budget - self.n_eval]
        if len(decisions) == 0:
            return
        raw = self.function(decisions.copy())
        objectives, constraints = (
            raw if isinstance(raw, tuple) else (raw, np.empty((len(decisions), 0)))
        )
        objectives = np.asarray(objectives, dtype=float)
        constraints = np.asarray(constraints, dtype=float)
        if (
            objectives.ndim != 2
            or constraints.ndim != 2
            or len(objectives) != len(decisions)
            or len(constraints) != len(decisions)
            or not np.all(np.isfinite(objectives))
            or not np.all(np.isfinite(constraints))
        ):
            raise ValueError(
                "Evaluator must return finite (n,m) F or (F,G); feasible G <= 0"
            )
        if self.F is not None and (
            objectives.shape[1] != self.F.shape[1]
            or constraints.shape[1] != self.G.shape[1]
        ):
            raise ValueError("Evaluator changed objective or constraint count")
        self.X = decisions.copy() if self.X is None else np.vstack((self.X, decisions))
        self.F = objectives if self.F is None else np.vstack((self.F, objectives))
        self.G = constraints if self.G is None else np.vstack((self.G, constraints))
        self.n_eval += len(decisions)

    def initial(self, count: int, rng: np.random.Generator) -> None:
        # Create the even Latin-hypercube design required by the five methods.
        if count < 2 or count > self.budget or count % 2:
            raise ValueError("population_size must be even, >= 2 and within the budget")
        design = qmc.LatinHypercube(len(self.lower), seed=rng).random(count)
        self.evaluate(self.lower + design * (self.upper - self.lower))

    def result(self, reason: str = "generations") -> SurrogateResult:
        # Return the complete exact-evaluation archive.
        return SurrogateResult(self.X, self.F, self.G, self.n_eval, reason)


def graph_sort(dominates: np.ndarray) -> np.ndarray:
    # Peel minimum-indegree layers, including cyclic probabilistic relations.
    front = np.zeros(len(dominates), dtype=int)
    remaining = np.arange(len(front))
    level = 0
    while len(remaining):
        level += 1
        degree = dominates[np.ix_(remaining, remaining)].sum(axis=0)
        take = degree == degree.min()
        front[remaining[take]] = level
        remaining = remaining[~take]
    return front


def dominance(objectives: np.ndarray, constraints: Optional[np.ndarray] = None) -> np.ndarray:
    # Construct feasible-first Pareto dominance relations.
    relation = np.all(objectives[:, None] <= objectives[None, :], axis=2) & np.any(
        objectives[:, None] < objectives[None, :],
        axis=2,
    )
    if constraints is not None and constraints.shape[1]:
        violation = np.maximum(constraints, 0.0).sum(axis=1)
        relation = np.where(
            (violation[:, None] == 0.0) & (violation[None, :] == 0.0),
            relation,
            violation[:, None] < violation[None, :],
        )
    return relation


def normalize(values: np.ndarray) -> np.ndarray:
    # Normalize columns while keeping constant dimensions finite.
    lower = values.min(axis=0)
    scale = np.maximum(np.ptp(values, axis=0), 1e-9)
    return (values - lower) / scale


def angles(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    # Return pairwise angular distances with safe zero-vector handling.
    denominator = np.linalg.norm(left, axis=1)[:, None] * np.linalg.norm(
        right,
        axis=1,
    )[None, :]
    cosine = np.divide(
        left @ right.T,
        denominator,
        out=np.zeros_like(denominator),
        where=denominator > 0,
    )
    return np.arccos(np.clip(cosine, -1.0, 1.0))


def distances(left: np.ndarray, right: np.ndarray, metric: str) -> np.ndarray:
    # Dispatch Euclidean, angular or shifted objective-space distance.
    if metric == "angle":
        return angles(left, right)
    if metric == "shift":
        return np.linalg.norm(
            np.maximum(right[None, :, :] - left[:, None, :], 0.0),
            axis=2,
        )
    return cdist(left, right)


def survival(front: np.ndarray, values: np.ndarray, count: int, metric: str = "angle") -> np.ndarray:
    # Keep an exact-size diverse subset using the requested distance metric.
    last = np.sort(front)[count - 1]
    keep = list(np.flatnonzero(front < last))
    tail = list(np.flatnonzero(front == last))
    if not keep:
        pairwise = distances(values, values, metric)
        np.fill_diagonal(pairwise, np.inf)
        while len(tail) > count:
            nearest = np.sort(pairwise[np.ix_(tail, tail)], axis=1)
            drop = min(range(len(tail)), key=lambda index: tuple(nearest[index]))
            tail.pop(drop)
        return np.asarray(tail, dtype=int)
    while len(keep) < count:
        index = int(np.argmax(distances(values[tail], values[keep], metric).min(axis=1)))
        keep.append(tail.pop(index))
    return np.asarray(keep, dtype=int)


def constraint_coordinate(objectives: np.ndarray, constraints: np.ndarray) -> np.ndarray:
    # Append normalized total constraint violation to normalized objectives.
    positive = np.maximum(constraints, 0.0)
    if positive.shape[1]:
        positive = positive / np.maximum(positive.max(axis=0), 1e-9)
    violation = positive.sum(axis=1)
    violation /= max(violation.max(), 1e-9)
    return np.column_stack((normalize(objectives), violation))


def probability_leq(mean_difference: np.ndarray, variance: np.ndarray) -> np.ndarray:
    # Compute P(a < b), including the deterministic zero-variance limit.
    sigma = np.sqrt(np.maximum(variance, 0.0))
    z_value = np.divide(
        -mean_difference,
        sigma,
        out=np.zeros_like(sigma),
        where=sigma > 0,
    )
    result = ndtr(z_value)
    return np.where(
        sigma > 0,
        result,
        np.where(mean_difference < 0, 1.0, np.where(mean_difference > 0, 0.0, 0.5)),
    )


def weighted_probability_sort(
    objectives: np.ndarray,
    variance: np.ndarray,
    weight: np.ndarray,
    constraints: Optional[np.ndarray] = None,
) -> np.ndarray:
    # Rank predictions with distribution-weighted probabilistic dominance.
    probability = probability_leq(
        objectives[:, None] - objectives[None, :],
        variance[:, None] + variance[None, :],
    )
    left = probability * weight[:, None, None]
    right = (1.0 - probability) * weight[None, :, None]
    relation = np.all(left >= right, axis=2) & np.any(left > right, axis=2)
    if constraints is not None and constraints.shape[1]:
        violation = np.maximum(constraints, 0.0).sum(axis=1)
        relation = np.where(
            violation[:, None] == violation[None, :],
            relation,
            violation[:, None] < violation[None, :],
        )
    np.fill_diagonal(relation, False)
    return graph_sort(relation)


def mutate(
    decisions: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    # Apply polynomial mutation with distribution index 20.
    decisions = np.clip(decisions, lower, upper)
    span = upper - lower
    site = rng.random(decisions.shape) < 1.0 / decisions.shape[1]
    random_values = rng.random(decisions.shape)
    distance_lower = (decisions - lower) / span
    distance_upper = (upper - decisions) / span
    delta = np.where(
        random_values <= 0.5,
        (
            2.0 * random_values
            + (1.0 - 2.0 * random_values) * (1.0 - distance_lower) ** 21
        )
        ** (1.0 / 21.0)
        - 1.0,
        1.0
        - (
            2.0 * (1.0 - random_values)
            + 2.0 * (random_values - 0.5) * (1.0 - distance_upper) ** 21
        )
        ** (1.0 / 21.0),
    )
    return np.clip(decisions + site * span * delta, lower, upper)


def ga(
    decisions: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    # Generate offspring with simulated binary crossover and polynomial mutation.
    count = len(decisions)
    left, right = decisions[: count // 2], decisions[count // 2 :]
    random_values = rng.random(left.shape)
    beta = np.where(
        random_values <= 0.5,
        (2.0 * random_values) ** (1.0 / 21.0),
        (2.0 - 2.0 * random_values) ** (-1.0 / 21.0),
    )
    beta *= (-1.0) ** rng.integers(2, size=left.shape)
    beta[rng.random(left.shape) < 0.5] = 1.0
    offspring = np.vstack(
        (
            (left + right) / 2.0 + beta * (left - right) / 2.0,
            (left + right) / 2.0 - beta * (left - right) / 2.0,
        )
    )
    return mutate(offspring, lower, upper, rng)


def differential_evolution(
    decisions: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    rng: np.random.Generator,
    current: bool = False,
) -> np.ndarray:
    # Apply the randomized DE variant used by DISK local exploration.
    count, dimensions = decisions.shape
    weight = rng.choice([0.6, 0.8, 1.0], count)[:, None]
    crossover = rng.choice([0.1, 0.2, 1.0], count)[:, None]
    first, second, third = (decisions[rng.permutation(count)] for _ in range(3))
    trial = (
        decisions + weight * (first - decisions) + weight * (second - third)
        if current
        else first + weight * (second - third)
    )
    mixed = np.where(rng.random((count, dimensions)) < crossover, trial, decisions)
    return mutate(mixed, lower, upper, rng)


def simplex(count: int, objectives: int) -> np.ndarray:
    # Generate a simplex-lattice set of nonzero direction vectors.
    divisions = 1
    while comb(divisions + objectives, objectives - 1) <= count:
        divisions += 1
    rows = []
    for bars in combinations(range(divisions + objectives - 1), objectives - 1):
        cuts = (-1,) + bars + (divisions + objectives - 1,)
        rows.append(
            [
                (cuts[index + 1] - cuts[index] - 1) / divisions
                for index in range(objectives)
            ]
        )
    return np.maximum(np.asarray(rows), 1e-6)


class Kriging:
    # Universal Gaussian-correlation Kriging with GLS trend and concentrated ML.

    def __init__(self, linear: bool = True, theta: Optional[np.ndarray] = None) -> None:
        self.linear = bool(linear)
        self.theta = theta

    def basis(self, values: np.ndarray) -> np.ndarray:
        # Return constant or linear trend basis values.
        return np.column_stack((np.ones(len(values)), values)) if self.linear else np.ones((len(values), 1))

    def fit(self, decisions: np.ndarray, targets: np.ndarray) -> "Kriging":
        # Fit correlation and GLS trend parameters.
        self.xmean = decisions.mean(axis=0)
        self.xstd = decisions.std(axis=0, ddof=1)
        self.xstd[self.xstd == 0] = 1.0
        self.x = (decisions - self.xmean) / self.xstd
        self.ymean = float(targets.mean())
        self.ystd = float(targets.std(ddof=1))
        if self.ystd == 0:
            self.ystd = 1.0
        self.y = (targets - self.ymean) / self.ystd
        self.trend = self.basis(self.x)
        self.squared = (self.x[:, None] - self.x[None, :]) ** 2
        start = np.full(decisions.shape[1], 5.0) if self.theta is None else self.theta
        optimum = scipy_minimize(
            self.likelihood,
            np.log(start),
            method="L-BFGS-B",
            bounds=[(np.log(1e-5), np.log(100.0))] * decisions.shape[1],
            options={"maxiter": 100},
        )
        self.theta = np.exp(optimum.x)
        self.likelihood(optimum.x, save=True)
        return self

    def likelihood(self, logtheta: np.ndarray, save: bool = False) -> float:
        # Evaluate concentrated negative log-likelihood and optionally cache factors.
        correlation = np.exp(-self.squared @ np.exp(logtheta))
        correlation.flat[:: len(correlation) + 1] += (10 + len(correlation)) * np.finfo(float).eps
        try:
            factor = cho_factor(correlation, lower=True)
            inverse_trend = cho_solve(factor, self.trend)
            information_inverse = np.linalg.pinv(self.trend.T @ inverse_trend)
            beta = information_inverse @ (self.trend.T @ cho_solve(factor, self.y))
            residual = self.y - self.trend @ beta
            gamma = cho_solve(factor, residual)
            sigma2 = max(float(residual @ gamma / len(correlation)), 1e-30)
            value = np.log(sigma2) + 2.0 * np.log(np.diag(factor[0])).sum() / len(correlation)
            if save:
                self.factor = factor
                self.inverse_trend = inverse_trend
                self.information_inverse = information_inverse
                self.beta = beta
                self.gamma = gamma
                self.sigma2 = sigma2
            return float(value)
        except np.linalg.LinAlgError:
            return 1e30

    def predict(self, decisions: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        # Predict response means and MSE including trend-estimation uncertainty.
        normalized = (decisions - self.xmean) / self.xstd
        correlation = np.exp(-((normalized[:, None] - self.x[None, :]) ** 2) @ self.theta)
        basis = self.basis(normalized)
        mean = basis @ self.beta + correlation @ self.gamma
        residual = basis - correlation @ self.inverse_trend
        mse = self.sigma2 * (
            1.0
            - np.sum(correlation * cho_solve(self.factor, correlation.T).T, axis=1)
            + np.sum((residual @ self.information_inverse) * residual, axis=1)
        )
        return self.ymean + self.ystd * mean, self.ystd**2 * np.maximum(mse, 0.0)


class Models:
    # Collection of one independent Kriging model per objective and constraint.

    def fit(
        self,
        decisions: np.ndarray,
        objectives: np.ndarray,
        constraints: np.ndarray,
        constant_constraints: bool = False,
    ) -> "Models":
        # Fit or refit all models while reusing previous correlation lengths.
        self.objective_count = objectives.shape[1]
        old_models = getattr(self, "models", [])
        self.models: list[Kriging] = []
        for index, target in enumerate(np.column_stack((objectives, constraints)).T):
            _, unique_X = np.unique(decisions, axis=0, return_index=True)
            _, unique_y = np.unique(target, return_index=True)
            use = np.intersect1d(unique_X, unique_y)
            if len(use) < 2:
                use = np.sort(unique_X)
            model = Kriging(
                not (constant_constraints and index >= self.objective_count),
                old_models[index].theta if index < len(old_models) else None,
            )
            self.models.append(model.fit(decisions[use], target[use]))
        return self

    def predict(
        self,
        decisions: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        # Predict means and variances for objectives and constraints.
        output = [model.predict(decisions) for model in self.models]
        means = np.column_stack([value[0] for value in output])
        variances = np.column_stack([value[1] for value in output])
        split = self.objective_count
        return means[:, :split], variances[:, :split], means[:, split:], variances[:, split:]


class SurrogateAlgorithm:
    # GUI-compatible base for the five stateful imported research methods.

    implementation_source = "standalone Python implementation based on the cited articles"

    def __init__(self, population_size: int, seed: int = 1) -> None:
        self.population_size = int(population_size)
        if self.population_size < 2 or self.population_size % 2:
            raise ValueError("population_size must be an even integer of at least 2")
        self.seed = int(seed)
        self.problem: Any = None
        self.n_gen = 0
        self.evaluator = SimpleNamespace(n_eval=0)
        self.pop = ArrayPopulationView(None)
        self.state = None

    def _objective(self, decisions: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        # Evaluate pymoo objectives and preserve individual inequality/equality constraints.
        output = self.problem.evaluate(
            decisions,
            return_values_of=["F", "G", "H"],
            return_as_dictionary=True,
        )
        objectives = np.asarray(output.get("F"), dtype=float)
        if objectives.ndim == 1:
            objectives = objectives.reshape(-1, 1)
        columns = []
        inequalities = output.get("G")
        if inequalities is not None:
            inequalities = np.asarray(inequalities, dtype=float)
            columns.append(inequalities.reshape(-1, 1) if inequalities.ndim == 1 else inequalities)
        equalities = output.get("H")
        if equalities is not None:
            equalities = np.asarray(equalities, dtype=float)
            equalities = equalities.reshape(-1, 1) if equalities.ndim == 1 else equalities
            columns.append(np.abs(equalities))
        constraints = np.column_stack(columns) if columns else np.zeros((len(objectives), 0))
        return objectives, constraints

    def _sync(self, surrogate_problem: SurrogateProblem) -> None:
        # Publish a bounded feasible-first view of the complete exact archive.
        if surrogate_problem.X is None:
            return
        violation = (
            np.maximum(surrogate_problem.G, 0.0).sum(axis=1)
            if surrogate_problem.G.shape[1]
            else np.zeros(len(surrogate_problem.X))
        )
        self.state = select_survivors_nsga2(
            surrogate_problem.X,
            surrogate_problem.F,
            violation,
            min(self.population_size, len(surrogate_problem.X)),
        )
        self.pop = ArrayPopulationView(self.state)
        self.evaluator.n_eval = surrogate_problem.n_eval

    def _run_surrogate(
        self,
        function: Callable[[np.ndarray], Any],
        lower: np.ndarray,
        upper: np.ndarray,
        maximum_generations: Optional[int],
        seed: int,
        generation_hook: Callable[[SurrogateProblem], None],
    ) -> SurrogateResult:
        # Subclasses implement their imported optimization loop.
        raise NotImplementedError

    def gui_minimize(
        self,
        *,
        problem: Any,
        termination: Any,
        seed: Optional[int] = None,
        callback: Any = None,
        **kwargs: Any,
    ) -> Result:
        # Execute imported outer iterations as GUI generations.
        self.problem = problem
        lower, upper, _ = problem_bounds(problem)
        maximum = termination_generations(termination)
        actual_seed = self.seed if seed is None else int(seed)
        self.n_gen = 0
        self.evaluator.n_eval = 0

        def generation_hook(surrogate_problem: SurrogateProblem) -> None:
            self.n_gen += 1
            self._sync(surrogate_problem)
            if callback is not None:
                callback(self)

        surrogate_result = self._run_surrogate(
            self._objective,
            lower,
            upper,
            maximum,
            actual_seed,
            generation_hook,
        )
        result = Result()
        result.algorithm = self
        result.problem = problem
        result.X = None if self.state is None else self.state.X
        result.F = None if self.state is None else self.state.F
        result.CV = None if self.state is None else self.state.CV
        result.termination = surrogate_result.termination
        return result


def evaluation_budget(population_size: int, maximum_generations: Optional[int], batch: int) -> int:
    # Allocate a finite strict budget or a practical ceiling for unlimited GUI runs.
    if maximum_generations is None:
        return np.iinfo(np.int32).max
    return population_size + max(int(maximum_generations), 1) * max(int(batch), 1)
