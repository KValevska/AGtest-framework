# Standalone PIMD implementation integrated with the GUI runtime.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
# Basis publication: Y. Li et al., Engineering Applications of Artificial Intelligence
# 133, 108616 (2024), DOI: 10.1016/j.engappai.2024.108616.

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
from scipy.spatial.distance import cdist
from scipy.special import ndtr

from .research_common import non_dominated_fronts, parse_positive_int, sample_reference_directions
from .surrogate_common import (
    Kriging,
    SurrogateAlgorithm,
    SurrogateProblem,
    SurrogateResult,
    evaluation_budget,
    ga,
)


def estimate_pf_shape(objectives: np.ndarray) -> float:
    # Estimate the Lp geometry used by the mapped crowding-distance criterion.
    objectives = np.asarray(objectives, dtype=float)
    if len(objectives) < 20:
        return 1.0
    front = objectives[non_dominated_fronts(objectives)[0]]
    lower = np.min(front, axis=0)
    normalized = (front - lower) / np.maximum(np.ptp(front, axis=0), 1e-12)
    candidates = np.asarray(
        [0.27, 0.36, 0.43, 0.5, 0.57, 0.66, 0.75, 0.86, 1.0, 1.15, 1.35, 1.6, 2.0, 2.4, 3.1, 4.2, 6.5]
    )
    scores = []
    for value in candidates:
        radii = np.sum(normalized**value, axis=1) ** (1.0 / value)
        q1, q3 = np.quantile(radii, [0.25, 0.75])
        clean = radii[radii <= q3 + 1.5 * (q3 - q1)]
        scores.append(np.inf if len(clean) == 0 else np.std(clean / max(float(np.max(clean)), 1e-12)))
    return float(candidates[int(np.argmin(scores))])


def _mapped(values: np.ndarray, power: float) -> np.ndarray:
    shifted = np.asarray(values, dtype=float) + 1e-6
    length = np.sum(np.abs(shifted) ** power, axis=1) ** (1.0 / power)
    return shifted / np.maximum(length[:, None], 1e-12)


