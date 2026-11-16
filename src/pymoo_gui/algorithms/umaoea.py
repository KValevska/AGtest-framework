# Standalone micro many-objective EA (muMaOEA) integrated with the GUI runtime.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
# Basis publication: H. Peng et al., IEEE Transactions on Emerging Topics in
# Computational Intelligence 9(1), 43-56 (2025), DOI: 10.1109/TETCI.2024.3451309.

from __future__ import annotations

import math
from typing import Any, Dict

import numpy as np
from scipy.spatial.distance import cdist

from .platypus_common import termination_generations
from .research_common import (
    PopulationState,
    ResearchMOOAlgorithm,
    assign_rank_and_crowding,
    non_dominated_fronts,
    parse_positive_int,
    problem_bounds,
    problem_n_obj,
    select_survivors_nsga2,
)
from .surrogate_common import ga


def reference_weights(
    count: int,
    objectives: int,
    rng: np.random.Generator,
    pool_size: int = 5000,
) -> np.ndarray:
    # UniformlyRandomlyPoint: greedily maximize the sorted distance profile.
    if count < objectives + 1:
        raise ValueError("muMaOEA requires population_size >= number of objectives + 1")
    weights = np.vstack((np.eye(objectives), np.full((1, objectives), 1.0 / objectives)))
    pool = rng.random((max(pool_size, count), objectives))
    pool /= np.maximum(np.sum(pool, axis=1, keepdims=True), 1e-12)
    while len(weights) < count:
        profiles = np.sort(cdist(pool, weights), axis=1)
        pick = max(range(len(pool)), key=lambda index: tuple(profiles[index]))
        weights = np.vstack((weights, pool[pick]))
        pool = np.delete(pool, pick, axis=0)
    return np.maximum(weights[:count], 1e-6)


def merge_sequence(count: int, block: int) -> np.ndarray:
    # Reproduce the recursive block order used by the Merge controller.
    positions = list(range(0, count, block))
    full_blocks = count // block
    if full_blocks <= 1:
        return np.arange(count)
    order: list[int] = [0]

    def recurse(left: int, right: int) -> None:
        middle = int(math.ceil((left + right) / 2.0))
        order.append(middle)
        if middle - left > 1:
            recurse(left, middle)
        if right - middle > 1:
            recurse(middle, right)

    recurse(0, full_blocks - 1)
    order.append(full_blocks - 1)
    order = list(dict.fromkeys(order))
    sequence = [index for item in order for index in range(positions[item], positions[item] + block)]
    sequence.extend(range(full_blocks * block, count))
    return np.asarray(sequence, dtype=int)


def sde_truncation(F: np.ndarray, count: int) -> np.ndarray:
    # Shift-based density truncation used in the second controller stage.
    selected = list(range(len(F)))
    shifted = np.maximum(F[None, :, :] - F[:, None, :], 0.0)
    distances = np.linalg.norm(shifted, axis=2)
    np.fill_diagonal(distances, np.inf)
    while len(selected) > count:
        local = distances[np.ix_(selected, selected)]
        profiles = np.sort(local, axis=1)
        victim = min(range(len(selected)), key=lambda index: tuple(profiles[index]))
        selected.pop(victim)
    return np.asarray(selected, dtype=int)


