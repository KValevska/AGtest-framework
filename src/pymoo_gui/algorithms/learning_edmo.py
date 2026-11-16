# Standalone learning-across-problems EDMO implementation.
# Provenance: AGtest-framework standalone implementation; not imported from pymoo or Platypus.
# ------------------------------------------------------------------------------------
# Article: Y. Xie, Q. Zhao, W. Zhou, and Z. Zhu, "Evolutionary Dynamic
#          Multiobjective Optimization With Learning Across Problems,"
#          IEEE Transactions on Evolutionary Computation, 29(5), 2025.
# DOI: 10.1109/TEVC.2025.3596468
# Implementation: own Python/NumPy implementation of dynamic feature extraction,
#                 task-specific solution classification and centralized learning.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Dict

import numpy as np

from .research_common import (
    PopulationState,
    ResearchMOOAlgorithm,
    normalized_objectives,
    parse_positive_float,
    parse_positive_int,
    parse_probability,
    project_to_bounds,
)


@dataclass
class ProblemKnowledge:
    # Store dimension-free dynamic features and a normalized elite shape.
    task_features: np.ndarray
    elite_profile: np.ndarray
    shift_profile: np.ndarray


class CentralizedClassifier:
    # Small shared logistic model trained by task-specific elite labels.

    def __init__(self, feature_count: int = 10) -> None:
        self.weights = np.zeros(feature_count, dtype=float)
        self.bias = 0.0
        self.updates = 0

    def predict(self, features: np.ndarray) -> np.ndarray:
        logits = np.clip(np.asarray(features) @ self.weights + self.bias, -40.0, 40.0)
        return 1.0 / (1.0 + np.exp(-logits))

    def fit(self, features: np.ndarray, labels: np.ndarray, rate: float, epochs: int) -> None:
        X = np.asarray(features, dtype=float)
        y = np.asarray(labels, dtype=float)
        if X.shape[0] == 0 or np.all(y == y[0]):
            return
        for _ in range(epochs):
            prediction = self.predict(X)
            error = prediction - y
            self.weights -= rate * (X.T @ error / X.shape[0] + 1e-4 * self.weights)
            self.bias -= rate * float(np.mean(error))
        self.updates += 1


