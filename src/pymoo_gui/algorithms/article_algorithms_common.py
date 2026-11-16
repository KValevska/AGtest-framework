# Shared mechanisms for the standalone implementations of classical MOEAs.
# Provenance: AGtest-framework infrastructure implementing mechanisms from the cited algorithm papers.

# ------------------------------------------------------------------------------------
# Module: article_algorithms_common.py
# Summary: Reference-direction, decomposition, epsilon-archive and SPEA2 mechanisms.
# Implementation: Original Python/NumPy implementation of equations and procedures
#                 published in the articles cited by the individual algorithm modules.
# Responsibility: contains no ready-made optimization algorithm from pymoo or Platypus.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Optional

import numpy as np

from .research_common import (
    FEASIBILITY_TOL,
    PopulationState,
    ResearchMOOAlgorithm,
    assign_rank_and_crowding,
    crowding_distance,
    feasible_mask,
    non_dominated_fronts,
    polynomial_mutation,
    sbx_crossover,
    select_survivors_nsga2,
)


def _state(X: np.ndarray, F: np.ndarray, CV: np.ndarray) -> PopulationState:
    rank, crowding = assign_rank_and_crowding(F, CV)
    return PopulationState(np.asarray(X), np.asarray(F), np.asarray(CV), rank, crowding)


def nsga3_normalize(F: np.ndarray) -> np.ndarray:
    # Deb-Jain normalization: ideal point, ASF extreme points and hyperplane intercepts.
    F = np.asarray(F, dtype=float)
    shifted = F - np.min(F, axis=0)
    n_obj = F.shape[1]
    extreme = []
    for axis in range(n_obj):
        weights = np.full(n_obj, 1e-6)
        weights[axis] = 1.0
        extreme.append(int(np.argmin(np.max(shifted / weights, axis=1))))
    nadir = np.max(shifted, axis=0)
    try:
        plane = np.linalg.solve(shifted[np.asarray(extreme)], np.ones(n_obj))
        intercepts = 1.0 / plane
        if not np.all(np.isfinite(intercepts)) or np.any(intercepts <= 1e-12):
            intercepts = nadir
    except np.linalg.LinAlgError:
        intercepts = nadir
    intercepts = np.where(intercepts > 1e-12, intercepts, 1.0)
    return shifted / intercepts