class MuMaOEA(ResearchMOOAlgorithm):
    # Micro many-objective evolutionary algorithm with knowledge transfer.

    def __init__(
        self,
        population_size: int = 30,
        block: int = 5,
        reference_pool: int = 5000,
        seed: int = 1,
    ) -> None:
        super().__init__(population_size=population_size, archive_size=population_size, seed=seed)
        self.block = parse_positive_int(block, "block")
        self.reference_pool = parse_positive_int(reference_pool, "reference_pool")
        if self.block < 2 or self.block > self.population_size:
            raise ValueError("block must satisfy 2 <= block <= population_size")
        self.weights = np.empty((0, 0))
        self.neighborhood = np.empty((0, 0), dtype=int)
        self.sequence = np.empty(0, dtype=int)
        self.sequence_position = 0
        self.maximum_generations = 1

    def after_initialize(self) -> None:
        assert self.state is not None
        self.weights = reference_weights(
            self.population_size, self.n_obj, self.random_state, self.reference_pool
        )
        self._update_neighborhood()
        self.sequence = merge_sequence(self.population_size, self.block)
        archive_X = self.random_state.uniform(
            self.xl, self.xu, size=(self.population_size, self.n_var)
        )
        archive_F, archive_CV = self.evaluate(archive_X)
        self.archive = select_survivors_nsga2(
            archive_X, archive_F, archive_CV, self.population_size
        )

    def _update_neighborhood(self) -> None:
        size = min(self.block, self.population_size)
        self.neighborhood = np.argsort(cdist(self.weights, self.weights), axis=1)[:, :size]

    def _nominal_convergence(self, parent_ids: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
        assert self.state is not None
        parents = self.state.X[np.asarray(parent_ids, dtype=int)]
        values_X = parents
        values_F = self.state.F[np.asarray(parent_ids, dtype=int)]
        values_CV = self.state.CV[np.asarray(parent_ids, dtype=int)]
        for _ in range(2):
            offspring = ga(values_X[:2], self.xl, self.xu, self.random_state)
            values_F, values_CV = self.evaluate(offspring)
            values_X = offspring
        front = non_dominated_fronts(values_F)[0]
        if len(front) > 1:
            feasible = front[values_CV[front] <= 1e-12]
            choices = feasible if len(feasible) else front[np.argmin(values_CV[front]) : np.argmin(values_CV[front]) + 1]
        else:
            choices = front
        pick = int(self.random_state.choice(choices))
        return values_X[pick], values_F[pick], float(values_CV[pick])

    @staticmethod
    def _pbi(F: np.ndarray, weight: np.ndarray, theta: float, ideal: np.ndarray) -> float:
        vector = np.asarray(F) - ideal
        weight_norm = max(float(np.linalg.norm(weight)), 1e-12)
        d1 = float(vector @ weight / weight_norm)
        d2 = math.sqrt(max(0.0, float(vector @ vector) - d1 * d1))
        return d1 + float(theta) * d2

    def _controller_archive(self, active_block: np.ndarray) -> None:
        assert self.state is not None and self.archive is not None
        ratio = min(1.0, (self.n_gen + 1) / max(self.maximum_generations, 1))
        regulator = 1.0 / (1.0 + math.exp(-25.0 * (ratio - 0.3)))
        chaos = np.empty(self.population_size)
        chaos[0] = self.random_state.random()
        for index in range(1, len(chaos)):
            chaos[index] = 3.7 * chaos[index - 1] * (1.0 - chaos[index - 1])
        if float(np.mean(chaos)) > regulator:
            decisions = self.state.X.copy()
            for row in range(len(decisions)):
                a, b, c = self.random_state.integers(0, self.n_var, size=3)
                decisions[row, a] = self.state.X[row, b] + (
                    self.state.X[row, c] - self.state.X[row, b]
                ) * self.random_state.random()
                mutation = self.random_state.random(self.n_var) < 1.0 / self.n_var
                decisions[row, mutation] += self.random_state.normal(
                    0.0, (self.xu - self.xl)[mutation] / 20.0
                )
            decisions = np.clip(decisions, self.xl, self.xu)
            objectives, violations = self.evaluate(decisions)
            self.archive = select_survivors_nsga2(
                np.vstack((self.archive.X, decisions)),
                np.vstack((self.archive.F, objectives)),
                np.concatenate((self.archive.CV, violations)),
                self.population_size,
            )
        else:
            X = np.vstack((self.archive.X, self.state.X[active_block]))
            F = np.vstack((self.archive.F, self.state.F[active_block]))
            CV = np.concatenate((self.archive.CV, self.state.CV[active_block]))
            candidates = sde_truncation(F, self.population_size)
            rank, crowding = assign_rank_and_crowding(F[candidates], CV[candidates])
            self.archive = PopulationState(
                X[candidates], F[candidates], CV[candidates], rank, crowding
            )

    def step(self) -> None:
        if self.state is None:
            raise RuntimeError("Algorithm must be initialized before step().")
        if self.sequence_position >= len(self.sequence):
            self.sequence_position = 0
        active_block = self.sequence[
            self.sequence_position : self.sequence_position + self.block
        ]
        self.sequence_position += len(active_block)
        ideal = np.min(self.state.F, axis=0)
        unit_weights = self.weights / np.maximum(
            np.linalg.norm(self.weights, axis=1, keepdims=True), 1e-12
        )
        weight_cosine = np.sort(unit_weights @ unit_weights.T, axis=1)[:, ::-1]
        neighbor_angle = np.degrees(np.arccos(np.clip(weight_cosine[:, 1], -1.0, 1.0)))
        shifted = self.state.F - ideal
        shifted_unit = shifted / np.maximum(np.linalg.norm(shifted, axis=1, keepdims=True), 1e-12)
        own_cosine = np.sum(shifted_unit * unit_weights, axis=1)
        theta = 0.06 * self.n_obj * (
            neighbor_angle + np.degrees(np.arccos(np.clip(own_cosine, -1.0, 1.0)))
        )
        X, F, CV = self.state.X.copy(), self.state.F.copy(), self.state.CV.copy()
        for slot in active_block:
            pool = (
                self.neighborhood[int(slot)]
                if self.random_state.random() < 0.9
                else np.arange(self.population_size)
            )
            parent_ids = self.random_state.choice(pool, size=2, replace=False)
            child_X, child_F, child_CV = self._nominal_convergence(parent_ids)
            ideal = np.minimum(ideal, child_F)
            vector = child_F - ideal
            denominator = np.maximum(
                np.linalg.norm(self.weights, axis=1) * np.linalg.norm(vector), 1e-12
            )
            niche = int(np.argmax((self.weights @ vector) / denominator))
            if self._pbi(F[niche], self.weights[niche], theta[niche], ideal) > self._pbi(
                child_F, self.weights[niche], theta[niche], ideal
            ):
                X[niche], F[niche], CV[niche] = child_X, child_F, child_CV
        rank, crowding = assign_rank_and_crowding(F, CV)
        self.state = PopulationState(X, F, CV, rank, crowding)
        self._controller_archive(active_block)

        interval = max(1, int(math.ceil(0.1 * self.maximum_generations)))
        if (self.n_gen + 1) % interval == 0 and self.n_gen + 1 < self.maximum_generations:
            front = non_dominated_fronts(self.state.F)[0]
            nadir = np.max(self.state.F[front], axis=0)
            span = np.maximum(nadir - np.min(self.state.F, axis=0), 1e-12)
            self.weights *= span
            self.weights /= np.maximum(np.linalg.norm(self.weights, axis=1, keepdims=True), 1e-12)
            self._update_neighborhood()
        self.n_gen += 1
        self._update_population_view()
        self._remember_state()

    def gui_minimize(self, *, problem: Any, termination: Any, **kwargs: Any):
        maximum = termination_generations(termination)
        self.maximum_generations = max(1, int(maximum)) if maximum is not None else 1000
        return super().gui_minimize(problem=problem, termination=termination, **kwargs)


def make_umaoea(
    population_size: int = 30,
    block: int = 5,
    reference_pool: int = 5000,
    seed: int = 1,
) -> MuMaOEA:
    return MuMaOEA(
        population_size=population_size,
        block=block,
        reference_pool=reference_pool,
        seed=seed,
    )


UMAOEA_DEFINITION: Dict[str, Any] = {
    "label": "μMaOEA",
    "factory": make_umaoea,
    "implementation_type": "adapted_port",
    "reference": "H. Peng et al., IEEE TETCI 9(1), 43-56 (2025), DOI 10.1109/TETCI.2024.3451309",
    "verified_against": "official MATLAB control flow, merge, adaptive PBI, fuzzy controller and SDE tests; repaired source indexing and duplicate evaluation; no claim of statistical equivalence",
    "supports_constraints": False,
    "form_fields": {
        "population_size": {"default": 30, "kind": "int", "minimum": 4},
        "block": {"default": 5, "kind": "int", "minimum": 2},
        "reference_pool": {"default": 5000, "kind": "int", "minimum": 10},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": (
        "Standalone muMaOEA for bounded real-valued many-objective problems. "
        "Initialization evaluates independent population and archive designs."
    ),
}


__all__ = [
    "MuMaOEA",
    "UMAOEA_DEFINITION",
    "make_umaoea",
    "merge_sequence",
    "reference_weights",
    "sde_truncation",
]
