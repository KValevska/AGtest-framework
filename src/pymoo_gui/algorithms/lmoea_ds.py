# LMOEA-DS implementation and GUI factory definition.
#
# ------------------------------------------------------------------------------------
# Module: lmoea_ds.py
# Summary: directed sampling, double reproduction, complementary environmental selection and GUI factory.
# Implementation: the algorithm follows the LMOEA-DS framework with guided solutions sampled along decision-space directions.
# Responsibility: adds a large-scale evolutionary multi-objective optimizer assisted by directed sampling.
# Author: Kristina Valevska, MSc Eng.
# Implementation source: based on Qin, S. et al. "Large-scale Evolutionary Multi-objective Optimization Assisted by Directed Sampling" (IEEE TEVC, 2021).
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np

from .research_common import (
    FEASIBILITY_TOL,
    PopulationState,
    ResearchMOOAlgorithm,
    assign_rank_and_crowding,
    feasible_mask,
    normalized_objectives,
    parse_positive_int,
    parse_probability,
    problem_n_obj,
    project_to_bounds,
    sample_reference_directions,
    sbx_crossover,
    select_survivors_nsga2,
    stable_survivor_order,
)


def _simple_kmeans(points: np.ndarray, n_clusters: int, rng: np.random.Generator, n_iter: int = 20) -> np.ndarray:
    # Cluster reference directions with a compact NumPy k-means used to build W0.
    points = np.asarray(points, dtype=float)
    if points.shape[0] <= int(n_clusters):
        return points.copy()

    ids = rng.choice(points.shape[0], size=int(n_clusters), replace=False)
    centers = points[ids].copy()
    for _ in range(int(n_iter)):
        distances = np.linalg.norm(points[:, None, :] - centers[None, :, :], axis=2)
        assignment = np.argmin(distances, axis=1)
        new_centers = centers.copy()
        for idx in range(int(n_clusters)):
            mask = assignment == idx
            if np.any(mask):
                new_centers[idx] = np.mean(points[mask], axis=0)
            else:
                new_centers[idx] = points[int(rng.integers(0, points.shape[0]))]
        if np.allclose(new_centers, centers):
            break
        centers = new_centers
    return centers


def _boundary_reference_vectors(ref_dirs: np.ndarray, n_obj: int) -> np.ndarray:
    # Pick reference vectors closest to unit basis directions as boundary vectors.
    ref_dirs = np.asarray(ref_dirs, dtype=float)
    eye = np.eye(int(n_obj), dtype=float)
    chosen: list[int] = []
    for basis in eye:
        distances = np.linalg.norm(ref_dirs - basis[None, :], axis=1)
        order = np.argsort(distances, kind="mergesort")
        for idx in order:
            idx = int(idx)
            if idx not in chosen:
                chosen.append(idx)
                break
    return ref_dirs[np.asarray(chosen, dtype=int)] if chosen else np.empty((0, int(n_obj)), dtype=float)


def _unique_rows(arr: np.ndarray) -> np.ndarray:
    # Return unique rows while preserving the first occurrence order.
    arr = np.asarray(arr, dtype=float)
    if arr.ndim != 2 or arr.shape[0] <= 1:
        return arr
    _, ids = np.unique(np.round(arr, 12), axis=0, return_index=True)
    return arr[np.sort(ids)]


def _normalize_rows(arr: np.ndarray) -> np.ndarray:
    # Normalize reference directions row-wise and avoid zero vectors.
    arr = np.asarray(arr, dtype=float)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    return arr / np.where(norms > 1e-12, norms, 1.0)


def _pairwise_sbx(
    parents_a: np.ndarray,
    parents_b: np.ndarray,
    xl: np.ndarray,
    xu: np.ndarray,
    eta: float,
    prob: float,
    rng: np.random.Generator,
) -> np.ndarray:
    # Apply SBX to explicit parent pairs.
    pair_count = min(parents_a.shape[0], parents_b.shape[0])
    pool = np.vstack([parents_a[:pair_count], parents_b[:pair_count]])
    parent_pairs = np.column_stack([np.arange(pair_count), np.arange(pair_count, 2 * pair_count)])
    return sbx_crossover(pool, parent_pairs, xl, xu, eta, prob, rng)


