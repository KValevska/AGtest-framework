# DISK implementation and GUI factory definition.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
#
# ------------------------------------------------------------------------------------
# Module: disk.py
# Summary: distribution-informed Kriging, DIPD, angular selection and local exploration.
# Implementation: elite decision distributions weight probabilistic dominance while
# Kriging-assisted GA and adaptive direction-gap exploration choose expensive infills.
# Responsibility: adds the 2025 expensive many-objective DISK method to GUI experiments.
# Author: Kristina Valevska, MSc Eng.
# Article reference: Z. Zhang, Y. Wang, G. Sun, and T. Pang, "A distribution
# information based Kriging-assisted evolutionary algorithm for expensive
# many-objective optimization problems," IEEE TEVC, 2025, 29(6): 2656-2670.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

import numpy as np
from scipy.spatial.distance import cdist

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
from .research_common import parse_positive_int


def distribution_weights(
    decisions: np.ndarray,
    mean: np.ndarray,
    covariance: np.ndarray,
) -> np.ndarray:
    # Compute stable relative Gaussian densities in decision space.
    delta = decisions - mean
    ridge = max(float(np.trace(covariance)) / len(mean), 1.0) * 1e-10
    precision = np.linalg.inv(covariance + ridge * np.eye(len(mean)))
    log_probability = -0.5 * np.einsum("ij,jk,ik->i", delta, precision, delta)
    return np.exp(np.maximum(log_probability - log_probability.max(), -700.0))


def _reference(
    objectives: np.ndarray,
    constraints: np.ndarray,
    count: int,
) -> np.ndarray:
    # Select the feasible-first reference layers used by constrained variants.
    fronts = graph_sort(dominance(objectives, constraints))
    enough_feasible = np.sum(np.all(constraints <= 0.0, axis=1)) >= count
    cutoff = 1 if enough_feasible else np.sort(fronts)[min(count, len(fronts)) - 1]
    return fronts <= cutoff


