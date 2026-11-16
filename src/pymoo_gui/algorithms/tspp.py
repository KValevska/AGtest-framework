# TSPP implementation and GUI factory definition.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
#
# ------------------------------------------------------------------------------------
# Module: tspp.py
# Summary: three-phase two-stage probabilistic penalty and Kriging-assisted infill.
# Implementation: probabilistic objective and feasibility penalties change across three
# phases; surrogate GA and diversity selection provide exact candidate batches.
# Responsibility: adds the 2026 expensive constrained TSPP method to GUI experiments.
# Author: Kristina Valevska, MSc Eng.
# Article reference: Z. Zhang, Y. Wang, G. Sun, and J. Luo, "Two-stage
# probabilistic penalty for expensive constrained multiobjective optimization
# problems," IEEE Transactions on Evolutionary Computation, 2026.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

import numpy as np
from scipy.spatial.distance import cdist

from .disk import _reference, distribution_weights
from .surrogate_common import (
    Models,
    SurrogateAlgorithm,
    SurrogateProblem,
    SurrogateResult,
    distances,
    dominance,
    evaluation_budget,
    ga,
    graph_sort,
    normalize,
    probability_leq,
    survival,
)
from .research_common import parse_positive_int


def tspp_sort(
    decisions: np.ndarray,
    objectives: np.ndarray,
    variance: np.ndarray,
    constraints: np.ndarray,
    constraint_variance: np.ndarray,
    phase: int,
    center: Optional[np.ndarray] = None,
    covariance: Optional[np.ndarray] = None,
) -> np.ndarray:
    # Rank predictions with the phase-dependent two-stage probabilistic penalty.
    probability = probability_leq(
        objectives[:, None] - objectives[None, :],
        variance[:, None] + variance[None, :],
    )
    constraint_probability = probability_leq(constraints, constraint_variance)
    feasibility = (
        constraint_probability.min(axis=1)
        if constraints.shape[1]
        else np.ones(len(objectives))
    )
    left_feasibility = feasibility[:, None, None]
    right_feasibility = feasibility[None, :, None]
    if phase == 1:
        weight = np.abs(2.0 * probability - 1.0).mean(axis=2, keepdims=True) / 2.0
        left = weight * probability + (1.0 - weight) * left_feasibility
        right = weight * (1.0 - probability) + (1.0 - weight) * right_feasibility
    else:
        left = np.where(left_feasibility < 0.5, left_feasibility, probability + 1.0)
        right = np.where(right_feasibility < 0.5, right_feasibility, 2.0 - probability)
        if phase == 3:
            density = distribution_weights(decisions, center, covariance)
            left *= density[:, None, None]
            right *= density[None, :, None]
    relation = np.all(left >= right, axis=2) & np.any(left > right, axis=2)
    np.fill_diagonal(relation, False)
    return graph_sort(relation)


