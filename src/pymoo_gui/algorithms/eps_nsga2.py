# Standalone epsilon-NSGA-II implementation.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
# ------------------------------------------------------------------------------------
# Article: J. B. Kollat and P. M. Reed, "Comparing state-of-the-art evolutionary
#          multi-objective algorithms for long-term groundwater monitoring design,"
#          Advances in Water Resources, 29(6), 792-807, 2006.
# DOI: 10.1016/j.advwatres.2005.07.010
# Implementation: own Python/NumPy implementation of epsilon archiving, connected
#                 NSGA-II runs, archive injection and adaptive population sizing.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .article_algorithms_common import EpsilonArchiveAlgorithm, epsilon_box
from .research_common import (
    PopulationState,
    assign_rank_and_crowding,
    parse_epsilons,
    parse_positive_float,
    parse_positive_int,
    problem_n_obj,
    select_survivors_nsga2,
)


def _state(X: np.ndarray, F: np.ndarray, CV: np.ndarray) -> PopulationState:
    # Build a population snapshot after a connected-run restart.
    rank, crowding = assign_rank_and_crowding(F, CV)
    return PopulationState(X, F, CV, rank, crowding)


class EpsNSGAII(EpsilonArchiveAlgorithm):
    """Kollat-Reed epsilon-NSGA-II with adaptive time continuation."""

    def __init__(
        self,
        *,
        injection_rate: float = 0.25,
        window_size: int = 20,
        improvement_threshold: float = 0.10,
        minimum_population_size: int = 10,
        maximum_population_size: int = 10000,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.injection_rate = float(injection_rate)
        if not 0.0 < self.injection_rate < 1.0:
            raise ValueError("injection_rate must be in (0, 1).")
        self.window_size = parse_positive_int(window_size, "window_size")
        self.improvement_threshold = parse_positive_float(
            improvement_threshold, "improvement_threshold"
        )
        self.minimum_population_size = parse_positive_int(
            minimum_population_size, "minimum_population_size"
        )
        self.maximum_population_size = parse_positive_int(
            maximum_population_size, "maximum_population_size"
        )
        if self.minimum_population_size > self.maximum_population_size:
            raise ValueError("minimum_population_size cannot exceed maximum_population_size.")
        self.archive_box_history: list[int] = []
        self.restart_count = 0

    def after_initialize(self) -> None:
        # Record epsilon progress at the start of the first connected run.
        self.archive_box_history = [0 if self.archive is None else self.archive.X.shape[0]]
        self.restart_count = 0

    def _connected_run_restart(self) -> None:
        # Inject archive solutions and sample the remaining solutions at random.
        assert self.archive is not None
        archive_count = self.archive.X.shape[0]
        target = int(round(archive_count / self.injection_rate)) if archive_count else self.population_size
        target = int(np.clip(target, self.minimum_population_size, self.maximum_population_size))
        injected_count = min(archive_count, max(1, int(round(target * self.injection_rate))))
        injected_ids = self.random_state.choice(archive_count, size=injected_count, replace=False)
        injected = self.archive.X[injected_ids]
        random_count = max(0, target - injected_count)
        random_points = self.random_state.uniform(self.xl, self.xu, size=(random_count, self.n_var))
        candidates = np.vstack((injected, random_points))
        F, CV = self.evaluate(candidates)
        self.population_size = target
        self.state = select_survivors_nsga2(candidates, F, CV, target)
        self.archive = self.build_archive(_state(candidates, F, CV))
        self.restart_count += 1

    def after_generation(self, previous: PopulationState, current: PopulationState) -> None:
        # Start a connected run when epsilon progress falls below the article threshold.
        if self.n_gen % self.window_size != 0 or self.archive is None:
            return
        current_boxes = np.unique(epsilon_box(self.archive.F, self.epsilons), axis=0).shape[0]
        baseline = self.archive_box_history[-1]
        progress = (current_boxes - baseline) / max(1, baseline)
        self.archive_box_history.append(current_boxes)
        if progress < self.improvement_threshold:
            self._connected_run_restart()


def make_eps_nsga2(
    problem: Any,
    population_size: int = 10,
    epsilons: Any = 0.01,
    injection_rate: float = 0.25,
    window_size: int = 20,
    improvement_threshold: float = 0.10,
    minimum_population_size: int = 10,
    maximum_population_size: int = 10000,
) -> EpsNSGAII:
    # Create epsilon-NSGA-II with the settings defined by Kollat and Reed.
    size = parse_positive_int(population_size, "population_size")
    eps = np.asarray(parse_epsilons(epsilons, problem_n_obj(problem)), dtype=float)
    return EpsNSGAII(
        epsilons=eps,
        population_size=size,
        archive_size=maximum_population_size,
        crossover_rate=1.0,
        crossover_eta=15.0,
        mutation_eta=20.0,
        mutation_rate=1.0 / max(1, int(problem.n_var)),
        injection_rate=injection_rate,
        window_size=window_size,
        improvement_threshold=improvement_threshold,
        minimum_population_size=minimum_population_size,
        maximum_population_size=maximum_population_size,
    )


EPS_NSGA2_DEFINITION: Dict[str, Any] = {
    "label": "ε-NSGA-II",
    "factory": make_eps_nsga2,
    "implementation_type": "adapted_port",
    "reference": "J. B. Kollat and P. M. Reed, Advances in Water Resources 29(6), 792-807 (2006), DOI 10.1016/j.advwatres.2005.07.010",
    "verified_against": "epsilon archive, archive-injection and adaptive-population mechanism tests; no claim of statistical equivalence",
    "form_fields": {
        "population_size": {"default": 10, "kind": "int", "minimum": 2, "tooltip": "Initial connected-run population size."},
        "epsilons": {"default": 0.01, "kind": "any", "tooltip": "One objective-space resolution per objective."},
        "injection_rate": {"default": 0.25, "kind": "float", "minimum": 0.01, "maximum": 0.99},
        "window_size": {"default": 20, "kind": "int", "minimum": 1},
        "improvement_threshold": {"default": 0.10, "kind": "float", "minimum": 1e-9},
        "minimum_population_size": {"default": 10, "kind": "int", "minimum": 2},
        "maximum_population_size": {"default": 10000, "kind": "int", "minimum": 2},
    },
    "form_note": (
        "Kollat-Reed epsilon-NSGA-II with epsilon-dominance archiving, connected runs, "
        "25% archive injection and adaptive population sizing."
    ),
}
