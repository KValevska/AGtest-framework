# SSDE implementation and GUI factory definition.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
#
# ------------------------------------------------------------------------------------
# Module: ssde.py
# Summary: self-organizing surrogate modelling, differential evolution and infill selection.
# Implementation: a SOM jointly encodes normalized decisions and objective estimates;
# DE candidates are labelled by their closest neurons and selected with Pareto rank and
# crowding before the chosen candidates receive expensive objective evaluations.
# Responsibility: adds the 2024 surrogate-assisted SSDE algorithm to GUI experiments.
# Author: Kristina Valevska, MSc Eng.
# Article reference: A. F. R. Araujo, L. R. C. Farias, and A. R. C. Goncalves,
# "Self-organizing surrogate-assisted non-dominated sorting differential
# evolution," Swarm and Evolutionary Computation, 2024, 91: 101703,
# DOI: 10.1016/j.swevo.2024.101703.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np
from scipy.spatial.distance import cdist

from .piea import SurrogateArchiveAlgorithm, nondominated_sort, operator_de
from .research_common import (
    PopulationState,
    parse_positive_float,
    parse_positive_int,
    select_survivors_nsga2,
)


def _crowding(objectives: np.ndarray, fronts: np.ndarray) -> np.ndarray:
    # Compute crowding distances independently inside every Pareto front.
    objectives = np.asarray(objectives, dtype=float)
    crowding = np.zeros(len(objectives), dtype=float)
    for front in np.unique(fronts):
        indices = np.flatnonzero(fronts == front)
        if len(indices) <= 2:
            crowding[indices] = np.inf
            continue
        for objective in range(objectives.shape[1]):
            order = indices[np.argsort(objectives[indices, objective])]
            crowding[order[[0, -1]]] = np.inf
            width = objectives[order[-1], objective] - objectives[order[0], objective]
            if width > 0.0:
                crowding[order[1:-1]] += (
                    objectives[order[2:], objective] - objectives[order[:-2], objective]
                ) / width
    return crowding


def _select(objectives: np.ndarray, count: int) -> np.ndarray:
    # Select exactly `count` solutions by Pareto rank and crowding distance.
    fronts = nondominated_sort(objectives)
    ordered_fronts = np.sort(fronts)
    last_front = ordered_fronts[int(count) - 1]
    selected = fronts < last_front
    candidates = np.flatnonzero(fronts == last_front)
    remaining = int(count - np.sum(selected))
    crowding = _crowding(objectives, fronts)
    if remaining > 0:
        selected[candidates[np.argsort(crowding[candidates])[-remaining:]]] = True
    return selected


