# HypE hypervolume-estimation operators, pymoo algorithm class and GUI factory.

# ------------------------------------------------------------------------------------
# Module: hype.py
# Summary: HypE fitness routines, selection operators, survival class, algorithm class and GUI factory.
# Implementation: hypervolume-estimation fitness is computed and used for mating, survival and full HypE runs.
# Responsibility: implements a hypervolume-based optimizer for doctoral-dissertation comparisons.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

import ast
from typing import Any, Callable, Dict, List, Optional, Sequence

import numpy as np
from pymoo.algorithms.base.genetic import GeneticAlgorithm
from pymoo.core.survival import Survival
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.selection.tournament import TournamentSelection
from pymoo.termination.default import DefaultMultiObjectiveTermination
from pymoo.util.display.multi import MultiObjectiveOutput


ObjectiveFn = Callable[[Sequence[float]], float]


def _parse_positive_int(value: Any, field_name: str) -> int:
    # Parse a positive integer used by HypE configuration.
    # Raises:
    # ValueError: If conversion fails or the value is below 1.
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def _rng_int(rng: Optional[np.random.Generator], high: int, size: Optional[int | tuple[int, ...]] = None):
    # Draw random integers while supporting both new NumPy generators and legacy random states.
    if rng is None:
        rng = np.random.default_rng()
    if hasattr(rng, "integers"):
        return rng.integers(0, high, size=size)
    return rng.randint(0, high, size=size)


def _rng_random(rng: Optional[np.random.Generator]) -> float:
    # Draw one random float from a provided or default NumPy generator.
    if rng is None:
        rng = np.random.default_rng()
    return float(rng.random())


def _clean_reference(value: Any) -> Any:
    # Normalize reference-point text from the GUI into Python objects or control tokens.
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if text.lower() in {"", "none", "null"}:
            return None
        if text.lower() == "auto":
            return "auto"
        try:
            return ast.literal_eval(text)
        except (SyntaxError, ValueError):
            return text
    return value


def _auto_reference_point(problem: Any, n_obj: int) -> np.ndarray:
    # Build an automatic HypE reference point from problem nadir data or a safe default.
    nadir_fn = getattr(problem, "nadir_point", None)
    if callable(nadir_fn):
        try:
            nadir = np.asarray(nadir_fn(), dtype=float).reshape(-1)
        except (TypeError, ValueError, AttributeError):
            nadir = None
        if nadir is not None and nadir.size == n_obj and np.isfinite(nadir).all():
            margin = 0.1 * np.maximum(1.0, np.abs(nadir))
            return nadir + margin
    return np.full(int(n_obj), 1.1, dtype=float)


def _reference_values(
    n_obj: int,
    problem: Any = None,
    reference_point: Any = None,
    reference_set: Any = None,
) -> np.ndarray:
    # Resolve GUI reference-point/reference-set options into a validated reference set.
    # Build the HypE reference set from the current GUI configuration.
    reference_point = _clean_reference(reference_point)
    reference_set = _clean_reference(reference_set)
    if reference_set is not None and isinstance(reference_point, str) and reference_point.lower() == "auto":
        reference_point = None
    if reference_point is None and reference_set is None:
        reference_point = "auto"
    if isinstance(reference_point, str) and reference_point.lower() == "auto":
        reference_point = _auto_reference_point(problem, n_obj)
    return prepare_reference_set(n_obj, reference_point=reference_point, reference_set=reference_set)


def prepare_reference_set(
    n_obj: int,
    reference_point: Sequence[float] | None = None,
    reference_set: Sequence[Sequence[float]] | None = None,
) -> np.ndarray:
    # Return a validated two-dimensional reference set; a single reference point becomes one row.
    # Raises:
    # ValueError: If both inputs are provided, both are missing or shape/content is invalid.
    if reference_point is not None and reference_set is not None:
        raise ValueError("Use reference_point or reference_set, not both.")
    if reference_point is None and reference_set is None:
        raise ValueError("HypE requires reference_point or reference_set.")

    refs = np.asarray(reference_set if reference_set is not None else reference_point, dtype=float)
    if refs.ndim == 1:
        refs = refs.reshape(1, -1)
    if refs.ndim != 2 or refs.shape[0] == 0 or refs.shape[1] != int(n_obj):
        raise ValueError("Invalid reference_set shape.")
    if not np.isfinite(refs).all():
        raise ValueError("reference_set must be finite.")
    return refs


