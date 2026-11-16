# Standalone MaO-TSP+ implementation.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
# ------------------------------------------------------------------------------------
# Article: Z. Zhang, Y. Wang, G. Sun, and J. Luo, "Two-Stage Probabilistic
#          Penalty for Expensive Constrained Multiobjective Optimization Problems,"
#          IEEE Transactions on Evolutionary Computation, 2026.
# DOI: 10.1109/TEVC.2026.3703985
# Implementation: own Python/NumPy/SciPy implementation of three penalty phases,
#                 objective/constraint Kriging and angular many-objective infill.
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
    dominance,
    evaluation_budget,
    ga,
    graph_sort,
    normalize,
    probability_leq,
    survival,
)


def _distribution_density(
    decisions: np.ndarray,
    center: np.ndarray,
    covariance: np.ndarray,
) -> np.ndarray:
    # Compute the phase-3 feasible decision-distribution density.
    covariance = np.atleast_2d(covariance)
    ridge = max(float(np.trace(covariance)) / max(1, len(center)), 1.0) * 1e-10
    precision = np.linalg.pinv(covariance + ridge * np.eye(len(center)))
    delta = np.asarray(decisions) - center
    log_density = -0.5 * np.einsum("ij,jk,ik->i", delta, precision, delta)
    return np.exp(np.maximum(log_density - np.max(log_density), -700.0))


def tsp_penalty_sort(
    decisions: np.ndarray,
    objectives: np.ndarray,
    objective_variance: np.ndarray,
    constraints: np.ndarray,
    constraint_variance: np.ndarray,
    phase: int,
    center: np.ndarray | None = None,
    covariance: np.ndarray | None = None,
) -> np.ndarray:
    # Apply PoB/PoF penalty dominance for the active article phase.
    probability_better = probability_leq(
        objectives[:, None] - objectives[None, :],
        objective_variance[:, None] + objective_variance[None, :],
    )
    if constraints.shape[1]:
        probability_feasible = probability_leq(constraints, constraint_variance).min(axis=1)
    else:
        probability_feasible = np.ones(len(objectives))

    left_feasible = probability_feasible[:, None, None]
    right_feasible = probability_feasible[None, :, None]
    if phase == 1:
        weight = np.abs(2.0 * probability_better - 1.0).mean(axis=2, keepdims=True) / 2.0
        left = weight * probability_better + (1.0 - weight) * left_feasible
        right = weight * (1.0 - probability_better) + (1.0 - weight) * right_feasible
    else:
        left = np.where(
            left_feasible < 0.5,
            left_feasible,
            probability_better + 1.0,
        )
        right = np.where(
            right_feasible < 0.5,
            right_feasible,
            2.0 - probability_better,
        )
        if phase == 3:
            if center is None or covariance is None:
                raise ValueError("Phase 3 requires a feasible decision distribution.")
            density = _distribution_density(decisions, center, covariance)
            left *= density[:, None, None]
            right *= density[None, :, None]

    relation = np.all(left >= right, axis=2) & np.any(left > right, axis=2)
    np.fill_diagonal(relation, False)
    return graph_sort(relation)


def _reference_set(problem: SurrogateProblem, population_size: int) -> np.ndarray:
    # Construct the feasible-first exact reference set used during infill.
    fronts = graph_sort(dominance(problem.F, problem.G))
    feasible = np.all(problem.G <= 0.0, axis=1)
    if np.sum(feasible) >= population_size:
        return problem.F[fronts == 1]
    cutoff = np.sort(fronts)[min(population_size, len(fronts)) - 1]
    return problem.F[fronts <= cutoff]