def _train_som(
    weights: np.ndarray,
    sample_X: np.ndarray,
    sample_F: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    learning_rate: float,
    neighborhood_radius: float,
    training_epochs: int,
    rng: np.random.Generator,
) -> np.ndarray:
    # Train the article-style SOM over decisions and associated objective values.
    normalized_X = (sample_X - lower) / (upper - lower)
    samples = np.column_stack((normalized_X, sample_F))
    node_count = len(weights)
    wins = np.zeros(node_count, dtype=int)
    side = int(np.ceil(np.sqrt(node_count)))
    grid = np.asarray([(index // side, index % side) for index in range(node_count)])
    latent_distances = cdist(grid, grid)
    for epoch in range(training_epochs):
        for sample_index in rng.permutation(len(samples)):
            decay = np.exp(-wins / max(len(samples), 1))
            rates = learning_rate * decay
            radii = neighborhood_radius * decay
            winner = int(
                np.argmin(
                    np.sum(
                        (weights[:, : len(lower)] - samples[sample_index, : len(lower)]) ** 2,
                        axis=1,
                    )
                )
            )
            if wins[winner] == 0:
                weights[winner] = samples[sample_index]
            wins[winner] = min(wins[winner] + 1, epoch + 1)
            neighbors = latent_distances[winner] < radii
            influence = rates[neighbors, None] * np.exp(
                -latent_distances[winner, neighbors]
            )[:, None]
            weights[neighbors] += influence * (samples[sample_index] - weights[neighbors])
    weights[:, : len(lower)] = np.clip(weights[:, : len(lower)], 0.0, 1.0)
    return weights


class SSDE(SurrogateArchiveAlgorithm):
    # Self-organizing surrogate-assisted differential evolution.

    implementation_source = "standalone Python implementation based on Araujo et al. (2024)"

    def __init__(
        self,
        population_size: int = 40,
        num_nodes: int = 40,
        learning_rate: float = 0.2,
        neighborhood_radius: float = 40.0,
        training_epochs: int = 50,
        seed: int = 1,
    ) -> None:
        super().__init__(population_size=population_size, seed=seed)
        self.num_nodes = parse_positive_int(num_nodes, "num_nodes")
        self.learning_rate = parse_positive_float(learning_rate, "learning_rate")
        self.neighborhood_radius = parse_positive_float(
            neighborhood_radius,
            "neighborhood_radius",
        )
        self.training_epochs = parse_positive_int(training_epochs, "training_epochs")
        self.weights = np.empty((0, 0), dtype=float)
        self.population_X = np.empty((0, 0), dtype=float)
        self.population_F = np.empty((0, 0), dtype=float)
        self.population_CV = np.empty(0, dtype=float)
        self._training_X = np.empty((0, 0), dtype=float)
        self._training_F = np.empty((0, 0), dtype=float)

    def initialize(self, problem: Any) -> None:
        # Initialize the exact population and the joint decision-objective SOM.
        super().initialize(problem)
        self.population_X = self.archive_X.copy()
        self.population_F = self.archive_F.copy()
        self.population_CV = self.archive_CV.copy()
        self._training_X = self.archive_X.copy()
        self._training_F = self.archive_F.copy()
        self.weights = 0.001 * self.random_state.standard_normal(
            (self.num_nodes, self.n_var + self.population_F.shape[1])
        ) + 0.5

    def _refresh_current_population(self) -> None:
        # Publish the exact SSDE population without mixing in discarded archive points.
        self.state = select_survivors_nsga2(
            self.population_X,
            self.population_F,
            self.population_CV,
            self.population_size,
        )
        self.population_X = self.state.X.copy()
        self.population_F = self.state.F.copy()
        self.population_CV = self.state.CV.copy()
        self.pop.state = self.state

    def step(self) -> None:
        # Predict a DE generation with the SOM and exactly evaluate selected infill points.
        if len(self._training_X) >= self.population_size:
            self.weights = _train_som(
                self.weights,
                self._training_X,
                self._training_F,
                self.xl,
                self.xu,
                self.learning_rate,
                self.neighborhood_radius,
                self.training_epochs,
                self.random_state,
            )
            self._training_X = np.empty((0, self.n_var), dtype=float)
            self._training_F = np.empty((0, self.population_F.shape[1]), dtype=float)

        parent = self.random_state.integers(
            len(self.population_X),
            size=self.population_size,
        )
        donor_a = self.random_state.integers(
            len(self.population_X),
            size=self.population_size,
        )
        donor_b = self.random_state.integers(
            len(self.population_X),
            size=self.population_size,
        )
        offspring = operator_de(
            self.population_X[parent],
            self.population_X[donor_a],
            self.population_X[donor_b],
            self.xl,
            self.xu,
            self.random_state,
        )
        normalized_offspring = (offspring - self.xl) / (self.xu - self.xl)
        closest_nodes = np.argmin(
            cdist(normalized_offspring, self.weights[:, : self.n_var]),
            axis=1,
        )
        predicted_F = self.weights[closest_nodes, self.n_var :]
        selection = _select(
            np.vstack((self.population_F, predicted_F)),
            self.population_size,
        )
        old_selected = selection[: self.population_size].copy()
        new_selected = selection[self.population_size :].copy()

        if not np.any(new_selected):
            # Force one diverse trial so a GUI generation always makes measurable progress.
            forced = int(
                np.argmax(np.min(cdist(offspring, self.population_X), axis=1))
            )
            new_selected[forced] = True
            old_fronts = nondominated_sort(self.population_F)
            old_crowding = _crowding(self.population_F, old_fronts)
            removable = np.flatnonzero(old_selected)
            drop_order = np.lexsort(
                (old_crowding[removable], -old_fronts[removable])
            )
            old_selected[removable[drop_order[0]]] = False

        chosen = np.flatnonzero(new_selected)
        new_X = offspring[chosen]
        new_F, new_CV = self._evaluate(new_X)
        replace = np.flatnonzero(~old_selected)
        count = min(len(replace), len(new_X))
        self.population_X[replace[:count]] = new_X[:count]
        self.population_F[replace[:count]] = new_F[:count]
        self.population_CV[replace[:count]] = new_CV[:count]

        self.archive_X = np.vstack((self.archive_X, new_X))
        self.archive_F = np.vstack((self.archive_F, new_F))
        self.archive_CV = np.concatenate((self.archive_CV, new_CV))
        self._training_X = np.vstack((self._training_X, new_X))
        self._training_F = np.vstack((self._training_F, new_F))
        self.n_gen += 1
        self._refresh_current_population()

    def finalize_result(self) -> Any:
        # Return the current exact population through the common result adapter.
        self._refresh_current_population()
        return super().finalize_result()


def make_ssde(
    population_size: int = 40,
    num_nodes: int = 40,
    learning_rate: float = 0.2,
    neighborhood_radius: float = 40.0,
    training_epochs: int = 50,
    seed: int = 1,
) -> SSDE:
    # Create a configured SSDE instance for the GUI registry.
    return SSDE(
        population_size=population_size,
        num_nodes=num_nodes,
        learning_rate=learning_rate,
        neighborhood_radius=neighborhood_radius,
        training_epochs=training_epochs,
        seed=seed,
    )


SSDE_DEFINITION: Dict[str, Any] = {
    "label": "SSDE",
    "factory": make_ssde,
    "implementation_type": "adapted_port",
    "reference": "A. F. R. Araujo et al., Swarm and Evolutionary Computation 91, 101703 (2024), DOI 10.1016/j.swevo.2024.101703",
    "verified_against": "SOM mechanism tests and deterministic short runs; no claim of statistical equivalence",
    "form_fields": {
        "population_size": {"default": 40, "kind": "int", "minimum": 2},
        "num_nodes": {"default": 40, "kind": "int", "minimum": 1},
        "learning_rate": {"default": 0.2, "kind": "float", "minimum": 1e-8},
        "neighborhood_radius": {"default": 40.0, "kind": "float", "minimum": 1e-8},
        "training_epochs": {"default": 50, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": (
        "Self-organizing surrogate-assisted differential evolution (SSDE, 2024). "
        "Each GUI generation predicts DE offspring with a SOM and exactly evaluates "
        "the candidates retained by Pareto-rank and crowding selection."
    ),
}