def fast_non_dominated_sort(objectives: np.ndarray) -> List[List[int]]:
    # Return nondominated fronts for a minimization objective matrix.
    F = np.asarray(objectives, dtype=float)
    n = F.shape[0]
    if n == 0:
        return []

    dominates = np.all(F[:, None, :] <= F[None, :, :], axis=2) & np.any(F[:, None, :] < F[None, :, :], axis=2)
    domination_count = dominates.sum(axis=0).astype(int)
    assigned = np.zeros(n, dtype=bool)
    fronts: List[List[int]] = []

    current = np.where(domination_count == 0)[0]
    while current.size:
        fronts.append(current.tolist())
        assigned[current] = True
        domination_count -= dominates[current].sum(axis=0).astype(int)
        domination_count[current] = -1
        current = np.where((domination_count == 0) & (~assigned))[0]
    return fronts


def _alpha(n: int, k: int, i: int) -> float:
    # Compute the HypE alpha coefficient for a region dominated by `i` points.
    if i <= 0 or i > k:
        return 0.0
    value = 1.0 / i
    for j in range(1, i):
        value *= (k - j) / (n - j)
    return value


def _axis_edges(F: np.ndarray, R: np.ndarray) -> list[np.ndarray]:
    # Build sorted objective-axis breakpoints from solution and reference coordinates.
    edges = []
    for axis in range(F.shape[1]):
        values = np.unique(np.concatenate([F[:, axis], R[:, axis]]))
        values = values[np.isfinite(values)]
        values.sort()
        edges.append(values)
    return edges


def exact_hype_fitness(objectives: np.ndarray, reference_set: np.ndarray, k: int) -> np.ndarray:
    # Compute exact classic HypE fitness for up to three objectives.
    # Raises:
    # ValueError: If objective and reference arrays are not compatible matrices.
    F = np.asarray(objectives, dtype=float)
    R = np.asarray(reference_set, dtype=float)
    if F.ndim != 2 or R.ndim != 2 or F.shape[1] != R.shape[1]:
        raise ValueError("objectives and reference_set must be 2D with matching dimensions.")
    if F.shape[0] == 0:
        return np.zeros(0, dtype=float)

    n, n_obj = F.shape
    k = min(max(int(k), 1), n)
    fitness = np.zeros(n, dtype=float)

    edges = _axis_edges(F, R)
    if any(edge.size < 2 for edge in edges):
        return fitness

    ranges = [range(edge.size - 1) for edge in edges]
    for cell in np.ndindex(*(len(item) for item in ranges)):
        lower = np.array([edges[axis][cell[axis]] for axis in range(n_obj)], dtype=float)
        upper = np.array([edges[axis][cell[axis] + 1] for axis in range(n_obj)], dtype=float)
        widths = upper - lower
        if np.any(widths <= 0.0):
            continue
        if not np.any(np.all(upper[None, :] <= R, axis=1)):
            continue
        dom_ids = np.flatnonzero(np.all(F <= lower[None, :], axis=1))
        weight = _alpha(n, k, int(dom_ids.size))
        if weight > 0.0:
            fitness[dom_ids] += weight * float(np.prod(widths))
    return fitness