class LearningAcrossProblemsEDMO(ResearchMOOAlgorithm):
    """Centralized cross-problem learning strategy for dynamic MOO."""

    CENTRAL_MODEL: ClassVar[CentralizedClassifier] = CentralizedClassifier()
    KNOWLEDGE_BASE: ClassVar[list[ProblemKnowledge]] = []

    def __init__(
        self,
        *,
        transfer_fraction: float = 0.2,
        candidate_multiplier: int = 5,
        learning_rate: float = 0.05,
        learning_epochs: int = 20,
        knowledge_size: int = 32,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.transfer_fraction = parse_probability(transfer_fraction, "transfer_fraction")
        self.candidate_multiplier = parse_positive_int(candidate_multiplier, "candidate_multiplier")
        self.learning_rate = parse_positive_float(learning_rate, "learning_rate")
        self.learning_epochs = parse_positive_int(learning_epochs, "learning_epochs")
        self.knowledge_size = parse_positive_int(knowledge_size, "knowledge_size")
        self.previous_elite_center: np.ndarray | None = None
        self.current_task_features = np.zeros(4)
        self.classification_updates = 0

    def _normalized(self, X: np.ndarray) -> np.ndarray:
        return (np.asarray(X) - self.xl) / np.maximum(self.xu - self.xl, 1e-15)

    @staticmethod
    def _resample_profile(profile: np.ndarray, dimension: int) -> np.ndarray:
        # Transfer a normalized decision profile between different dimensions.
        profile = np.asarray(profile, dtype=float).reshape(-1)
        if profile.size == dimension:
            return profile.copy()
        old_axis = np.linspace(0.0, 1.0, profile.size)
        new_axis = np.linspace(0.0, 1.0, dimension)
        return np.interp(new_axis, old_axis, profile)

    def _dynamic_features(self, state: PopulationState) -> np.ndarray:
        # Extract a dimension-free descriptor of the current task and its change.
        elite = state.X[state.rank == np.min(state.rank)]
        normalized = self._normalized(elite)
        center = np.mean(normalized, axis=0)
        spread = np.mean(np.std(normalized, axis=0))
        if self.previous_elite_center is None:
            shift = np.zeros_like(center)
        else:
            shift = center - self.previous_elite_center
        self.previous_elite_center = center.copy()
        feasible_ratio = float(np.mean(state.CV <= 1e-12))
        return np.array(
            [float(np.mean(np.abs(shift))), float(np.std(shift)), float(spread), feasible_ratio],
            dtype=float,
        )

    def _solution_features(self, X: np.ndarray, task_features: np.ndarray) -> np.ndarray:
        # Build invariant candidate descriptors consumed by the centralized model.
        normalized = self._normalized(X)
        if self.previous_elite_center is None:
            center = np.full(self.n_var, 0.5)
        else:
            center = self.previous_elite_center
        distance = np.abs(normalized - center[None, :])
        base = np.column_stack(
            (
                np.mean(normalized, axis=1),
                np.std(normalized, axis=1),
                np.min(normalized, axis=1),
                np.max(normalized, axis=1),
                np.mean(distance, axis=1),
                np.max(distance, axis=1),
            )
        )
        return np.column_stack((base, np.tile(task_features, (len(X), 1))))

    def _knowledge_candidates(self, count: int) -> np.ndarray:
        # Generate cross-problem candidates from stored elite and change profiles.
        if count <= 0 or not self.KNOWLEDGE_BASE:
            return np.empty((0, self.n_var))
        task_matrix = np.vstack([item.task_features for item in self.KNOWLEDGE_BASE])
        distances = np.linalg.norm(task_matrix - self.current_task_features[None, :], axis=1)
        order = np.argsort(distances)
        candidates = []
        span = self.xu - self.xl
        for i in range(count):
            item = self.KNOWLEDGE_BASE[order[i % len(order)]]
            center = self._resample_profile(item.elite_profile, self.n_var)
            shift = self._resample_profile(item.shift_profile, self.n_var)
            noise = self.random_state.normal(0.0, 0.05, self.n_var)
            normalized = np.clip(center + shift + noise, 0.0, 1.0)
            candidates.append(self.xl + normalized * span)
        return np.asarray(candidates)

    def warm_start_candidates(self) -> np.ndarray | None:
        # Rank a mixed random/knowledge pool with the centralized classifier.
        count = max(1, int(round(self.population_size * self.transfer_fraction)))
        if not self.KNOWLEDGE_BASE or self.CENTRAL_MODEL.updates == 0:
            return None
        knowledge = self._knowledge_candidates(count * self.candidate_multiplier)
        random_pool = self.random_state.uniform(
            self.xl, self.xu, size=(count * self.candidate_multiplier, self.n_var)
        )
        pool = np.vstack((knowledge, random_pool))
        scores = self.CENTRAL_MODEL.predict(
            self._solution_features(pool, self.current_task_features)
        )
        return pool[np.argsort(-scores)[:count]]

    def guided_candidates(self) -> np.ndarray:
        # Reuse the centralized model during the current evolutionary search.
        count = int(round(self.population_size * self.transfer_fraction))
        if count <= 0 or self.CENTRAL_MODEL.updates == 0:
            return np.empty((0, self.n_var))
        knowledge = self._knowledge_candidates(count * self.candidate_multiplier)
        current = self.archive_elites(max(1, count))
        if current.shape[0]:
            ids = self.random_state.integers(0, current.shape[0], size=count * self.candidate_multiplier)
            mutation = current[ids] + self.random_state.normal(
                0.0, 0.08, size=(len(ids), self.n_var)
            ) * (self.xu - self.xl)
            pool = np.vstack((knowledge, project_to_bounds(mutation, self.xl, self.xu)))
        else:
            pool = knowledge
        scores = self.CENTRAL_MODEL.predict(
            self._solution_features(pool, self.current_task_features)
        )
        return pool[np.argsort(-scores)[:count]]

    def after_initialize(self) -> None:
        assert self.state is not None
        self.previous_elite_center = None
        self.current_task_features = self._dynamic_features(self.state)
        self._learn_from_state(self.state)

    def _learn_from_state(self, state: PopulationState) -> None:
        # Train task-specific elite classification in the shared centralized model.
        labels = (state.rank == np.min(state.rank)).astype(float)
        if np.all(labels == labels[0]):
            normalized, _, _ = normalized_objectives(state.F)
            score = np.sum(normalized, axis=1)
            labels = np.zeros(len(score))
            labels[np.argsort(score)[: max(1, len(score) // 4)]] = 1.0
        features = self._solution_features(state.X, self.current_task_features)
        before = self.CENTRAL_MODEL.updates
        self.CENTRAL_MODEL.fit(
            features, labels, self.learning_rate, self.learning_epochs
        )
        self.classification_updates += self.CENTRAL_MODEL.updates - before

    def after_generation(self, previous: PopulationState, current: PopulationState) -> None:
        # Update dynamic features, classifier and the bounded cross-problem knowledge base.
        previous_center = self.previous_elite_center.copy() if self.previous_elite_center is not None else None
        self.current_task_features = self._dynamic_features(current)
        self._learn_from_state(current)
        elite = current.X[current.rank == np.min(current.rank)]
        profile = np.mean(self._normalized(elite), axis=0)
        shift = (
            np.zeros_like(profile)
            if previous_center is None
            else profile - previous_center
        )
        self.KNOWLEDGE_BASE.append(
            ProblemKnowledge(self.current_task_features.copy(), profile.copy(), shift.copy())
        )
        del self.KNOWLEDGE_BASE[:-self.knowledge_size]


def make_learning_edmo(
    population_size: int = 100,
    archive_size: int = 100,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.1,
    transfer_fraction: float = 0.2,
    candidate_multiplier: int = 5,
    learning_rate: float = 0.05,
    learning_epochs: int = 20,
    knowledge_size: int = 32,
    seed: int = 1,
) -> LearningAcrossProblemsEDMO:
    # Create the centralized learning-across-problems EDMO.
    return LearningAcrossProblemsEDMO(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        transfer_fraction=transfer_fraction,
        candidate_multiplier=candidate_multiplier,
        learning_rate=learning_rate,
        learning_epochs=learning_epochs,
        knowledge_size=knowledge_size,
        seed=seed,
    )


LEARNING_EDMO_DEFINITION: Dict[str, Any] = {
    "label": "Learning-across-problems EDMO",
    "factory": make_learning_edmo,
    "implementation_type": "adapted_port",
    "reference": "Y. Xie, Q. Zhao, W. Zhou and Z. Zhu, IEEE TEVC 29(5), 1561-1574 (2025), DOI 10.1109/TEVC.2025.3596468",
    "verified_against": "dynamic-feature, task-classification, centralized-learning and cross-dimension transfer tests; no claim of statistical equivalence",
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 2},
        "archive_size": {"default": 100, "kind": "int", "minimum": 2},
        "crossover_rate": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "transfer_fraction": {"default": 0.2, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "candidate_multiplier": {"default": 5, "kind": "int", "minimum": 1},
        "learning_rate": {"default": 0.05, "kind": "float", "minimum": 1e-9},
        "learning_epochs": {"default": 20, "kind": "int", "minimum": 1},
        "knowledge_size": {"default": 32, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": "Centralized learning across problems with dynamic features and task-specific solution classification.",
}
