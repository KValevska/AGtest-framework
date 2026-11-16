# Standalone DISK+ implementation.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
# ------------------------------------------------------------------------------------
# Article: Z. Zhang, Y. Wang, G. Sun, and T. Pang, "A Distribution Information
#          Based Kriging-Assisted Evolutionary Algorithm for Expensive
#          Many-Objective Optimization Problems," IEEE TEVC, 2025.
# DOI: 10.1109/TEVC.2024.3519185
# Implementation: own Python/NumPy/SciPy implementation of objective and constraint
#                 Kriging, CDIPD, angular infill and adaptive local exploration.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

import numpy as np
from scipy.spatial.distance import cdist

from .research_common import parse_positive_int
from .surrogate_common import (
    Models,
    SurrogateAlgorithm,
    SurrogateProblem,
    SurrogateResult,
    angles,
    differential_evolution,
    dominance,
    evaluation_budget,
    ga,
    graph_sort,
    normalize,
    simplex,
    survival,
    weighted_probability_sort,
)


def decision_distribution(
    decisions: np.ndarray,
    center: np.ndarray,
    covariance: np.ndarray,
) -> np.ndarray:
    # Evaluate stable relative Gaussian densities learned from first-front decisions.
    covariance = np.atleast_2d(covariance)
    ridge = max(float(np.trace(covariance)) / max(1, len(center)), 1.0) * 1e-10
    precision = np.linalg.pinv(covariance + ridge * np.eye(len(center)))
    delta = np.asarray(decisions) - center
    log_density = -0.5 * np.einsum("ij,jk,ik->i", delta, precision, delta)
    return np.exp(np.maximum(log_density - np.max(log_density), -700.0))


def cdipd_sort(
    decisions: np.ndarray,
    objectives: np.ndarray,
    objective_variance: np.ndarray,
    constraints: np.ndarray,
    center: np.ndarray,
    covariance: np.ndarray,
) -> np.ndarray:
    # Perform constrained distribution-informed probabilistic dominance sorting.
    weights = decision_distribution(decisions, center, covariance)
    return weighted_probability_sort(
        objectives,
        objective_variance,
        weights,
        constraints,
    )


def _reference_mask(objectives: np.ndarray, constraints: np.ndarray, count: int) -> np.ndarray:
    # Build the feasible-first reference set used by article candidate selection.
    fronts = graph_sort(dominance(objectives, constraints))
    feasible = np.all(constraints <= 0.0, axis=1) if constraints.shape[1] else np.ones(len(fronts), bool)
    if np.sum(feasible) >= count:
        return fronts == 1
    cutoff = np.sort(fronts)[min(count, len(fronts)) - 1]
    return fronts <= cutoff


