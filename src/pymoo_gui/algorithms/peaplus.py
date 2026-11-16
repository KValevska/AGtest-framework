# PEAplus implementation and GUI factory definition.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
#
# ------------------------------------------------------------------------------------
# Module: peaplus.py
# Summary: constrained probabilistic Pareto dominance and shifted-distance infill.
# Implementation: objective and constraint Kriging models guide CPPD survival; candidate
# batches are diversified in normalized objective and constraint-violation coordinates.
# Responsibility: adds the 2025 expensive constrained PEAplus method to GUI experiments.
# Author: Kristina Valevska, MSc Eng.
# Article reference: Z. Zhang, Y. Wang, G. Sun, and K. Tang, "Constrained
# probabilistic Pareto dominance for expensive constrained multiobjective
# optimization problems," IEEE TEVC, 2025, 29(4): 1138-1152.
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
    constraint_coordinate,
    distances,
    dominance,
    evaluation_budget,
    ga,
    graph_sort,
    probability_leq,
    survival,
    weighted_probability_sort,
)
from .research_common import parse_positive_int


def cppd(
    objectives: np.ndarray,
    variance: np.ndarray,
    constraints: np.ndarray,
    constraint_variance: np.ndarray,
) -> np.ndarray:
    # Rank predictions by constrained probabilistic Pareto dominance.
    feasibility = probability_leq(constraints, constraint_variance)
    weight = feasibility.min(axis=1) if constraints.shape[1] else np.ones(len(objectives))
    return weighted_probability_sort(objectives, variance, weight)


def run_peaplus(
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
    # Execute the PEAplus outer optimization loop.
    rng = np.random.default_rng(seed)
    problem = SurrogateProblem(
        function,
        lower,
        upper,
        evaluation_budget(population_size, maximum_generations, infill_batch_size),
    )
    problem.initial(population_size, rng)
    active = np.arange(population_size)
    models = Models()
    generation = 0
    while maximum_generations is None or generation < maximum_generations:
        models.fit(problem.X, problem.F, problem.G)
        population_X = problem.X[active].copy()
        population_F = problem.F[active].copy()
        population_G = problem.G[active].copy()
        variance_F = np.zeros_like(population_F)
        variance_G = np.zeros_like(population_G)
        for _ in range(surrogate_generations):
            offspring = ga(population_X, problem.lower, problem.upper, rng)
            offspring_F, offspring_variance, offspring_G, offspring_G_variance = models.predict(
                offspring
            )
            population_X = np.vstack((population_X, offspring))
            population_F = np.vstack((population_F, offspring_F))
            variance_F = np.vstack((variance_F, offspring_variance))
            population_G = np.vstack((population_G, offspring_G))
            variance_G = np.vstack((variance_G, offspring_G_variance))
            take = survival(
                cppd(population_F, variance_F, population_G, variance_G),
                constraint_coordinate(population_F, population_G),
                population_size,
                "shift",
            )
            population_X, population_F, variance_F, population_G, variance_G = (
                values[take]
                for values in (
                    population_X,
                    population_F,
                    variance_F,
                    population_G,
                    variance_G,
                )
            )

        novel = np.flatnonzero(cdist(population_X, problem.X).min(axis=1) > 1e-5)
        count = min(infill_batch_size, len(novel))
        if not count:
            return problem.result("no_novel_candidates")
        if len(novel) <= count:
            chosen = novel
        else:
            joined_F = np.vstack((problem.F, population_F[novel]))
            lower_F = joined_F.min(axis=0)
            scale_F = np.maximum(np.ptp(joined_F, axis=0), 1e-9)
            candidate_F = (population_F[novel] - lower_F) / scale_F
            archive_F = (problem.F - lower_F) / scale_F
            candidate_G = np.maximum(population_G[novel], 0.0)
            archive_G = np.maximum(problem.G, 0.0)
            constraint_scale = np.maximum(
                np.vstack((candidate_G, archive_G)).max(axis=0),
                1e-9,
            )
            candidate_G = candidate_G / constraint_scale
            archive_G = archive_G / constraint_scale
            candidate_violation = candidate_G.sum(axis=1)
            archive_violation = archive_G.sum(axis=1)
            violation_scale = max(
                np.r_[candidate_violation, archive_violation].max(),
                1e-9,
            )
            candidate_violation /= violation_scale
            archive_violation /= violation_scale
            archive_front = graph_sort(dominance(archive_F, archive_G))
            cutoff = (
                1
                if np.sum(np.all(archive_G <= 0.0, axis=1)) >= population_size
                else np.sort(archive_front)[population_size - 1]
            )
            reference = np.column_stack(
                (
                    archive_F[archive_front <= cutoff],
                    archive_violation[archive_front <= cutoff],
                )
            )
            candidate_front = cppd(
                candidate_F,
                variance_F[novel] / scale_F**2,
                candidate_G,
                variance_G[novel],
            )
            candidate_cutoff = np.sort(candidate_front)[count - 1]
            selected = list(np.flatnonzero(candidate_front < candidate_cutoff))
            tail = list(np.flatnonzero(candidate_front == candidate_cutoff))
            candidate_values = np.column_stack((candidate_F, candidate_violation))
            if selected:
                reference = np.vstack((reference, candidate_values[selected]))
            while len(selected) < count:
                index = int(
                    np.argmax(
                        distances(candidate_values[tail], reference, "shift").min(axis=1)
                    )
                )
                candidate = tail.pop(index)
                selected.append(candidate)
                reference = np.vstack((reference, candidate_values[candidate]))
            chosen = novel[selected]
        problem.evaluate(population_X[chosen])
        active = survival(
            graph_sort(dominance(problem.F, problem.G)),
            constraint_coordinate(problem.F, problem.G),
            population_size,
            "shift",
        )
        generation += 1
        generation_hook(problem)
    return problem.result()


class PEAplus(SurrogateAlgorithm):
    # Constrained probabilistic Pareto-dominance expensive optimizer.

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
        # Execute PEAplus with the configured surrogate and infill batch sizes.
        return run_peaplus(
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


def make_peaplus(
    population_size: int = 40,
    surrogate_generations: int = 10,
    infill_batch_size: int = 5,
    seed: int = 1,
) -> PEAplus:
    # Create a configured PEAplus instance for the GUI registry.
    return PEAplus(population_size, surrogate_generations, infill_batch_size, seed)


PEAPLUS_DEFINITION: Dict[str, Any] = {
    "label": "PEAplus",
    "factory": make_peaplus,
    "requires_constraints": True,
    "implementation_type": "adapted_port",
    "reference": "Z. Zhang et al., constrained probabilistic Pareto dominance, IEEE TEVC 29(4), 1138-1152 (2025)",
    "verified_against": "CPPD mechanism tests, deterministic constrained runs and GUI/Multi integration; no claim of statistical equivalence",
    "form_fields": {
        "population_size": {"default": 40, "kind": "int", "minimum": 2},
        "surrogate_generations": {"default": 10, "kind": "int", "minimum": 1},
        "infill_batch_size": {"default": 5, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": (
        "Constrained probabilistic Pareto-dominance PEAplus (2025) with Kriging "
        "and shifted-distance infill selection. Population size must be even."
    ),
}