class LMOEADS(ResearchMOOAlgorithm):
    # Large-scale MOEA assisted by directed sampling.

    def __init__(
        self,
        population_size: int = 153,
        archive_size: int = 153,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.0,
        crossover_eta: float = 20.0,
        mutation_eta: float = 20.0,
        guiding_vector_count: int = 12,
        samples_per_direction: int = 30,
        selection_threshold_ratio: float = 2.0 / 3.0,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=archive_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            crossover_eta=crossover_eta,
            mutation_eta=mutation_eta,
            seed=seed,
        )
        self.guiding_vector_count = parse_positive_int(guiding_vector_count, "guiding_vector_count")
        self.samples_per_direction = parse_positive_int(samples_per_direction, "samples_per_direction")
        self.selection_threshold_ratio = parse_probability(selection_threshold_ratio, "selection_threshold_ratio")
        self.guiding_reference_directions: Optional[np.ndarray] = None

    def after_initialize(self) -> None:
        # Build W0 after the problem objective count becomes known.
        self.guiding_reference_directions = self._build_guiding_reference_directions()

    def _effective_mutation_rate(self) -> float:
        # Use the article default 1 / D when the GUI parameter is left at zero.
        if self.mutation_rate > 0.0:
            return self.mutation_rate
        return 1.0 / max(self.n_var, 1)

    def mutation(self, offspring: np.ndarray) -> np.ndarray:
        # Mutate offspring with article-style polynomial mutation probability 1 / D by default.
        from .research_common import polynomial_mutation

        return polynomial_mutation(
            offspring,
            self.xl,
            self.xu,
            self.mutation_eta,
            self._effective_mutation_rate(),
            self.random_state,
        )

    def _build_guiding_reference_directions(self) -> np.ndarray:
        # Build the smaller W0 set from W using k-means plus boundary directions.
        if self.reference_directions is None or self.reference_directions.size == 0:
            return sample_reference_directions(
                self.n_obj,
                self.guiding_vector_count,
                max(self.n_partitions, 1),
                self.random_state,
            )[: self.guiding_vector_count]

        ref_dirs = _normalize_rows(np.asarray(self.reference_directions, dtype=float))
        m = min(self.n_obj, self.guiding_vector_count)
        boundary = _boundary_reference_vectors(ref_dirs, self.n_obj)
        n_clusters = max(0, self.guiding_vector_count - boundary.shape[0])
        clustered = _simple_kmeans(ref_dirs, n_clusters, self.random_state) if n_clusters > 0 else np.empty((0, self.n_obj), dtype=float)
        combined = np.vstack([clustered, boundary]) if boundary.size else clustered
        combined = _unique_rows(_normalize_rows(combined))

        if combined.shape[0] < self.guiding_vector_count:
            need = self.guiding_vector_count - combined.shape[0]
            order = np.arange(ref_dirs.shape[0])
            self.random_state.shuffle(order)
            extras = []
            existing = combined if combined.size else np.empty((0, self.n_obj), dtype=float)
            for idx in order:
                candidate = ref_dirs[int(idx)]
                if existing.shape[0] and np.any(np.all(np.isclose(existing, candidate[None, :]), axis=1)):
                    continue
                extras.append(candidate)
                if len(extras) >= need:
                    break
            if extras:
                combined = np.vstack([combined, np.asarray(extras, dtype=float)]) if combined.size else np.asarray(extras, dtype=float)

        return combined[: self.guiding_vector_count]

    def _guided_assignment_objectives(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Normalize current objectives and return normalized values plus ideal and distances.
        assert self.state is not None
        Fn, _, _ = normalized_objectives(self.state.F)
        distances = np.linalg.norm(Fn, axis=1)
        return Fn, self.state.F, distances

    def _identify_search_seeds(self) -> np.ndarray:
        # Select one representative solution for each W0 vector as in Algorithm 1.
        assert self.state is not None
        W0 = self.guiding_reference_directions
        if W0 is None or W0.size == 0:
            return self.state.X[: min(self.guiding_vector_count, self.state.X.shape[0])]

        Fn, _, distances = self._guided_assignment_objectives()
        ref_dirs = _normalize_rows(W0)
        point_norms = np.linalg.norm(Fn, axis=1, keepdims=True)
        point_unit = Fn / np.where(point_norms > 1e-12, point_norms, 1.0)
        cosine = np.clip(point_unit @ ref_dirs.T, -1.0, 1.0)
        angles = np.arccos(cosine)
        assignment = np.argmin(angles, axis=1)

        chosen: list[int] = []
        for ref_idx in range(ref_dirs.shape[0]):
            candidates = np.flatnonzero(assignment == ref_idx)
            if candidates.size:
                local = candidates[np.argmin(distances[candidates])]
                chosen.append(int(local))

        for ref_idx in range(ref_dirs.shape[0]):
            if len(chosen) >= ref_dirs.shape[0]:
                break
            if np.any(assignment[np.asarray(chosen, dtype=int)] == ref_idx) if chosen else False:
                continue
            order = np.argsort(angles[:, ref_idx], kind="mergesort")
            for idx in order:
                idx = int(idx)
                if idx not in chosen:
                    chosen.append(idx)
                    break

        if not chosen:
            chosen = list(range(min(self.population_size, ref_dirs.shape[0])))
        return self.state.X[np.asarray(chosen[: ref_dirs.shape[0]], dtype=int)]

    def _sample_guiding_solutions(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Generate guiding solutions by directed sampling and keep their nondominated subset.
        seeds = self._identify_search_seeds()
        if seeds.size == 0:
            return (
                np.empty((0, self.n_var), dtype=float),
                np.empty((0, self.n_obj), dtype=float),
                np.empty(0, dtype=float),
            )

        span_norm = float(np.linalg.norm(self.xu - self.xl))
        sampled: list[np.ndarray] = []
        for seed in np.asarray(seeds, dtype=float):
            lower_dir = seed - self.xl
            upper_dir = seed - self.xu
            lower_norm = float(np.linalg.norm(lower_dir))
            upper_norm = float(np.linalg.norm(upper_dir))

            for _ in range(self.samples_per_direction):
                if lower_norm > 1e-12:
                    step = float(self.random_state.uniform(0.0, span_norm))
                    sampled.append(self.xl + step * lower_dir / lower_norm)
                else:
                    sampled.append(seed.copy())
                if upper_norm > 1e-12:
                    step = float(self.random_state.uniform(0.0, span_norm))
                    sampled.append(self.xu + step * upper_dir / upper_norm)
                else:
                    sampled.append(seed.copy())

        guided = project_to_bounds(np.asarray(sampled, dtype=float), self.xl, self.xu)
        F, CV = self.evaluate(guided)
        state = select_survivors_nsga2(guided, F, CV, guided.shape[0])
        rank0 = state.rank == 0
        if np.any(rank0):
            return state.X[rank0], state.F[rank0], state.CV[rank0]
        limit = min(self.population_size, state.X.shape[0])
        return state.X[:limit], state.F[:limit], state.CV[:limit]

    def _first_reproduction(self, guiding: np.ndarray) -> np.ndarray:
        # Cross each parent with one random guiding solution, then mutate.
        assert self.state is not None
        if guiding.size == 0:
            return self.create_offspring()
        guide_ids = self.random_state.integers(0, guiding.shape[0], size=self.state.X.shape[0])
        offspring = _pairwise_sbx(
            self.state.X,
            guiding[guide_ids],
            self.xl,
            self.xu,
            self.crossover_eta,
            self.crossover_rate,
            self.random_state,
        )
        return self.mutation(offspring)

    def _performance_measure(self, F: np.ndarray, ref_dirs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        # Compute assignment and Psi = cos(theta) / d on normalized objective values.
        Fn, _, _ = normalized_objectives(F)
        distances = np.linalg.norm(Fn, axis=1)
        ref_dirs = _normalize_rows(ref_dirs)
        point_norms = np.linalg.norm(Fn, axis=1, keepdims=True)
        point_unit = Fn / np.where(point_norms > 1e-12, point_norms, 1.0)
        cosine = np.clip(point_unit @ ref_dirs.T, -1.0, 1.0)
        assignment = np.argmax(cosine, axis=1)
        psi = cosine[np.arange(F.shape[0]), assignment] / np.maximum(distances, 1e-12)
        return assignment, psi

    def environmental_selection(
        self,
        X: np.ndarray,
        F: np.ndarray,
        CV: np.ndarray,
        n_survive: int,
    ) -> PopulationState:
        # Complementary environmental selection from Algorithm 2.
        X = np.asarray(X, dtype=float)
        F = np.asarray(F, dtype=float)
        CV = np.asarray(CV, dtype=float).reshape(-1)
        feasible_idx = np.flatnonzero(feasible_mask(CV))

        if feasible_idx.size == 0:
            return select_survivors_nsga2(X, F, CV, n_survive)

        feasible_X = X[feasible_idx]
        feasible_F = F[feasible_idx]
        feasible_CV = CV[feasible_idx]
        ref_dirs = self.reference_directions
        if ref_dirs is None or ref_dirs.size == 0:
            ref_dirs = sample_reference_directions(self.n_obj, n_survive, max(self.n_partitions, 1), self.random_state)
        ref_dirs = _normalize_rows(np.asarray(ref_dirs, dtype=float))
        if ref_dirs.shape[0] > int(n_survive):
            ref_dirs = ref_dirs[: int(n_survive)]

        assignment, psi = self._performance_measure(feasible_F, ref_dirs)
        occupied = np.unique(assignment).size
        threshold = max(1, int(round(self.selection_threshold_ratio * int(n_survive))))

        if occupied >= threshold:
            selected_local: list[int] = []
            for ref_idx in range(ref_dirs.shape[0]):
                candidates = np.flatnonzero(assignment == ref_idx)
                if candidates.size == 0:
                    continue
                best = candidates[np.argmax(psi[candidates])]
                selected_local.append(int(best))

            if len(selected_local) < int(n_survive):
                remaining = [idx for idx in np.argsort(psi)[::-1] if int(idx) not in selected_local]
                selected_local.extend(int(idx) for idx in remaining[: int(n_survive) - len(selected_local)])

            chosen_feasible = feasible_idx[np.asarray(selected_local[: min(int(n_survive), len(selected_local))], dtype=int)]
            if chosen_feasible.size < int(n_survive):
                infeasible_idx = np.flatnonzero(~feasible_mask(CV))
                infeasible_order = infeasible_idx[np.argsort(CV[infeasible_idx], kind="mergesort")]
                chosen = np.concatenate([chosen_feasible, infeasible_order[: int(n_survive) - chosen_feasible.size]])
            else:
                chosen = chosen_feasible
            rank, crowding = assign_rank_and_crowding(F[chosen], CV[chosen])
            return PopulationState(X=X[chosen], F=F[chosen], CV=CV[chosen], rank=rank, crowding=crowding)

        base = select_survivors_nsga2(feasible_X, feasible_F, feasible_CV, min(int(n_survive), feasible_idx.size))
        if base.X.shape[0] >= int(n_survive):
            return base

        selected_mask = stable_survivor_order(base.rank, base.crowding, base.CV)
        chosen_feasible = feasible_idx[selected_mask[: base.X.shape[0]]]
        infeasible_idx = np.flatnonzero(~feasible_mask(CV))
        infeasible_order = infeasible_idx[np.argsort(CV[infeasible_idx], kind="mergesort")]
        chosen = np.concatenate([chosen_feasible, infeasible_order[: int(n_survive) - chosen_feasible.size]])
        rank, crowding = assign_rank_and_crowding(F[chosen], CV[chosen])
        return PopulationState(X=X[chosen], F=F[chosen], CV=CV[chosen], rank=rank, crowding=crowding)

    def step(self) -> None:
        # Execute one LMOEA-DS generation with guided double reproduction.
        if self.state is None:
            raise RuntimeError("Algorithm must be initialized before step().")

        previous = self.state
        guiding, guiding_F, guiding_CV = self._sample_guiding_solutions()
        first_offspring = self._first_reproduction(guiding)
        first_F, first_CV = self.evaluate(first_offspring)

        if guiding.size:
            candidate_X = np.vstack([previous.X, first_offspring, guiding])
            candidate_F = np.vstack([previous.F, first_F, guiding_F])
            candidate_CV = np.concatenate([previous.CV, first_CV, guiding_CV])
        else:
            candidate_X = np.vstack([previous.X, first_offspring])
            candidate_F = np.vstack([previous.F, first_F])
            candidate_CV = np.concatenate([previous.CV, first_CV])

        intermediate = self.environmental_selection(candidate_X, candidate_F, candidate_CV, self.population_size)
        self.state = intermediate
        self._update_population_view()

        second_offspring = self.create_offspring()
        second_F, second_CV = self.evaluate(second_offspring)
        candidate_X = np.vstack([intermediate.X, second_offspring])
        candidate_F = np.vstack([intermediate.F, second_F])
        candidate_CV = np.concatenate([intermediate.CV, second_CV])

        self.state = self.environmental_selection(candidate_X, candidate_F, candidate_CV, self.population_size)
        self.archive = self.build_archive(self.state)
        self.n_gen += 1
        self._update_population_view()
        self._remember_state()
        self.after_generation(previous, self.state)


def make_lmoea_ds(
    problem: Any = None,
    population_size: int = 153,
    archive_size: int = 153,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.0,
    crossover_eta: float = 20.0,
    mutation_eta: float = 20.0,
    guiding_vector_count: Optional[int] = None,
    samples_per_direction: int = 30,
    selection_threshold_ratio: float = 2.0 / 3.0,
    seed: int = 1,
) -> LMOEADS:
    # Create a configured LMOEA-DS instance for the GUI registry.
    n_obj = problem_n_obj(problem) if problem is not None else 2
    effective_guides = n_obj + 10 if guiding_vector_count is None else guiding_vector_count
    return LMOEADS(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        crossover_eta=crossover_eta,
        mutation_eta=mutation_eta,
        guiding_vector_count=effective_guides,
        samples_per_direction=samples_per_direction,
        selection_threshold_ratio=selection_threshold_ratio,
        seed=seed,
    )


LMOEA_DS_DEFINITION: Dict[str, Any] = {
    "label": "LMOEA-DS",
    "factory": make_lmoea_ds,
    "form_fields": {
        "population_size": {"default": 153, "kind": "int", "minimum": 1},
        "archive_size": {"default": 153, "kind": "int", "minimum": 1},
        "crossover_rate": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.0, "kind": "float", "minimum": 0.0, "maximum": 1.0, "tooltip": "0 oznacza artykulowe ustawienie 1 / liczba_zmiennych."},
        "crossover_eta": {"default": 20.0, "kind": "float", "minimum": 1e-6},
        "mutation_eta": {"default": 20.0, "kind": "float", "minimum": 1e-6},
        "guiding_vector_count": {"default": None, "kind": "any", "tooltip": "None oznacza M + 10, gdzie M to liczba celow."},
        "samples_per_direction": {"default": 30, "kind": "int", "minimum": 1},
        "selection_threshold_ratio": {"default": 2.0 / 3.0, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Implementacja LMOEA-DS: directed sampling, double reproduction i complementary environmental selection zgodnie z TEVC 2021.",
}
LMOEA_DS_DEFINITION["form_fields"]["mutation_rate"]["tooltip"] = (
    "0 uses the paper setting 1 / number_of_variables."
)
LMOEA_DS_DEFINITION["form_fields"]["guiding_vector_count"]["tooltip"] = (
    "None means M + 10, where M is the number of objectives."
)
LMOEA_DS_DEFINITION["form_note"] = (
    "LMOEA-DS implementation: directed sampling, double reproduction, and complementary environmental selection "
    "according to TEVC 2021."
)