def estimated_hype_fitness(
    objectives: np.ndarray,
    reference_set: np.ndarray,
    k: int,
    n_samples: int,
    rng: Optional[np.random.Generator] = None,
) -> np.ndarray:
    # Estimate HypE fitness with Monte Carlo sampling for higher-dimensional objectives.
    # Raises:
    # ValueError: If objective and reference arrays are not compatible matrices.
    if rng is None:
        rng = np.random.default_rng()

    F = np.asarray(objectives, dtype=float)
    R = np.asarray(reference_set, dtype=float)
    if F.ndim != 2 or R.ndim != 2 or F.shape[1] != R.shape[1]:
        raise ValueError("objectives and reference_set must be 2D with matching dimensions.")
    if F.shape[0] == 0:
        return np.zeros(0, dtype=float)

    n = F.shape[0]
    k = min(max(int(k), 1), n)
    n_samples = max(int(n_samples), 1)
    lower = F.min(axis=0)
    upper = R.max(axis=0)
    widths = upper - lower
    if np.any(widths <= 0.0):
        return np.zeros(n, dtype=float)

    samples = rng.uniform(lower, upper, size=(n_samples, F.shape[1]))
    in_ref = np.any(np.all(samples[:, None, :] <= R[None, :, :], axis=2), axis=1)
    dominated = np.all(F[:, None, :] <= samples[None, :, :], axis=2)
    box_volume = float(np.prod(widths))
    fitness = np.zeros(n, dtype=float)

    for sample_id in np.flatnonzero(in_ref):
        dom_ids = np.flatnonzero(dominated[:, sample_id])
        weight = _alpha(n, k, int(dom_ids.size))
        if weight > 0.0:
            fitness[dom_ids] += weight * box_volume / n_samples
    return fitness


def hype_fitness(
    objectives: np.ndarray,
    reference_set: np.ndarray,
    k: int,
    n_samples: int,
    rng: Optional[np.random.Generator] = None,
) -> np.ndarray:
    # Choose exact or estimated HypE fitness depending on objective dimensionality.
    if np.asarray(objectives).shape[1] <= 3:
        return exact_hype_fitness(objectives, reference_set, k)
    return estimated_hype_fitness(objectives, reference_set, k, n_samples, rng)


def mating_selection(
    population: np.ndarray,
    n_obj: int,
    reference_set: np.ndarray,
    n_offspring: int,
    n_samples: int,
    rng: Optional[np.random.Generator] = None,
) -> np.ndarray:
    # Select parents by binary tournament using HypE fitness; `k` equals offspring count.
    if rng is None:
        rng = np.random.default_rng()

    fitness = hype_fitness(population[:, -n_obj:], reference_set, k=n_offspring, n_samples=n_samples, rng=rng)
    selected = np.empty(int(n_offspring), dtype=int)
    for i in range(int(n_offspring)):
        a, b = _rng_int(rng, population.shape[0], size=2)
        if fitness[a] > fitness[b]:
            selected[i] = a
        elif fitness[b] > fitness[a]:
            selected[i] = b
        else:
            selected[i] = a if _rng_random(rng) < 0.5 else b
    return population[selected]


def _eval_objectives(x: np.ndarray, functions: Sequence[ObjectiveFn]) -> np.ndarray:
    # Evaluate all objective functions for one decision vector.
    return np.asarray([fn(x) for fn in functions], dtype=float)


def _new_population(
    size: int,
    min_values: np.ndarray,
    max_values: np.ndarray,
    functions: Sequence[ObjectiveFn],
    rng: np.random.Generator,
) -> np.ndarray:
    # Create an initial classic-HypE population containing decision variables and objectives.
    X = rng.uniform(min_values, max_values, size=(int(size), min_values.size))
    F = np.asarray([_eval_objectives(x, functions) for x in X], dtype=float)
    return np.hstack([X, F])