def associate(F: np.ndarray, ref_dirs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # Associate normalized objective vectors with reference lines by perpendicular distance.
    Y = nsga3_normalize(F)
    W = np.asarray(ref_dirs, dtype=float)
    W = W / np.maximum(np.linalg.norm(W, axis=1, keepdims=True), 1e-15)
    projections = Y @ W.T
    distances = np.linalg.norm(Y[:, None, :] - projections[:, :, None] * W[None, :, :], axis=2)
    niches = np.argmin(distances, axis=1)
    return niches, distances[np.arange(Y.shape[0]), niches]


def nsga3_survival(
    X: np.ndarray,
    F: np.ndarray,
    CV: np.ndarray,
    n_survive: int,
    ref_dirs: np.ndarray,
    rng: np.random.Generator,
) -> PopulationState:
    # Feasible-first NSGA-III environmental selection and reference-line niching.
    feasible = np.flatnonzero(feasible_mask(CV))
    if feasible.size < n_survive:
        chosen = feasible.tolist()
        infeasible = np.flatnonzero(~feasible_mask(CV))
        chosen.extend(infeasible[np.argsort(CV[infeasible])[: n_survive - len(chosen)]].tolist())
        ids = np.asarray(chosen, dtype=int)
        return _state(X[ids], F[ids], CV[ids])

    fronts = non_dominated_fronts(F[feasible])
    selected: list[int] = []
    split = np.empty(0, dtype=int)
    for front in fronts:
        absolute = feasible[front]
        if len(selected) + absolute.size <= n_survive:
            selected.extend(absolute.tolist())
        else:
            split = absolute
            break
    if len(selected) == n_survive:
        ids = np.asarray(selected, dtype=int)
        return _state(X[ids], F[ids], CV[ids])

    pool = np.asarray(selected + split.tolist(), dtype=int)
    niches, distances = associate(F[pool], ref_dirs)
    n_fixed = len(selected)
    rho = np.bincount(niches[:n_fixed], minlength=ref_dirs.shape[0]).astype(int)
    candidates = list(range(n_fixed, pool.size))
    while len(selected) < n_survive and candidates:
        available_niches = np.unique(niches[candidates])
        min_rho = np.min(rho[available_niches])
        niche = int(rng.choice(available_niches[rho[available_niches] == min_rho]))
        local = [idx for idx in candidates if niches[idx] == niche]
        if rho[niche] == 0:
            pick = min(local, key=lambda idx: distances[idx])
        else:
            pick = int(rng.choice(local))
        selected.append(int(pool[pick]))
        candidates.remove(pick)
        rho[niche] += 1
    ids = np.asarray(selected[:n_survive], dtype=int)
    return _state(X[ids], F[ids], CV[ids])


class NSGA3Algorithm(ResearchMOOAlgorithm):
    # Standalone NSGA-III loop using the Deb-Jain reference-point survival procedure.

    def environmental_selection(self, X, F, CV, n_survive):
        assert self.reference_directions is not None
        return nsga3_survival(X, F, CV, n_survive, self.reference_directions, self.random_state)


class MOEADAlgorithm(ResearchMOOAlgorithm):
    # Standalone MOEA/D using Tchebycheff decomposition and neighborhood replacement.

    def __init__(self, prob_neighbor_mating: float = 0.7, max_replacements: int = 2, **kwargs):
        super().__init__(**kwargs)
        self.prob_neighbor_mating = float(prob_neighbor_mating)
        self.max_replacements = int(max_replacements)
        self.neighborhood = np.empty((0, 0), dtype=int)
        self.ideal = np.empty(0, dtype=float)

    def after_initialize(self) -> None:
        assert self.state is not None and self.reference_directions is not None
        weights = self.reference_directions[: self.population_size]
        distances = np.linalg.norm(weights[:, None, :] - weights[None, :, :], axis=2)
        size = min(max(2, self.n_neighbors), self.population_size)
        self.neighborhood = np.argsort(distances, axis=1)[:, :size]
        self.ideal = np.min(self.state.F, axis=0)

    def _scalar(self, F: np.ndarray, weights: np.ndarray) -> np.ndarray:
        return np.max(np.maximum(weights, 1e-6) * np.abs(F - self.ideal), axis=1)

    def build_archive(self, state: PopulationState) -> PopulationState:
        # Maintain the external nondominated population EP from the MOEA/D framework.
        if self.archive is None:
            X, F, CV = state.X, state.F, state.CV
        else:
            X = np.vstack((self.archive.X, state.X))
            F = np.vstack((self.archive.F, state.F))
            CV = np.concatenate((self.archive.CV, state.CV))
        feasible = np.flatnonzero(feasible_mask(CV))
        if feasible.size:
            front = non_dominated_fronts(F[feasible])[0]
            ids = feasible[front]
        else:
            best = np.min(CV)
            ids = np.flatnonzero(np.isclose(CV, best))
        _, unique = np.unique(np.round(np.column_stack((X[ids], F[ids])), 14), axis=0, return_index=True)
        ids = ids[np.sort(unique)]
        if ids.size > self.archive_size:
            distance = crowding_distance(F[ids])
            ids = ids[np.argsort(-distance, kind="mergesort")[: self.archive_size]]
        return _state(X[ids], F[ids], CV[ids])

    def replacement_allowed(self, child_f, child_cv, target_f, target_cv, weights) -> bool:
        # Deb feasibility comparison followed by the decomposition scalar value.
        if child_cv < target_cv - FEASIBILITY_TOL:
            return True
        if abs(child_cv - target_cv) > FEASIBILITY_TOL:
            return False
        return self._scalar(child_f[None, :], weights[None, :])[0] <= self._scalar(
            target_f[None, :], weights[None, :]
        )[0]

    def generate_child(self, subproblem: int, pool: np.ndarray) -> np.ndarray:
        # Default MOEA/D reproduction with SBX and polynomial mutation.
        replace = pool.size < 2
        parents = self.random_state.choice(pool, size=2, replace=replace).reshape(1, 2)
        child = sbx_crossover(
            self.state.X, parents, self.xl, self.xu, self.crossover_eta,
            self.crossover_rate, self.random_state,
        )
        return polynomial_mutation(
            child, self.xl, self.xu, self.mutation_eta,
            self.mutation_rate, self.random_state,
        )

    def step(self) -> None:
        if self.state is None or self.reference_directions is None:
            raise RuntimeError("Algorithm must be initialized before step().")
        previous = _state(self.state.X.copy(), self.state.F.copy(), self.state.CV.copy())
        order = self.random_state.permutation(self.population_size)
        all_ids = np.arange(self.population_size)
        for subproblem in order:
            pool = self.neighborhood[subproblem] if self.random_state.random() < self.prob_neighbor_mating else all_ids
            child = self.generate_child(int(subproblem), pool)
            child_F, child_CV = self.evaluate(child)
            self.ideal = np.minimum(self.ideal, child_F[0])
            # Algorithm 1 uses the same set S for mating and replacement: the
            # neighborhood with probability delta, otherwise the full population.
            targets = np.asarray(pool, dtype=int).copy()
            self.random_state.shuffle(targets)
            replacements = 0
            for target in targets:
                weights = self.reference_directions[target]
                if self.replacement_allowed(
                    child_F[0], child_CV[0], self.state.F[target], self.state.CV[target], weights
                ):
                    self.state.X[target] = child[0]
                    self.state.F[target] = child_F[0]
                    self.state.CV[target] = child_CV[0]
                    replacements += 1
                    if replacements >= self.max_replacements:
                        break
        self.state = _state(self.state.X, self.state.F, self.state.CV)
        self.archive = self.build_archive(self.state)
        self.n_gen += 1
        self._update_population_view()
        self._remember_state()
        self.after_generation(previous, self.state)


def epsilon_box(F: np.ndarray, epsilons: np.ndarray) -> np.ndarray:
    return np.floor(np.asarray(F, dtype=float) / np.asarray(epsilons, dtype=float)).astype(np.int64)


def epsilon_archive_indices(F: np.ndarray, CV: np.ndarray, epsilons: np.ndarray) -> np.ndarray:
    # Laumanns-Deb epsilon-box archive: one representative per nondominated box.
    order = np.argsort(CV, kind="mergesort")
    archive: list[int] = []
    boxes: list[np.ndarray] = []
    for idx in order:
        if CV[idx] > FEASIBILITY_TOL and archive and CV[archive[0]] <= FEASIBILITY_TOL:
            continue
        box = epsilon_box(F[idx : idx + 1], epsilons)[0]
        dominated = [j for j, old in enumerate(boxes) if np.all(box <= old) and np.any(box < old)]
        if any(np.all(old <= box) and np.any(old < box) for old in boxes):
            continue
        same = next((j for j, old in enumerate(boxes) if np.array_equal(old, box)), None)
        if same is not None:
            corner = box.astype(float) * epsilons
            if np.linalg.norm(F[idx] - corner) < np.linalg.norm(F[archive[same]] - corner):
                archive[same] = int(idx)
            continue
        for j in reversed(dominated):
            del archive[j]
            del boxes[j]
        archive.append(int(idx))
        boxes.append(box)
    return np.asarray(archive, dtype=int)


class EpsilonArchiveAlgorithm(ResearchMOOAlgorithm):
    # Generational NSGA-II with an external epsilon-dominance archive.

    def __init__(self, epsilons: np.ndarray, steady_state: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.epsilons = np.asarray(epsilons, dtype=float)
        self.steady_state = bool(steady_state)

    def build_archive(self, state: PopulationState) -> PopulationState:
        if self.archive is None:
            X, F, CV = state.X, state.F, state.CV
        else:
            X = np.vstack([self.archive.X, state.X])
            F = np.vstack([self.archive.F, state.F])
            CV = np.concatenate([self.archive.CV, state.CV])
        ids = epsilon_archive_indices(F, CV, self.epsilons)
        if ids.size > self.archive_size:
            trimmed = select_survivors_nsga2(X[ids], F[ids], CV[ids], self.archive_size)
            return trimmed
        return _state(X[ids], F[ids], CV[ids])

    def step(self) -> None:
        if not self.steady_state:
            return super().step()
        if self.state is None:
            raise RuntimeError("Algorithm must be initialized before step().")
        previous = _state(self.state.X.copy(), self.state.F.copy(), self.state.CV.copy())
        for _ in range(self.population_size):
            child = self.create_offspring()
            child_F, child_CV = self.evaluate(child)
            X = np.vstack([self.state.X, child])
            F = np.vstack([self.state.F, child_F])
            CV = np.concatenate([self.state.CV, child_CV])
            self.state = select_survivors_nsga2(X, F, CV, self.population_size)
            self.archive = self.build_archive(_state(child, child_F, child_CV))
        self.n_gen += 1
        self._update_population_view()
        self._remember_state()
        self.after_generation(previous, self.state)


def spea2_fitness(F: np.ndarray, CV: np.ndarray) -> np.ndarray:
    # SPEA2 strength, raw fitness and kth-nearest-neighbor density.
    F = np.asarray(F, dtype=float)
    n = F.shape[0]
    dominates = np.all(F[:, None, :] <= F[None, :, :], axis=2) & np.any(F[:, None, :] < F[None, :, :], axis=2)
    feasible = feasible_mask(CV)
    dominates |= feasible[:, None] & ~feasible[None, :]
    strength = np.sum(dominates, axis=1)
    raw = dominates.T @ strength
    normalized = (F - np.min(F, axis=0)) / np.maximum(np.ptp(F, axis=0), 1e-15)
    distances = np.linalg.norm(normalized[:, None, :] - normalized[None, :, :], axis=2)
    np.fill_diagonal(distances, np.inf)
    k = min(max(1, int(np.sqrt(n))), max(1, n - 1))
    sigma = np.partition(distances, k - 1, axis=1)[:, k - 1]
    return raw + 1.0 / (sigma + 2.0) + np.maximum(CV, 0.0) * 1e6


def spea2_survival(X, F, CV, n_survive) -> PopulationState:
    fitness = spea2_fitness(F, CV)
    chosen = np.flatnonzero(fitness < 1.0).tolist()
    if len(chosen) < n_survive:
        remaining = [i for i in np.argsort(fitness) if i not in chosen]
        chosen.extend(remaining[: n_survive - len(chosen)])
    while len(chosen) > n_survive:
        values = F[np.asarray(chosen)]
        values = (values - np.min(values, axis=0)) / np.maximum(np.ptp(values, axis=0), 1e-15)
        D = np.linalg.norm(values[:, None, :] - values[None, :, :], axis=2)
        np.fill_diagonal(D, np.inf)
        lexicographic = np.sort(D, axis=1)
        remove = min(range(len(chosen)), key=lambda i: tuple(lexicographic[i]))
        chosen.pop(remove)
    ids = np.asarray(chosen, dtype=int)
    state = _state(X[ids], F[ids], CV[ids])
    state.crowding = -fitness[ids]
    return state


class SPEA2Algorithm(ResearchMOOAlgorithm):
    def environmental_selection(self, X, F, CV, n_survive):
        return spea2_survival(X, F, CV, n_survive)