def run_diskplus(
    function: Callable[[np.ndarray], Any],
    lower: np.ndarray,
    upper: np.ndarray,
    population_size: int,
    maximum_generations: Optional[int],
    surrogate_generations: int,
    infill_batch_size: int,
    seed: int,
    generation_hook: Callable[[SurrogateProblem], None],
) -> SurrogateResult:
    # Execute the full constrained DISK+ loop.
    rng = np.random.default_rng(seed)
    budget = evaluation_budget(population_size, maximum_generations, infill_batch_size + 1)
    problem = SurrogateProblem(function, lower, upper, budget)
    problem.initial(population_size, rng)
    if problem.G.shape[1] == 0:
        raise ValueError("DISK+ requires at least one inequality constraint.")
    models = Models()
    active = np.arange(population_size)
    generation = 0

    while maximum_generations is None or generation < maximum_generations:
        before = problem.n_eval
        models.fit(problem.X, problem.F, problem.G, constant_constraints=True)
        exact_fronts = graph_sort(dominance(problem.F, problem.G))
        elite = problem.X[exact_fronts == 1]
        if elite.shape[0] <= 1:
            elite = problem.X[exact_fronts <= 2]
        center = np.mean(elite, axis=0)
        covariance = np.atleast_2d(np.cov(elite, rowvar=False))

        population_X = problem.X[active].copy()
        for _ in range(surrogate_generations):
            population_X = np.vstack((population_X, ga(population_X, lower, upper, rng)))
            predicted_F, variance_F, predicted_G, variance_G = models.predict(population_X)
            fronts = cdipd_sort(
                population_X, predicted_F, variance_F, predicted_G, center, covariance
            )
            keep = survival(fronts, normalize(predicted_F), population_size, "angle")
            population_X, predicted_F, variance_F, predicted_G, variance_G = (
                values[keep]
                for values in (population_X, predicted_F, variance_F, predicted_G, variance_G)
            )

        novel = np.flatnonzero(cdist(population_X, problem.X).min(axis=1) > 1e-50)
        if novel.size:
            joined = np.vstack((problem.F, predicted_F[novel]))
            zmin = np.min(joined, axis=0)
            scale = np.maximum(np.ptp(joined, axis=0), 1e-10)
            normalized_F = (predicted_F[novel] - zmin) / scale
            fronts = cdipd_sort(
                population_X[novel],
                normalized_F,
                variance_F[novel] / scale**2,
                predicted_G[novel],
                center,
                covariance,
            )
            first = novel[fronts == 1]
            candidates = first if first.size else novel[np.argsort(fronts)]
            reference = (problem.F[_reference_mask(problem.F, problem.G, population_size)] - zmin) / scale
            selected: list[int] = []
            while candidates.size and len(selected) < infill_batch_size:
                local_F = (predicted_F[candidates] - zmin) / scale
                distance = angles(local_F, reference).min(axis=1)
                local = int(np.argmax(distance))
                chosen = int(candidates[local])
                selected.append(chosen)
                problem.evaluate(population_X[chosen : chosen + 1])
                reference = np.vstack((reference, (problem.F[-1] - zmin) / scale))
                candidates = np.delete(candidates, local)

        # Trigger exploration when the new batch does not dominate the old first front.
        if problem.n_eval > before:
            old_front = graph_sort(dominance(problem.F[:before], problem.G[:before])) == 1
            cross = dominance(problem.F, problem.G)[before:, :before]
            if not np.any(cross[:, old_front]):
                models.fit(problem.X, problem.F, problem.G, constant_constraints=True)
                current = problem.F[graph_sort(dominance(problem.F, problem.G)) == 1]
                ideal = np.min(current, axis=0) - 0.1 * np.ptp(current, axis=0) - 0.1
                vectors = simplex(10 * population_size, problem.F.shape[1])
                gap = angles(vectors, current - ideal).min(axis=1)
                direction = vectors[int(rng.choice(np.flatnonzero(gap == np.max(gap))))]
                local_X = population_X.copy()
                for _ in range(surrogate_generations):
                    local_X = np.unique(
                        np.vstack(
                            (
                                local_X,
                                ga(local_X, lower, upper, rng),
                                differential_evolution(local_X, lower, upper, rng, True),
                                differential_evolution(local_X, lower, upper, rng, False),
                            )
                        ),
                        axis=0,
                    )
                    local_F, local_var, local_G, local_G_var = models.predict(local_X)
                    uncertainty = np.sqrt(local_var).mean(axis=1) + np.sqrt(local_G_var).mean(axis=1)
                    fitness = np.max(np.abs(local_F - ideal) * direction, axis=1) - uncertainty
                    violation = np.maximum(local_G, 0.0).sum(axis=1)
                    infeasible = violation > 0.0
                    fitness[infeasible] = np.max(fitness) + violation[infeasible]
                    local_X = local_X[np.argsort(fitness, kind="stable")[:population_size]]
                if cdist(local_X[:1], problem.X).min() > 1e-50:
                    problem.evaluate(local_X[:1])

        if problem.n_eval == before:
            return problem.result("no_novel_candidates")
        active = survival(
            graph_sort(dominance(problem.F, problem.G)),
            normalize(problem.F),
            population_size,
            "angle",
        )
        generation += 1
        generation_hook(problem)
    return problem.result()


class DISKplus(SurrogateAlgorithm):
    """Constrained distribution-informed Kriging-assisted optimizer."""

    def __init__(
        self,
        population_size: int = 40,
        surrogate_generations: int = 60,
        infill_batch_size: int = 5,
        seed: int = 1,
    ) -> None:
        super().__init__(population_size=population_size, seed=seed)
        self.surrogate_generations = parse_positive_int(
            surrogate_generations, "surrogate_generations"
        )
        self.infill_batch_size = parse_positive_int(infill_batch_size, "infill_batch_size")

    def _run_surrogate(self, function, lower, upper, maximum_generations, seed, generation_hook):
        return run_diskplus(
            function,
            lower,
            upper,
            self.population_size,
            maximum_generations,
            self.surrogate_generations,
            self.infill_batch_size,
            seed,
            generation_hook,
        )


def make_diskplus(
    population_size: int = 40,
    surrogate_generations: int = 60,
    infill_batch_size: int = 5,
    seed: int = 1,
) -> DISKplus:
    # Create the complete standalone DISK+ implementation.
    return DISKplus(population_size, surrogate_generations, infill_batch_size, seed)


DISKPLUS_DEFINITION: Dict[str, Any] = {
    "label": "DISK+",
    "factory": make_diskplus,
    "implementation_type": "adapted_port",
    "reference": "Z. Zhang, Y. Wang, G. Sun and T. Pang, IEEE TEVC 29(6), 2656-2670 (2025), DOI 10.1109/TEVC.2024.3519185",
    "verified_against": "CDIPD, angular-infill, local-exploration and constrained runtime tests; no claim of statistical equivalence",
    "requires_constraints": True,
    "form_fields": {
        "population_size": {"default": 40, "kind": "int", "minimum": 2},
        "surrogate_generations": {"default": 60, "kind": "int", "minimum": 1},
        "infill_batch_size": {"default": 5, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Standalone constrained DISK+ with objective/constraint Kriging, CDIPD and adaptive exploration.",
}