def _normalize_pair(left: np.ndarray, right: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    joined = np.vstack((left, right))
    lower = np.min(joined, axis=0)
    scale = np.maximum(np.ptp(joined, axis=0), 1e-12)
    return (left - lower) / scale, (right - lower) / scale


def _nsga3_indices(
    objectives: np.ndarray,
    count: int,
    directions: np.ndarray,
    rng: np.random.Generator,
    ideal: Optional[np.ndarray] = None,
) -> np.ndarray:
    # Return NSGA-III survivor indices while preserving side arrays such as MSE.
    fronts = non_dominated_fronts(objectives)
    selected: list[int] = []
    split = np.empty(0, dtype=int)
    for front in fronts:
        if len(selected) + len(front) <= count:
            selected.extend(front.tolist())
        else:
            split = np.asarray(front, dtype=int)
            break
    if len(selected) >= count:
        return np.asarray(selected[:count], dtype=int)
    pool = np.asarray(selected + split.tolist(), dtype=int)
    shifted = objectives[pool] - (
        np.min(objectives, axis=0) if ideal is None else np.asarray(ideal, dtype=float)
    )
    objective_count = objectives.shape[1]
    extreme = []
    for axis in range(objective_count):
        weights = np.full(objective_count, 1e-6)
        weights[axis] = 1.0
        extreme.append(int(np.argmin(np.max(shifted / weights, axis=1))))
    nadir = np.max(shifted, axis=0)
    try:
        plane = np.linalg.solve(shifted[np.asarray(extreme)], np.ones(objective_count))
        intercepts = 1.0 / plane
        if not np.all(np.isfinite(intercepts)) or np.any(intercepts <= 1e-12):
            intercepts = nadir
    except np.linalg.LinAlgError:
        intercepts = nadir
    normalized = shifted / np.where(intercepts > 1e-12, intercepts, 1.0)
    unit_directions = directions / np.maximum(
        np.linalg.norm(directions, axis=1, keepdims=True), 1e-12
    )
    projections = normalized @ unit_directions.T
    all_distances = np.linalg.norm(
        normalized[:, None, :] - projections[:, :, None] * unit_directions[None, :, :],
        axis=2,
    )
    niches = np.argmin(all_distances, axis=1)
    distances = all_distances[np.arange(len(pool)), niches]
    fixed = len(selected)
    occupancy = np.bincount(niches[:fixed], minlength=len(directions)).astype(int)
    candidates = list(range(fixed, len(pool)))
    while len(selected) < count and candidates:
        available = np.unique(niches[candidates])
        minimum = np.min(occupancy[available])
        niche = int(rng.choice(available[occupancy[available] == minimum]))
        local = [index for index in candidates if niches[index] == niche]
        pick = min(local, key=lambda index: distances[index]) if occupancy[niche] == 0 else int(rng.choice(local))
        selected.append(int(pool[pick]))
        candidates.remove(pick)
        occupancy[niche] += 1
    if len(selected) < count:
        used = set(selected)
        selected.extend(index for index in range(len(objectives)) if index not in used)
    return np.asarray(selected[:count], dtype=int)


def run_pimd(
    function,
    lower: np.ndarray,
    upper: np.ndarray,
    population_size: int,
    maximum_generations: Optional[int],
    wmax: int,
    eta: int,
    seed: int,
    generation_hook,
) -> SurrogateResult:
    rng = np.random.default_rng(seed)
    budget = evaluation_budget(population_size, maximum_generations, eta)
    problem = SurrogateProblem(function, lower, upper, budget)
    problem.initial(population_size, rng)
    active = np.arange(population_size)
    directions = sample_reference_directions(problem.F.shape[1], population_size, 12, rng)
    directions = directions[:population_size]
    theta: list[Optional[np.ndarray]] = [None] * problem.F.shape[1]
    generation = 0
    while problem.n_eval < problem.budget and (
        maximum_generations is None or generation < maximum_generations
    ):
        rounded = np.round(problem.X, 6)
        _, unique = np.unique(rounded, axis=0, return_index=True)
        unique = np.sort(unique)
        models = []
        for objective in range(problem.F.shape[1]):
            model = Kriging(linear=False, theta=theta[objective]).fit(
                problem.X[unique], problem.F[unique, objective]
            )
            theta[objective] = model.theta.copy()
            models.append(model)

        decisions = problem.X[active].copy()
        predicted = problem.F[active].copy()
        variances = np.zeros_like(predicted)
        ideal = np.min(problem.F, axis=0)
        for _ in range(wmax):
            parents = decisions[rng.integers(0, len(decisions), size=population_size)]
            offspring = ga(parents, lower, upper, rng)
            output = [model.predict(offspring) for model in models]
            offspring_F = np.column_stack([item[0] for item in output])
            offspring_V = np.column_stack([item[1] for item in output])
            joined_X = np.vstack((decisions, offspring))
            joined_F = np.vstack((predicted, offspring_F))
            joined_V = np.vstack((variances, offspring_V))
            ideal = np.minimum(ideal, np.min(offspring_F, axis=0))
            keep = _nsga3_indices(joined_F, population_size, directions, rng, ideal=ideal)
            decisions, predicted, variances = joined_X[keep], joined_F[keep], joined_V[keep]

        archive_front = problem.F[non_dominated_fronts(problem.F)[0]]
        novel = np.sum(variances, axis=1) > 1e-15
        novel &= cdist(decisions, problem.X).min(axis=1) > 1e-10
        candidate_X = decisions[novel]
        candidate_F = predicted[novel]
        candidate_V = variances[novel]
        chosen = np.empty((0, len(lower)))
        if len(candidate_X):
            sigma = np.sqrt(np.maximum(candidate_V, 0.0))
            probabilities = []
            for mean, deviation in zip(candidate_F, sigma):
                deterministic = archive_front <= mean
                z = np.divide(
                    archive_front - mean,
                    deviation,
                    out=np.zeros_like(archive_front),
                    where=deviation > 1e-15,
                )
                values = np.where(deviation > 1e-15, ndtr(z), deterministic.astype(float))
                probabilities.append(-float(np.max(np.prod(values, axis=1))))
            probability_improvement = np.asarray(probabilities)
            norm_candidate, norm_archive = _normalize_pair(candidate_F, archive_front)
            power = estimate_pf_shape(problem.F[active])
            mapped_candidate = _mapped(norm_candidate, power)
            mapped_archive = _mapped(norm_archive, power)
            diversity = -cdist(mapped_candidate, mapped_archive).min(axis=1)
            criteria = np.column_stack((diversity, probability_improvement))
            first = non_dominated_fronts(criteria)[0]
            picks = first.tolist()
            if len(picks) > eta:
                best = int(picks[int(np.argmin(probability_improvement[picks]))])
                picks = rng.choice(picks, size=eta, replace=False).tolist()
                if best not in picks:
                    picks[0] = best
            chosen = candidate_X[np.asarray(picks, dtype=int)]
        if len(chosen) == 0:
            chosen = rng.uniform(lower, upper, size=(1, len(lower)))
        before = problem.n_eval
        problem.evaluate(chosen)
        if problem.n_eval == before:
            break
        active = _nsga3_indices(
            problem.F,
            min(population_size, len(problem.F)),
            directions,
            rng,
            ideal=np.min(problem.F, axis=0),
        )
        generation += 1
        generation_hook(problem)
    return problem.result()


class PIMD(SurrogateAlgorithm):
    # Probability-improvement and mapped-distance expensive optimizer.

    def __init__(
        self,
        population_size: int = 20,
        wmax: int = 15,
        eta: int = 5,
        seed: int = 1,
    ) -> None:
        super().__init__(population_size=population_size, seed=seed)
        self.wmax = parse_positive_int(wmax, "wmax")
        self.eta = parse_positive_int(eta, "eta")

    def _run_surrogate(self, function, lower, upper, maximum_generations, seed, generation_hook):
        return run_pimd(
            function,
            lower,
            upper,
            self.population_size,
            maximum_generations,
            self.wmax,
            self.eta,
            seed,
            generation_hook,
        )


def make_pimd(
    population_size: int = 20,
    wmax: int = 15,
    eta: int = 5,
    seed: int = 1,
) -> PIMD:
    return PIMD(population_size=population_size, wmax=wmax, eta=eta, seed=seed)


PIMD_DEFINITION: Dict[str, Any] = {
    "label": "PIMD",
    "factory": make_pimd,
    "implementation_type": "adapted_port",
    "reference": "Y. Li et al., Engineering Applications of Artificial Intelligence 133, 108616 (2024), DOI 10.1016/j.engappai.2024.108616",
    "verified_against": "PlatEMO control flow, probability-improvement and mapped-distance mechanism tests; internal DACE-style Kriging",
    "supports_constraints": False,
    "form_fields": {
        "population_size": {"default": 20, "kind": "int", "minimum": 4},
        "wmax": {"default": 15, "kind": "int", "minimum": 1},
        "eta": {"default": 5, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": (
        "Surrogate-assisted PIMD for bounded real-valued unconstrained expensive problems. "
        "Each GUI generation performs up to eta exact infill evaluations."
    ),
}


__all__ = ["PIMD", "PIMD_DEFINITION", "estimate_pf_shape", "make_pimd", "run_pimd"]