def crossover(
    parents: np.ndarray,
    min_values: Sequence[float],
    max_values: Sequence[float],
    functions: Sequence[ObjectiveFn],
    size: int,
    mu: float = 20.0,
    rng: Optional[np.random.Generator] = None,
) -> np.ndarray:
    # Apply simulated binary crossover and evaluate generated offspring.
    if rng is None:
        rng = np.random.default_rng()

    min_values = np.asarray(min_values, dtype=float)
    max_values = np.asarray(max_values, dtype=float)
    n_var = min_values.size
    n_obj = len(functions)
    offspring = np.zeros((int(size), n_var + n_obj), dtype=float)

    for i in range(int(size)):
        p1, p2 = parents[_rng_int(rng, parents.shape[0], size=2), :n_var]
        child = p1.copy()
        for j in range(n_var):
            y1, y2 = float(p1[j]), float(p2[j])
            yl, yu = float(min_values[j]), float(max_values[j])
            if _rng_random(rng) > 0.5 or abs(y1 - y2) <= 1e-14:
                child[j] = y1 if _rng_random(rng) < 0.5 else y2
                continue
            if y1 > y2:
                y1, y2 = y2, y1
            rand = _rng_random(rng)
            beta = 1.0 + 2.0 * (y1 - yl) / (y2 - y1)
            alpha = 2.0 - beta ** (-(mu + 1.0))
            if rand <= 1.0 / alpha:
                betaq = (rand * alpha) ** (1.0 / (mu + 1.0))
            else:
                betaq = (1.0 / (2.0 - rand * alpha)) ** (1.0 / (mu + 1.0))
            c1 = 0.5 * ((y1 + y2) - betaq * (y2 - y1))

            beta = 1.0 + 2.0 * (yu - y2) / (y2 - y1)
            alpha = 2.0 - beta ** (-(mu + 1.0))
            if rand <= 1.0 / alpha:
                betaq = (rand * alpha) ** (1.0 / (mu + 1.0))
            else:
                betaq = (1.0 / (2.0 - rand * alpha)) ** (1.0 / (mu + 1.0))
            c2 = 0.5 * ((y1 + y2) + betaq * (y2 - y1))
            child[j] = np.clip(c1 if _rng_random(rng) < 0.5 else c2, yl, yu)
        offspring[i, :n_var] = child
        offspring[i, n_var:] = _eval_objectives(child, functions)
    return offspring


def mutation(
    offspring: np.ndarray,
    min_values: Sequence[float],
    max_values: Sequence[float],
    functions: Sequence[ObjectiveFn],
    mutation_rate: float = 0.1,
    eta: float = 20.0,
    rng: Optional[np.random.Generator] = None,
) -> np.ndarray:
    # Apply polynomial mutation in-place and refresh offspring objective values.
    if rng is None:
        rng = np.random.default_rng()

    min_values = np.asarray(min_values, dtype=float)
    max_values = np.asarray(max_values, dtype=float)
    n_var = min_values.size
    n_obj = len(functions)

    for i in range(offspring.shape[0]):
        for j in range(n_var):
            if _rng_random(rng) >= float(mutation_rate):
                continue
            y = float(offspring[i, j])
            yl, yu = float(min_values[j]), float(max_values[j])
            delta1 = (y - yl) / (yu - yl)
            delta2 = (yu - y) / (yu - yl)
            rand = _rng_random(rng)
            mut_pow = 1.0 / (eta + 1.0)
            if rand < 0.5:
                xy = 1.0 - delta1
                val = 2.0 * rand + (1.0 - 2.0 * rand) * (xy ** (eta + 1.0))
                deltaq = val ** mut_pow - 1.0
            else:
                xy = 1.0 - delta2
                val = 2.0 * (1.0 - rand) + 2.0 * (rand - 0.5) * (xy ** (eta + 1.0))
                deltaq = 1.0 - val ** mut_pow
            offspring[i, j] = np.clip(y + deltaq * (yu - yl), yl, yu)
        offspring[i, n_var : n_var + n_obj] = _eval_objectives(offspring[i, :n_var], functions)
    return offspring


def environmental_selection(
    population: np.ndarray,
    population_size: int,
    n_obj: int,
    reference_set: np.ndarray,
    n_samples: int,
    rng: Optional[np.random.Generator] = None,
) -> np.ndarray:
    # Keep the next generation by nondominated sorting and iterative HypE truncation.
    if rng is None:
        rng = np.random.default_rng()

    objectives = population[:, -n_obj:]
    fronts = fast_non_dominated_sort(objectives)
    keep: List[int] = []
    front_id = 0
    while front_id < len(fronts) and len(keep) + len(fronts[front_id]) <= int(population_size):
        keep.extend(fronts[front_id])
        front_id += 1
    if len(keep) == int(population_size) or front_id >= len(fronts):
        return population[np.asarray(keep, dtype=int)]

    current = np.asarray(fronts[front_id], dtype=int)
    k_remove = len(keep) + current.size - int(population_size)
    while k_remove > 0:
        fitness = hype_fitness(objectives[current], reference_set, k=k_remove, n_samples=n_samples, rng=rng)
        worst = np.flatnonzero(np.isclose(fitness, fitness.min()))
        current = np.delete(current, int(worst[_rng_int(rng, worst.size)]))
        k_remove -= 1
    keep.extend(current.tolist())
    return population[np.asarray(keep, dtype=int)]


