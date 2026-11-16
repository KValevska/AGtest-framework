# Standalone reference-point-based R-NSGA-III implementation.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
# ------------------------------------------------------------------------------------
# Article: Y. Vesikar, K. Deb, J. Blank, "Reference Point Based NSGA-III for
#          Preferred Solutions", IEEE SSCI, 2018.
# DOI: 10.1109/SSCI.2018.8628819
# Implementation: own Python/NumPy implementation based on the article.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------
from typing import Any, Dict

import numpy as np

from .article_algorithms_common import NSGA3Algorithm, nsga3_survival
from .research_common import das_dennis_reference_directions, parse_positive_int, problem_n_obj


DEFAULT_REF_POINTS = np.array([[0.3, 0.4], [0.8, 0.5]], dtype=float)


def _points(value: Any, n_obj: int) -> np.ndarray:
    points = np.asarray(value, dtype=float)
    if points.ndim == 1:
        points = points.reshape(1, -1)
    if points.ndim != 2 or points.shape[0] == 0 or points.shape[1] != n_obj:
        raise ValueError(f"ref_points must have shape (n, {n_obj}).")
    if not np.isfinite(points).all():
        raise ValueError("ref_points must contain finite values.")
    return points


def _uniform_directions(n_obj: int, count: int) -> np.ndarray:
    # Generate the requested number of deterministic Das-Dennis aspiration directions.
    partitions = 1
    directions = das_dennis_reference_directions(n_obj, partitions)
    while directions.shape[0] < count:
        partitions += 1
        directions = das_dennis_reference_directions(n_obj, partitions)
    if directions.shape[0] > count:
        take = np.linspace(0, directions.shape[0] - 1, count).round().astype(int)
        directions = directions[take]
    return directions


def _default_ref_points(n_obj: int) -> np.ndarray:
    # Preserve the documented two-objective defaults and use one aspiration
    # point per objective for higher-dimensional problems.
    if int(n_obj) == 2:
        return DEFAULT_REF_POINTS.copy()
    return np.eye(int(n_obj), dtype=float)


def _line_plane_intersection(point: np.ndarray) -> np.ndarray:
    # Project the aspiration ray from the origin onto sum(f_i)=1.
    total = float(np.sum(point))
    if abs(total) <= 1e-12:
        return np.full(point.size, 1.0 / point.size)
    return point / total


def reference_directions_from_points(
    unit_points: np.ndarray,
    aspiration_directions: np.ndarray,
    mu: float,
) -> np.ndarray:
    # Shrink the simplex lattice and translate it around every projected aspiration point.
    n_obj = unit_points.shape[1]
    shrunken = float(mu) * np.asarray(aspiration_directions, dtype=float)
    centroid = np.mean(shrunken, axis=0)
    groups = []
    for point in unit_points:
        projected = _line_plane_intersection(point)
        local = shrunken + (projected - centroid)
        local = np.maximum(local, 0.0)
        row_sum = np.sum(local, axis=1, keepdims=True)
        local = np.divide(local, row_sum, out=np.full_like(local, 1.0 / n_obj), where=row_sum > 1e-15)
        groups.append(local)
    return np.vstack(groups + [np.eye(n_obj)])


class RNSGA3(NSGA3Algorithm):
    """R-NSGA-III with dynamically normalized aspiration-point reference directions."""

    def __init__(self, ref_points: np.ndarray, aspiration_directions: np.ndarray, mu: float, **kwargs):
        super().__init__(**kwargs)
        self.ref_points = np.asarray(ref_points, dtype=float)
        self.aspiration_directions = np.asarray(aspiration_directions, dtype=float)
        self.mu = float(mu)

    def environmental_selection(self, X, F, CV, n_survive):
        # Normalize aspiration points with the current objective range, then perform NSGA-III niching.
        combined = np.vstack((F, self.ref_points))
        ideal = np.min(combined, axis=0)
        nadir = np.max(combined, axis=0)
        span = np.where(nadir > ideal, nadir - ideal, 1.0)
        unit_points = (self.ref_points - ideal) / span
        self.reference_directions = reference_directions_from_points(
            unit_points, self.aspiration_directions, self.mu
        )
        return nsga3_survival(X, F, CV, n_survive, self.reference_directions, self.random_state)


def make_rnsga3(
    problem: Any,
    ref_points: Any = None,
    pop_per_ref_point: int = 50,
    mu: float = 0.1,
) -> RNSGA3:
    n_obj = problem_n_obj(problem)
    points = _points(_default_ref_points(n_obj) if ref_points is None else ref_points, n_obj)
    count = parse_positive_int(pop_per_ref_point, "pop_per_ref_point")
    mu = float(mu)
    if not 0.0 <= mu <= 1.0:
        raise ValueError("mu must be in [0, 1].")
    aspiration_directions = _uniform_directions(n_obj, count)
    population_size = points.shape[0] * aspiration_directions.shape[0] + n_obj
    return RNSGA3(
        ref_points=points,
        aspiration_directions=aspiration_directions,
        mu=mu,
        population_size=population_size,
        archive_size=population_size,
        reference_directions=np.eye(n_obj),
        mutation_rate=1.0 / max(1, int(problem.n_var)),
    )


RNSGA3_DEFINITION: Dict[str, Any] = {
    "label": "R-NSGA-III",
    "factory": make_rnsga3,
    "form_fields": {
        "ref_points": {"default": None, "kind": "any", "tooltip": "Aspiration points; leave empty to generate defaults matching the objective count."},
        "pop_per_ref_point": {"default": 50, "kind": "int", "minimum": 1, "tooltip": "Reference directions per aspiration point."},
        "mu": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0, "tooltip": "Simplex-lattice shrinkage factor."},
    },
    "form_note": "Own Python implementation of R-NSGA-III (DOI: 10.1109/SSCI.2018.8628819).",
}