def run_disk(
    function: Callable[[np.ndarray], Any],
    lower: np.ndarray,
    upper: np.ndarray,
    population_size: int,
    maximum_generations: Optional[int],
    surrogate_generations: int,
    infill_batch_size: int,
    seed: int,
    constrained: bool,
    generation_hook: Callable[[SurrogateProblem], None],
) -> SurrogateResult:
    # Run the shared DISK or DISKplus outer optimization loop.
    rng = np.random.default_rng(seed)
    budget = evaluation_budget(
        population_size,
        maximum_generations,
        infill_batch_size + 1,
    )
    problem = SurrogateProblem(function, lower, upper, budget)
    problem.initial(population_size, rng)
    if not constrained and problem.G.shape[1]:
        raise ValueError("DISK is unconstrained; use DISKplus for constrained problems")
    active = np.arange(population_size)
    models = Models()
    generation = 0
    while maximum_generations is None or generation < maximum_generations:
        before = problem.n_eval
        decisions, objectives, constraints = problem.X, problem.F, problem.G
        models.fit(decisions, objectives, constraints, constant_constraints=constrained)
        fronts = graph_sort(dominance(objectives, constraints if constrained else None))
        elite = decisions[fronts == 1]
        if len(elite) <= 1:
            elite = decisions[fronts <= 2]
        center = elite.mean(axis=0)
        covariance = np.atleast_2d(np.cov(elite, rowvar=False))
        population_X = decisions[active].copy()
        for _ in range(surrogate_generations):
            population_X = np.vstack(
                (population_X, ga(population_X, problem.lower, problem.upper, rng))
            )
            predicted_F, variance_F, predicted_G, variance_G = models.predict(population_X)
            weight = distribution_weights(population_X, center, covariance)
            predicted_front = weighted_probability_sort(
                predicted_F,
                variance_F,
                weight,
                predicted_G if constrained else None,
            )
            take = survival(
                predicted_front,
                normalize(predicted_F),
                population_size,
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

        novel = np.flatnonzero(cdist(population_X, problem.X).min(axis=1) > 1e-50)
        if len(novel) > infill_batch_size:
            reference_mask = (
                _reference(problem.F, problem.G, population_size)
                if constrained
                else graph_sort(dominance(problem.F)) == 1
            )
            reference_F = problem.F[reference_mask]
            joined = np.vstack((reference_F, predicted_F[novel]))
            lower_F = joined.min(axis=0)
            scale_F = np.maximum(np.ptp(joined, axis=0), 1e-9)
            normalized_F = (predicted_F[novel] - lower_F) / scale_F
            candidate_front = weighted_probability_sort(
                normalized_F,
                variance_F[novel] / scale_F**2,
                distribution_weights(population_X[novel], center, covariance),
                predicted_G[novel] if constrained else None,
            )
            novel = novel[candidate_front == 1]
            if len(novel) > infill_batch_size:
                selected = []
                for _ in range(infill_batch_size):
                    reference = (
                        problem.F[_reference(problem.F, problem.G, population_size)]
                        if constrained
                        else problem.F[graph_sort(dominance(problem.F)) == 1]
                    )
                    index = int(
                        np.argmax(
                            angles(
                                (predicted_F[novel] - lower_F) / scale_F,
                                (reference - lower_F) / scale_F,
                            ).min(axis=1)
                        )
                    )
                    candidate = novel[index]
                    selected.append(candidate)
                    problem.evaluate(population_X[candidate : candidate + 1])
                    novel = np.delete(novel, index)
                novel = np.empty(0, dtype=int)
        problem.evaluate(population_X[novel[:infill_batch_size]])

        if problem.n_eval > before:
            cross = dominance(
                problem.F,
                problem.G if constrained else None,
            )[before:, :before]
            old_front = graph_sort(
                dominance(objectives, constraints if constrained else None)
            ) == 1
            if not cross[:, old_front].any():
                models.fit(
                    problem.X,
                    problem.F,
                    problem.G,
                    constant_constraints=constrained,
                )
                current = problem.F[
                    graph_sort(
                        dominance(problem.F, problem.G if constrained else None)
                    )
                    == 1
                ]
                ideal = current.min(axis=0) - 0.1 * np.ptp(current, axis=0) - 0.1
                vectors = simplex(10 * population_size, objectives.shape[1])
                gaps = angles(vectors, current - ideal).min(axis=1)
                choices = np.flatnonzero(gaps == gaps.max())
                direction = vectors[rng.choice(choices)]
                local = population_X.copy()
                for _ in range(surrogate_generations):
                    local = np.unique(
                        np.vstack(
                            (
                                local,
                                ga(local, problem.lower, problem.upper, rng),
                                differential_evolution(local, problem.lower, problem.upper, rng, True),
                                differential_evolution(local, problem.lower, problem.upper, rng),
                                differential_evolution(local, problem.lower, problem.upper, rng, True),
                            )
                        ),
                        axis=0,
                    )
                    local_F, local_variance, local_G, local_G_variance = models.predict(local)
                    uncertainty = 2.0 * np.sqrt(local_variance).mean(axis=1)
                    if constrained and local_G.shape[1]:
                        uncertainty = np.sqrt(local_variance).mean(axis=1) + np.sqrt(
                            local_G_variance
                        ).mean(axis=1)
                    score = np.max(np.abs(local_F - ideal) * direction, axis=1) - uncertainty
                    violation = np.maximum(local_G, 0.0).sum(axis=1)
                    if constrained:
                        score[violation > 0] = score.max() + violation[violation > 0]
                    local = local[
                        np.argsort(score, kind="stable")[:population_size]
                    ]
                trial = local[:1]
                if cdist(trial, problem.X).min() > 1e-50:
                    problem.evaluate(trial)

        if problem.n_eval == before:
            return problem.result("no_novel_candidates")
        active = survival(
            graph_sort(dominance(problem.F, problem.G if constrained else None)),
            normalize(problem.F),
            population_size,
        )
        generation += 1
        generation_hook(problem)
    return problem.result()


class DISK(SurrogateAlgorithm):
    # Distribution-informed Kriging-assisted expensive many-objective optimizer.

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
        # Execute the unconstrained DISK variant.
        return run_disk(
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


def make_disk(
    population_size: int = 40,
    surrogate_generations: int = 10,
    infill_batch_size: int = 5,
    seed: int = 1,
) -> DISK:
    # Create a configured DISK instance for the GUI registry.
    return DISK(population_size, surrogate_generations, infill_batch_size, seed)


DISK_DEFINITION: Dict[str, Any] = {
    "label": "DISK",
    "factory": make_disk,
    "supports_constraints": False,
    "implementation_type": "adapted_port",
    "reference": "Z. Zhang et al., IEEE TEVC 29(6), 2656-2670 (2025), DOI 10.1109/TEVC.2024.3519185",
    "verified_against": "article-mechanism tests, deterministic short runs and GUI/Multi integration; no claim of statistical equivalence",
    "form_fields": {
        "population_size": {"default": 40, "kind": "int", "minimum": 2},
        "surrogate_generations": {"default": 10, "kind": "int", "minimum": 1},
        "infill_batch_size": {"default": 5, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": (
        "Distribution-informed Kriging-assisted DISK (2025). The method is intended "
        "for unconstrained expensive many-objective problems. Population size must be even."
    ),
}
