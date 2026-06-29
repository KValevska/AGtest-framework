# Classic AGE-MOEA implementation integrated with the GUI registry.

# ------------------------------------------------------------------------------------
# Module: age.py
# Summary: AGE-MOEA survival, algorithm class and GUI factory definition.
# Implementation: AGE-MOEA estimates Pareto-front geometry and uses it for survival.
# Responsibility: adds the classic adaptive-geometry AGE optimizer.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
from pymoo.algorithms.base.genetic import GeneticAlgorithm
from pymoo.algorithms.moo.nsga2 import binary_tournament
from pymoo.core.survival import Survival
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.selection.tournament import TournamentSelection
from pymoo.termination.default import DefaultMultiObjectiveTermination
from pymoo.util.display.multi import MultiObjectiveOutput
from pymoo.util.misc import has_feasible
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting


def _parse_positive_int(value: Any, field_name: str) -> int:
    # Parse a positive integer AGE-MOEA configuration value.
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def _parse_optional_positive_int(value: Any, field_name: str) -> Optional[int]:
    # Parse an optional positive integer and preserve `None` for pymoo defaults.
    if value is None:
        return None
    return _parse_positive_int(value, field_name)


def point_2_line_distance(points: np.ndarray, start: np.ndarray, end: np.ndarray) -> np.ndarray:
    # Compute squared distances from points to a line in objective space.
    points = np.asarray(points, dtype=float)
    start = np.asarray(start, dtype=float)
    end = np.asarray(end, dtype=float)
    direction = end - start
    denom = np.dot(direction, direction)
    if denom == 0.0:
        return np.sum((points - start) ** 2, axis=1)
    projection = np.dot(points - start, direction) / denom
    return np.sum((points - start - projection[:, None] * direction) ** 2, axis=1)


def find_corner_solutions(front: np.ndarray) -> np.ndarray:
    # Return indices of extreme solutions used to normalize the current front.
    front = np.asarray(front, dtype=float)
    n_points, n_obj = front.shape
    if n_points <= n_obj:
        return np.arange(n_points)

    axes = 1e-6 + np.eye(n_obj)
    indexes = np.zeros(n_obj, dtype=int)
    selected = np.zeros(n_points, dtype=bool)
    for i, axis in enumerate(axes):
        distances = point_2_line_distance(front, np.zeros(n_obj), axis)
        distances[selected] = np.inf
        index = int(np.argmin(distances))
        indexes[i] = index
        selected[index] = True
    return indexes