def hype_tournament(pop, P, random_state=None, **kwargs):
    # pymoo tournament comparator that selects parents using HypE fitness.
    # Raises:
    # ValueError: If tournament arity or algorithm context is invalid.
    n_tournaments, n_parents = P.shape
    if n_parents != 2:
        raise ValueError("HypE uses binary tournament selection.")

    algorithm = kwargs.get("algorithm")
    if algorithm is None:
        raise ValueError("HypE tournament requires algorithm context.")
    F = np.asarray(pop.get("F"), dtype=float)
    refs = algorithm.reference_values(F.shape[1])
    rng = random_state or getattr(algorithm, "random_state", None)
    fitness = hype_fitness(F, refs, k=n_tournaments, n_samples=algorithm.n_samples, rng=rng)
    selected = np.full(n_tournaments, np.nan)

    for i in range(n_tournaments):
        a, b = int(P[i, 0]), int(P[i, 1])
        if fitness[a] > fitness[b]:
            selected[i] = a
        elif fitness[b] > fitness[a]:
            selected[i] = b
        else:
            selected[i] = a if _rng_random(rng) < 0.5 else b
    return selected[:, None].astype(int, copy=False)


class HypESurvival(Survival):
    # pymoo survival operator that truncates a population with HypE fitness.
    # wedlug frontow Pareto i oceny HypE.

    def __init__(self, reference_point: Any = "auto", reference_set: Any = None, n_samples: int = 1000):
        # Configure reference data and Monte Carlo sample count for HypE survival.
        super().__init__(filter_infeasible=True)
        self.reference_point = reference_point
        self.reference_set = reference_set
        self.n_samples = _parse_positive_int(n_samples, "n_samples")

    def _do(self, problem, pop, *args, n_survive=None, **kwargs):
        # Select survivors from a pymoo population for the next generation.
        if n_survive is None:
            n_survive = len(pop)
        if len(pop) <= int(n_survive):
            return pop

        F = np.asarray(pop.get("F"), dtype=float)
        refs = _reference_values(F.shape[1], problem, self.reference_point, self.reference_set)
        fronts = fast_non_dominated_sort(F)
        keep: List[int] = []
        front_id = 0
        while front_id < len(fronts) and len(keep) + len(fronts[front_id]) <= int(n_survive):
            keep.extend(fronts[front_id])
            front_id += 1
        if len(keep) == int(n_survive) or front_id >= len(fronts):
            return pop[np.asarray(keep, dtype=int)]

        current = np.asarray(fronts[front_id], dtype=int)
        k_remove = len(keep) + current.size - int(n_survive)
        rng = getattr(kwargs.get("algorithm", None), "random_state", None)
        while k_remove > 0:
            fitness = hype_fitness(F[current], refs, k=k_remove, n_samples=self.n_samples, rng=rng)
            worst = np.flatnonzero(np.isclose(fitness, fitness.min()))
            current = np.delete(current, int(worst[_rng_int(rng, worst.size)]))
            k_remove -= 1
        keep.extend(current.tolist())
        return pop[np.asarray(keep, dtype=int)]