def run_tspp(
    function: Callable[[np.ndarray], Any],
    lower: np.ndarray,
    upper: np.ndarray,
    population_size: int,
    maximum_generations: Optional[int],
    surrogate_generations: int,
    infill_batch_size: int,
    seed: int,
    many_objective: bool,
    generation_hook: Callable[[SurrogateProblem], None],
) -> SurrogateResult:
    # Run the shared TSPP or MaO-TSPP three-phase optimization loop.
    rng = np.random.default_rng(seed)
    actual_budget = evaluation_budget(
        population_size,
        maximum_generations,
        infill_batch_size,
    )
    phase_horizon = maximum_generations if maximum_generations is not None else 20
    phase_budget = population_size + max(int(phase_horizon), 1) * infill_batch_size
    problem = SurrogateProblem(function, lower, upper, actual_budget)
    problem.initial(population_size, rng)
    models = Models()
    phase = 1
    old_violation = np.inf
    rising = False
    center = None
    covariance = None
    metric = "angle" if many_objective else "euclidean"
    generation = 0
    while maximum_generations is None or generation < maximum_generations:
        models.fit(problem.X, problem.F, problem.G)
        active = survival(
            graph_sort(dominance(problem.F, problem.G)),
            normalize(problem.F),
            population_size,
            metric,
        )
        population_X = problem.X[active].copy()
        for _ in range(surrogate_generations):
            population_X = np.vstack(
                (population_X, ga(population_X, problem.lower, problem.upper, rng))
            )
            predicted_F, variance_F, predicted_G, variance_G = models.predict(population_X)
            predicted_front = tspp_sort(
                population_X,
                predicted_F,
                variance_F,
                predicted_G,
                variance_G,
                phase,
                center,
                covariance,
            )
            take = survival(
                predicted_front,
                normalize(predicted_F),
                population_size,
                metric,
            )
            population_X, predicted_F, variance_F, predicted_G, variance_G = (
                values[take]
                for values in (
                    population_X,
                    predicted_F,
                    variance_F,
                    predicted_G,
                    variance_G,
                )
            )

        novel = np.flatnonzero(cdist(population_X, problem.X).min(axis=1) > 1e-20)
        count = min(infill_batch_size, len(novel))
        before = problem.n_eval
        if not count:
            return problem.result("no_novel_candidates")
        if len(novel) <= count:
            problem.evaluate(population_X[novel])
        else:
            joined = np.vstack((problem.F, predicted_F[novel]))
            lower_F = joined.min(axis=0)
            scale_F = np.maximum(np.ptp(joined, axis=0), 1e-9)
            normalized_F = (predicted_F[novel] - lower_F) / scale_F
            reference = (
                problem.F[_reference(problem.F, problem.G, population_size)] - lower_F
            ) / scale_F
            candidate_front = tspp_sort(
                population_X[novel],
                normalized_F,
                variance_F[novel] / scale_F**2,
                predicted_G[novel],
                variance_G[novel],
                phase,
                center,
                covariance,
            )
            cutoff = np.sort(candidate_front)[count - 1]
            selected = list(np.flatnonzero(candidate_front < cutoff))
            tail = list(np.flatnonzero(candidate_front == cutoff))
            if selected:
                start = problem.n_eval
                problem.evaluate(population_X[novel[selected]])
                reference = np.vstack(
                    (reference, (problem.F[start:] - lower_F) / scale_F)
                )
            while len(selected) < count:
                index = int(
                    np.argmax(
                        distances(normalized_F[tail], reference, metric).min(axis=1)
                    )
                )
                candidate = tail.pop(index)
                selected.append(candidate)
                problem.evaluate(population_X[novel[candidate] : novel[candidate] + 1])
                reference = np.unique(
                    np.vstack((reference, (problem.F[-1:] - lower_F) / scale_F)),
                    axis=0,
                )

        if phase == 1:
            if problem.n_eval >= population_size + (phase_budget - population_size) / 2.0:
                phase = 2
            elif problem.n_eval >= population_size + (phase_budget - population_size) / 4.0:
                violation = np.maximum(problem.G[before:], 0.0).sum(axis=1).mean()
                increase = violation > old_violation and not np.any(
                    np.all(problem.G[before:] <= 0.0, axis=1)
                )
                if increase and rising:
                    phase = 2
                rising = increase
                old_violation = violation
        elif phase == 2:
            feasible = np.all(problem.G <= 0.0, axis=1)
            if (
                problem.n_eval
                >= population_size + (phase_budget - population_size) * 0.75
                and np.sum(feasible) >= population_size
            ):
                phase = 3
        if phase == 3:
            elite = problem.X[np.all(problem.G <= 0.0, axis=1)]
            center = elite.mean(axis=0)
            covariance = np.atleast_2d(np.cov(elite, rowvar=False))
        generation += 1
        generation_hook(problem)
    return problem.result()


class TSPP(SurrogateAlgorithm):
    # Three-phase two-stage probabilistic-penalty expensive optimizer.

    def __init__(
        self,
        population_size: int = 40,
        surrogate_generations: int = 10,
        infill_batch_size: int = 5,
        seed: int = 1,
    ) -> None:
        super().__init__(population_size=population_size, seed=seed)
        self.surrogate_generations = parse_positive_int(
            surrogate_generations,
            "surrogate_generations",
        )
        self.infill_batch_size = parse_positive_int(
            infill_batch_size,
            "infill_batch_size",
        )

    def _run_surrogate(self, function, lower, upper, maximum_generations, seed, generation_hook):
        # Execute TSPP with Euclidean candidate diversity.
        return run_tspp(
            function,
            lower,
            upper,
            self.population_size,
            maximum_generations,
            self.surrogate_generations,
            self.infill_batch_size,
            seed,
            False,
            generation_hook,
        )


def make_tspp(
    population_size: int = 40,
    surrogate_generations: int = 10,
    infill_batch_size: int = 5,
    seed: int = 1,
) -> TSPP:
    # Create a configured TSPP instance for the GUI registry.
    return TSPP(population_size, surrogate_generations, infill_batch_size, seed)


TSPP_DEFINITION: Dict[str, Any] = {
    "label": "TSPP",
    "factory": make_tspp,
    "requires_constraints": True,
    "implementation_type": "adapted_port",
    "reference": "Z. Zhang et al., Two-stage probabilistic penalty, IEEE TEVC (2026)",
    "verified_against": "phase-transition tests, deterministic constrained runs and GUI/Multi integration; no claim of statistical equivalence",
    "form_fields": {
        "population_size": {"default": 40, "kind": "int", "minimum": 2},
        "surrogate_generations": {"default": 10, "kind": "int", "minimum": 1},
        "infill_batch_size": {"default": 5, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": (
        "Three-phase two-stage probabilistic penalty TSPP (2026) for expensive "
        "constrained multiobjective problems. Population size must be even."
    ),
}