def run_maotspp(
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
    # Execute the many-objective TSP+ optimization framework.
    rng = np.random.default_rng(seed)
    budget = evaluation_budget(population_size, maximum_generations, infill_batch_size)
    problem = SurrogateProblem(function, lower, upper, budget)
    problem.initial(population_size, rng)
    if problem.G.shape[1] == 0:
        raise ValueError("MaO-TSP+ requires at least one inequality constraint.")
    models = Models()
    phase = 1
    old_mean_violation = np.inf
    phase_one_warning = False
    center: np.ndarray | None = None
    covariance: np.ndarray | None = None
    generation = 0
    horizon = maximum_generations or 20
    phase_budget = population_size + horizon * infill_batch_size

    while maximum_generations is None or generation < maximum_generations:
        models.fit(problem.X, problem.F, problem.G)
        active = survival(
            graph_sort(dominance(problem.F, problem.G)),
            normalize(problem.F),
            population_size,
            "angle",
        )
        population_X = problem.X[active].copy()

        for _ in range(surrogate_generations):
            population_X = np.vstack((population_X, ga(population_X, lower, upper, rng)))
            predicted_F, variance_F, predicted_G, variance_G = models.predict(population_X)
            fronts = tsp_penalty_sort(
                population_X,
                predicted_F,
                variance_F,
                predicted_G,
                variance_G,
                phase,
                center,
                covariance,
            )
            keep = survival(fronts, normalize(predicted_F), population_size, "angle")
            population_X, predicted_F, variance_F, predicted_G, variance_G = (
                values[keep]
                for values in (population_X, predicted_F, variance_F, predicted_G, variance_G)
            )

        novel = np.flatnonzero(cdist(population_X, problem.X).min(axis=1) > 1e-20)
        if novel.size == 0:
            return problem.result("no_novel_candidates")
        count = min(infill_batch_size, novel.size)
        before = problem.n_eval
        joined = np.vstack((problem.F, predicted_F[novel]))
        zmin = np.min(joined, axis=0)
        scale = np.maximum(np.ptp(joined, axis=0), 1e-10)
        normalized_F = (predicted_F[novel] - zmin) / scale
        fronts = tsp_penalty_sort(
            population_X[novel],
            normalized_F,
            variance_F[novel] / scale**2,
            predicted_G[novel],
            variance_G[novel],
            phase,
            center,
            covariance,
        )
        cutoff = np.sort(fronts)[count - 1]
        selected = list(np.flatnonzero(fronts < cutoff))
        tail = list(np.flatnonzero(fronts == cutoff))
        reference = (_reference_set(problem, population_size) - zmin) / scale

        if selected:
            problem.evaluate(population_X[novel[selected]])
            reference = np.vstack((reference, (problem.F[before:] - zmin) / scale))
        while len(selected) < count and tail:
            local_distance = angles(normalized_F[tail], reference).min(axis=1)
            local = int(np.argmax(local_distance))
            candidate = tail.pop(local)
            selected.append(candidate)
            problem.evaluate(population_X[novel[candidate] : novel[candidate] + 1])
            reference = np.unique(
                np.vstack((reference, (problem.F[-1:] - zmin) / scale)), axis=0
            )

        # Apply the two transition conditions and the final distribution-learning phase.
        if problem.n_eval > before:
            if phase == 1:
                halfway = population_size + (phase_budget - population_size) / 2.0
                quarter = population_size + (phase_budget - population_size) / 4.0
                if problem.n_eval >= halfway:
                    phase = 2
                elif problem.n_eval >= quarter:
                    new_G = problem.G[before:]
                    mean_violation = float(np.maximum(new_G, 0.0).sum(axis=1).mean())
                    warning = mean_violation > old_mean_violation and not np.any(
                        np.all(new_G <= 0.0, axis=1)
                    )
                    if warning and phase_one_warning:
                        phase = 2
                    phase_one_warning = warning
                    old_mean_violation = mean_violation
            elif phase == 2:
                three_quarters = population_size + 0.75 * (phase_budget - population_size)
                feasible = np.all(problem.G <= 0.0, axis=1)
                if problem.n_eval >= three_quarters and np.sum(feasible) >= population_size:
                    phase = 3
            if phase == 3:
                feasible_X = problem.X[np.all(problem.G <= 0.0, axis=1)]
                center = np.mean(feasible_X, axis=0)
                covariance = np.atleast_2d(np.cov(feasible_X, rowvar=False))

        generation += 1
        generation_hook(problem)
    return problem.result()


class MaOTSPP(SurrogateAlgorithm):
    """Many-objective TSP+ for expensive constrained optimization."""

    def __init__(
        self,
        population_size: int = 40,
        surrogate_generations: int = 20,
        infill_batch_size: int = 5,
        seed: int = 1,
    ) -> None:
        super().__init__(population_size=population_size, seed=seed)
        self.surrogate_generations = parse_positive_int(
            surrogate_generations, "surrogate_generations"
        )
        self.infill_batch_size = parse_positive_int(infill_batch_size, "infill_batch_size")

    def _run_surrogate(self, function, lower, upper, maximum_generations, seed, generation_hook):
        return run_maotspp(
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


def make_maotspp(
    population_size: int = 40,
    surrogate_generations: int = 20,
    infill_batch_size: int = 5,
    seed: int = 1,
) -> MaOTSPP:
    # Create the complete standalone MaO-TSP+ implementation.
    return MaOTSPP(population_size, surrogate_generations, infill_batch_size, seed)


MAOTSPP_DEFINITION: Dict[str, Any] = {
    "label": "MaO-TSP+",
    "factory": make_maotspp,
    "implementation_type": "adapted_port",
    "reference": "Z. Zhang, Y. Wang, G. Sun and J. Luo, IEEE TEVC (2026), DOI 10.1109/TEVC.2026.3703985",
    "verified_against": "PoB/PoF, three-phase transition, distribution-learning and angular-infill tests; no claim of statistical equivalence",
    "requires_constraints": True,
    "form_fields": {
        "population_size": {"default": 40, "kind": "int", "minimum": 2},
        "surrogate_generations": {"default": 20, "kind": "int", "minimum": 1},
        "infill_batch_size": {"default": 5, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Standalone MaO-TSP+ with the article's three probabilistic-penalty phases and angular infill.",
}