class HypE(GeneticAlgorithm):
    # pymoo genetic algorithm using HypE survival and tournament selection.

    def __init__(
        self,
        pop_size: int = 40,
        reference_point: Any = "auto",
        reference_set: Any = None,
        n_samples: int = 1000,
        sampling=FloatRandomSampling(),
        selection=TournamentSelection(func_comp=hype_tournament),
        crossover=SBX(eta=15, prob=0.9),
        mutation=PM(eta=20),
        output=MultiObjectiveOutput(),
        **kwargs,
    ):
        # Initialize HypE with sampling, variation operators and hypervolume reference data.
        self.reference_point = reference_point
        self.reference_set = reference_set
        self.n_samples = _parse_positive_int(n_samples, "n_samples")
        super().__init__(
            pop_size=_parse_positive_int(pop_size, "pop_size"),
            sampling=sampling,
            selection=selection,
            crossover=crossover,
            mutation=mutation,
            survival=HypESurvival(reference_point, reference_set, self.n_samples),
            output=output,
            advance_after_initial_infill=True,
            **kwargs,
        )
        self.termination = DefaultMultiObjectiveTermination()

    def reference_values(self, n_obj: int) -> np.ndarray:
        # Return validated reference values for the current problem and objective count.
        return _reference_values(n_obj, getattr(self, "problem", None), self.reference_point, self.reference_set)


def hype(
    min_values: Sequence[float],
    max_values: Sequence[float],
    functions: Sequence[ObjectiveFn],
    population_size: int = 100,
    generations: int = 50,
    reference_point: Sequence[float] | None = None,
    reference_set: Sequence[Sequence[float]] | None = None,
    n_samples: int = 1000,
    mutation_rate: float = 0.1,
    mu: float = 20.0,
    eta: float = 20.0,
    rng: Optional[np.random.Generator] = None,
) -> np.ndarray:
    # Run the standalone classic HypE loop and return the final objective matrix.
    if rng is None:
        rng = np.random.default_rng()

    min_values = np.asarray(min_values, dtype=float)
    max_values = np.asarray(max_values, dtype=float)
    n_obj = len(functions)
    refs = prepare_reference_set(n_obj, reference_point=reference_point, reference_set=reference_set)
    population = _new_population(population_size, min_values, max_values, functions, rng)

    for _ in range(int(generations)):
        parents = mating_selection(population, n_obj, refs, int(population_size), int(n_samples), rng)
        offspring = crossover(parents, min_values, max_values, functions, int(population_size), mu, rng)
        offspring = mutation(offspring, min_values, max_values, functions, mutation_rate, eta, rng)
        population = environmental_selection(
            np.vstack([population, offspring]),
            int(population_size),
            n_obj,
            refs,
            int(n_samples),
            rng,
        )
    return population[:, -n_obj:]


def make_hype(
    problem: Any = None,
    pop_size: int = 40,
    reference_point: Any = "auto",
    reference_set: Any = None,
    n_samples: int = 1000,
) -> HypE:
    # Validate reference settings and create a GUI-registered `HypE` instance.
    # Args:
    # problem (Any): Problem used for automatic reference-point construction.
    # pop_size (int): Population size.
    # reference_point (Any): Explicit reference point or `"auto"`.
    # reference_set (Any): Optional set of reference points.
    # n_samples (int): Monte Carlo sample count for estimated fitness.
    # Returns:
    # HypE: Configured pymoo-compatible HypE algorithm.
    # Raises:
    # ValueError: If reference settings or integer parameters are invalid.
    n_obj = int(getattr(problem, "n_obj", 2))
    _reference_values(n_obj, problem, reference_point, reference_set)
    return HypE(
        pop_size=pop_size,
        reference_point=reference_point,
        reference_set=reference_set,
        n_samples=n_samples,
    )


HYPE_DEFINITION: Dict[str, Any] = {
    "label": "HypE",
    "factory": make_hype,
    "form_fields": {
        "pop_size": {"default": 40, "kind": "int", "minimum": 1},
        "reference_point": {"default": "auto", "kind": "any"},
        "reference_set": {"default": None, "kind": "any"},
        "n_samples": {"default": 1000, "kind": "int", "minimum": 1},
    },
    "form_note": "reference_point='auto' uzywa nadir_point problemu, a gdy go nie ma: [1.1, ..., 1.1].",
}
HYPE_DEFINITION["form_note"] = (
    "reference_point='auto' uses the problem nadir_point, or [1.1, ..., 1.1] when it is unavailable."
)