def normalize(front: np.ndarray, extreme: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # Normalize a front using the hyperplane defined by its extreme points.
    front = np.asarray(front, dtype=float)
    _, n_obj = front.shape

    if len(extreme) != len(np.unique(extreme)):
        normalization = np.max(front, axis=0)
        normalization[normalization == 0.0] = 1.0
        return front / normalization, normalization

    try:
        hyperplane = np.linalg.solve(front[extreme], np.ones(n_obj))
        if np.any(np.isnan(hyperplane)) or np.any(np.isinf(hyperplane)) or np.any(hyperplane <= 0.0):
            normalization = np.max(front, axis=0)
        else:
            normalization = 1.0 / hyperplane
            if np.any(np.isnan(normalization)) or np.any(np.isinf(normalization)):
                normalization = np.max(front, axis=0)
    except np.linalg.LinAlgError:
        normalization = np.max(front, axis=0)

    normalization[normalization == 0.0] = 1.0
    return front / normalization, normalization


class AGEMOEASurvival(Survival):
    # Environmental selection for classic AGE-MOEA.

    def __init__(self) -> None:
        # Initialize non-dominated sorting used by AGE-MOEA survival.
        super().__init__(filter_infeasible=True)
        self.nds = NonDominatedSorting()

    def _do(self, problem, pop, *args, n_survive=None, **kwargs):
        # Select survivors by rank and adaptive-geometry crowding score.
        F = np.asarray(pop.get("F"), dtype=float)
        n_survive = len(pop) if n_survive is None else int(n_survive)
        fronts = self.nds.do(F, n_stop_if_ranked=n_survive)

        max_rank = np.iinfo(int).max
        front_no = np.full(F.shape[0], max_rank, dtype=int)
        for rank, front in enumerate(fronts):
            front_no[front] = rank
        pop.set("rank", front_no)

        last_front_rank = int(np.max(front_no[front_no != max_rank]))
        selected = front_no < last_front_rank
        crowding = np.zeros(F.shape[0], dtype=float)

        front1 = F[front_no == 0]
        ideal_point = np.min(front1, axis=0)
        crowding[front_no == 0], p_norm, normalization = self.survival_score(front1, ideal_point)

        for rank in range(1, last_front_rank):
            front = F[front_no == rank] / normalization
            distances = self.minkowski_distances(front, ideal_point[None, :], p=p_norm).squeeze()
            distances[distances < 1e-8] = 1e-8
            crowding[front_no == rank] = 1.0 / distances

        last = np.arange(selected.shape[0])[front_no == last_front_rank]
        order = np.argsort(crowding[last])[::-1]
        selected[last[order[: n_survive - int(np.sum(selected))]]] = True

        pop.set("crowding", crowding)
        return pop[selected]

    def survival_score(self, front: np.ndarray, ideal_point: np.ndarray) -> tuple[np.ndarray, float, np.ndarray]:
        # Compute AGE-MOEA crowding values, estimated p-norm and normalization.
        front = np.round(np.asarray(front, dtype=float).copy(), 12)
        n_points, n_obj = front.shape
        crowding = np.zeros(n_points, dtype=float)

        if n_points < n_obj:
            normalization = np.max(front, axis=0)
            normalization[normalization == 0.0] = 1.0
            return crowding, 1.0, normalization

        front = front - ideal_point
        extreme = find_corner_solutions(front)
        front, normalization = normalize(front, extreme)

        crowding[extreme] = np.inf
        selected = np.full(n_points, False, dtype=bool)
        selected[extreme] = True

        p_norm = self.compute_geometry(front, extreme, n_obj)
        norms = np.linalg.norm(front, p_norm, axis=1)
        norms[norms < 1e-8] = 1.0

        distances = self.pairwise_distances(front, p_norm)
        distances[distances < 1e-8] = 1e-8
        distances = distances / norms[:, None]

        remaining = list(np.arange(n_points)[~selected])
        neighbors = 2
        for _ in range(n_points - int(np.sum(selected))):
            mesh = np.meshgrid(np.arange(selected.shape[0])[selected], remaining, copy=False, sparse=False)
            candidate_distances = distances[tuple(mesh)]
            if candidate_distances.shape[1] > 1:
                nearest = np.argpartition(candidate_distances, neighbors - 1, axis=1)[:, :neighbors]
                summed = np.sum(np.take_along_axis(candidate_distances, nearest, axis=1), axis=1)
                local_idx = int(np.argmax(summed))
                score = float(summed[local_idx])
            else:
                local_idx = int(candidate_distances[:, 0].argmax())
                score = float(candidate_distances[local_idx, 0])

            best = remaining.pop(local_idx)
            selected[best] = True
            crowding[best] = score

        return crowding, p_norm, normalization

    @staticmethod
    def compute_geometry(front: np.ndarray, extreme: np.ndarray, n_obj: int) -> float:
        # Estimate the Minkowski p-norm that best matches the first front geometry.
        distances = point_2_line_distance(front, np.zeros(n_obj), np.ones(n_obj))
        distances[extreme] = np.inf
        index = int(np.argmin(distances))
        mean_value = float(np.mean(front[index, :]))

        if mean_value <= 0.0:
            return 1.0
        p_norm = np.log(n_obj) / np.log(1.0 / mean_value)
        if np.isnan(p_norm) or p_norm <= 0.1:
            return 1.0
        if p_norm > 20.0:
            return 20.0
        return float(p_norm)

    @staticmethod
    def pairwise_distances(front: np.ndarray, p: float) -> np.ndarray:
        # Compute pairwise Minkowski distances inside one front.
        n_points = np.shape(front)[0]
        distances = np.zeros((n_points, n_points), dtype=float)
        for i in range(n_points):
            distances[i] = np.sum(np.abs(front[i] - front) ** p, axis=1) ** (1.0 / p)
        return distances

    @staticmethod
    def minkowski_distances(A: np.ndarray, B: np.ndarray, p: float) -> np.ndarray:
        # Compute Minkowski distances between two objective matrices.
        A = np.asarray(A, dtype=float)
        B = np.asarray(B, dtype=float)
        distances = np.zeros((A.shape[0], B.shape[0]), dtype=float)
        for i in range(A.shape[0]):
            for j in range(B.shape[0]):
                distances[i, j] = np.sum(np.abs(A[i] - B[j]) ** p) ** (1.0 / p)
        return distances


class AGE(GeneticAlgorithm):
    # Classic adaptive-geometry AGE-MOEA algorithm.

    def __init__(
        self,
        pop_size: int = 100,
        sampling=FloatRandomSampling(),
        selection=TournamentSelection(func_comp=binary_tournament),
        crossover=SBX(eta=15, prob=0.9),
        mutation=PM(eta=20),
        eliminate_duplicates: bool = True,
        n_offsprings: Optional[int] = None,
        output=MultiObjectiveOutput(),
        **kwargs,
    ):
        # Configure AGE-MOEA with pymoo-compatible genetic operators.
        super().__init__(
            pop_size=_parse_positive_int(pop_size, "pop_size"),
            sampling=sampling,
            selection=selection,
            crossover=crossover,
            mutation=mutation,
            survival=AGEMOEASurvival(),
            eliminate_duplicates=eliminate_duplicates,
            n_offsprings=_parse_optional_positive_int(n_offsprings, "n_offsprings"),
            output=output,
            advance_after_initial_infill=True,
            **kwargs,
        )
        self.default_termination = DefaultMultiObjectiveTermination()
        self.tournament_type = "comp_by_rank_and_crowding"

    def _set_optimum(self, **kwargs):
        # Expose feasible rank-zero solutions as the current optimum.
        if not has_feasible(self.pop):
            self.opt = self.pop[[np.argmin(self.pop.get("CV"))]]
        else:
            self.opt = self.pop[self.pop.get("rank") == 0]


def make_age(pop_size: int = 100, n_offsprings: Optional[int] = None) -> AGE:
    # Create a configured classic AGE-MOEA algorithm for the GUI registry.
    return AGE(
        pop_size=_parse_positive_int(pop_size, "pop_size"),
        n_offsprings=_parse_optional_positive_int(n_offsprings, "n_offsprings"),
    )


AGE_DEFINITION: Dict[str, Any] = {
    "label": "AGE-MOEA",
    "factory": make_age,
    "form_fields": {
        "pop_size": {
            "default": 100,
            "kind": "int",
            "minimum": 1,
            "tooltip": "Rozmiar populacji AGE-MOEA.",
        },
        "n_offsprings": {
            "default": None,
            "kind": "any",
            "tooltip": "Liczba potomkow; None oznacza domyslna liczbe rowna pop_size.",
        },
    },
    "form_note": "Klasyczny AGE-MOEA: non-dominated sorting i adaptacyjna geometria frontu.",
}
AGE_DEFINITION["form_fields"]["pop_size"]["tooltip"] = "Population size for AGE-MOEA."
AGE_DEFINITION["form_fields"]["n_offsprings"]["tooltip"] = (
    "Number of offspring; None uses the default value equal to pop_size."
)
AGE_DEFINITION["form_note"] = "Classic AGE-MOEA with non-dominated sorting and adaptive front geometry."
