# ------------------------------------------------------------------------------------
# File: cm_moea.py
# Contents: constrained multimodal MOEA class, factory and GUI registry definition.
# What happens here: adaptive epsilon handling, diversity-biased offspring generation,
# local/global environmental selection and a diversity-preserving archive are combined.
# Role in the framework: adds an article-inspired CM-MOEA variant for constrained
# multimodal multi-objective optimization.
# Author: mgr inz. Kristina Valevska
# Implementation source: own implementation based on the article.
# ------------------------------------------------------------------------------------

from __future__ import annotations

from typing import Any, Dict

import numpy as np

from .research_common import (
    PopulationState,
    ResearchMOOAlgorithm,
    assign_rank_and_crowding,
    crowding_distance,
    polynomial_mutation,
    parse_positive_int,
    parse_probability,
    select_survivors_nsga2,
    stable_survivor_order,
)


class CMMOEA(ResearchMOOAlgorithm):
    """
    EN:
    CM-MOEA with adaptive epsilon constraint handling, diversity-based mutation,
    two-level environmental selection and a crowding-based archive update.
    Implementation source: own implementation based on the article.

    PL:
    CM-MOEA z adaptacyjnym epsilon dla ograniczen, mutacja oparta o roznorodnosc,
    dwuetapowa selekcja srodowiskowa oraz archiwum opartym o crowding.
    """

    def __init__(
        self,
        population_size: int = 100,
        archive_size: int = 100,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1,
        guided_fraction: float = 0.2,
        candidate_multiplier: int = 5,
        seed: int = 1,
    ) -> None:
        super().__init__(
            population_size=population_size,
            archive_size=archive_size,
            crossover_rate=crossover_rate,
            mutation_rate=mutation_rate,
            seed=seed,
        )
        self.guided_fraction = parse_probability(guided_fraction, "guided_fraction")
        self.candidate_multiplier = parse_positive_int(candidate_multiplier, "candidate_multiplier")

    def _adaptive_epsilon(self, cv: np.ndarray) -> float:
        """
        EN:
        Compute a relaxed constraint threshold from the current violation profile.

        PL:
        Wyznacza adaptacyjny prog epsilon na podstawie aktualnych naruszen.
        """
        cv = np.asarray(cv, dtype=float).reshape(-1)
        positive = cv[cv > 1e-12]
        if positive.size == 0:
            return 0.0
        feasible_ratio = float(np.mean(cv <= 1e-12))
        if feasible_ratio >= 0.95:
            return 0.0
        quantile = min(0.95, max(0.25, 1.0 - feasible_ratio))
        return float(np.quantile(positive, quantile) * (1.0 + self.epsilon))

    def _relaxed_cv(self, cv: np.ndarray, epsilon_value: float) -> np.ndarray:
        """
        EN:
        Transform constraint violations into epsilon-relaxed violations.

        PL:
        Zamienia naruszenia ograniczen na postac zrelaksowana przez epsilon.
        """
        cv = np.asarray(cv, dtype=float).reshape(-1)
        return np.maximum(cv - float(max(epsilon_value, 0.0)), 0.0)

    def _decision_crowding(self, X: np.ndarray) -> np.ndarray:
        """
        EN:
        Estimate diversity in the decision space using NSGA-II-style crowding.

        PL:
        Szacuje roznorodnosc w przestrzeni decyzyjnej przez crowding jak w NSGA-II.
        """
        X = np.asarray(X, dtype=float)
        if X.shape[0] <= 2:
            return np.full(X.shape[0], np.inf, dtype=float)
        span = np.maximum(np.max(X, axis=0) - np.min(X, axis=0), 1e-12)
        Xn = (X - np.min(X, axis=0)) / span
        return crowding_distance(Xn)

    def _species_labels(self, X: np.ndarray, n_species: int) -> np.ndarray:
        """
        EN:
        Partition the decision space into simple species using farthest anchors.

        PL:
        Dzieli przestrzen decyzyjna na gatunki przez kotwice typu farthest-point.
        """
        X = np.asarray(X, dtype=float)
        n_points = X.shape[0]
        if n_points == 0 or n_species <= 1:
            return np.zeros(n_points, dtype=int)

        n_species = max(1, min(int(n_species), n_points))
        span = np.maximum(np.max(X, axis=0) - np.min(X, axis=0), 1e-12)
        Xn = (X - np.min(X, axis=0)) / span

        anchors = [int(np.argmin(np.sum(Xn, axis=1)))]
        min_dist = np.linalg.norm(Xn - Xn[anchors[0]], axis=1)
        for _ in range(1, n_species):
            next_anchor = int(np.argmax(min_dist))
            anchors.append(next_anchor)
            min_dist = np.minimum(min_dist, np.linalg.norm(Xn - Xn[next_anchor], axis=1))

        anchor_points = Xn[np.asarray(anchors, dtype=int)]
        distances = np.linalg.norm(Xn[:, None, :] - anchor_points[None, :, :], axis=2)
        return np.argmin(distances, axis=1)

    def _selection_order(self, F: np.ndarray, CV: np.ndarray, epsilon_value: float) -> np.ndarray:
        """
        EN:
        Rank candidates with epsilon-relaxed constraints.

        PL:
        Ustala kolejnosc kandydatow z uzyciem zrelaksowanych ograniczen.
        """
        relaxed_cv = self._relaxed_cv(CV, epsilon_value)
        rank, crowding = assign_rank_and_crowding(F, relaxed_cv)
        return stable_survivor_order(rank, crowding, relaxed_cv)

    def _diverse_parent_indices(self, count: int) -> np.ndarray:
        """
        EN:
        Select diverse feasible or near-feasible parents for extra mutation.

        PL:
        Wybiera roznorodnych rodzicow wykonalnych lub prawie wykonalnych do mutacji.
        """
        if self.state is None or self.state.X.shape[0] == 0 or count <= 0:
            return np.empty(0, dtype=int)

        epsilon_value = self._adaptive_epsilon(self.state.CV)
        relaxed_cv = self._relaxed_cv(self.state.CV, epsilon_value)
        preferred = np.flatnonzero(relaxed_cv <= 1e-12)
        if preferred.size == 0:
            preferred = np.argsort(self.state.CV, kind="mergesort")[: max(2, count)]

        decision_cd = self._decision_crowding(self.state.X)
        objective_cd = crowding_distance(self.state.F)
        decision_score = np.where(np.isfinite(decision_cd), decision_cd, 1e12)
        objective_score = np.where(np.isfinite(objective_cd), objective_cd, 1e12)
        score = decision_score + objective_score

        pool_size = min(preferred.size, max(count, count * self.candidate_multiplier))
        order = preferred[np.argsort(score[preferred], kind="mergesort")[::-1]]
        return order[:pool_size]

    def create_offspring(self) -> np.ndarray:
        """
        EN:
        Create offspring with standard variation plus diversity-based mutation.

        PL:
        Tworzy potomstwo przez standardowe operatory oraz mutacje wsparta roznorodnoscia.
        """
        offspring = super().create_offspring()
        guided_count = int(round(self.population_size * self.guided_fraction))
        if self.state is None or guided_count <= 0:
            return offspring

        parent_pool = self._diverse_parent_indices(guided_count)
        if parent_pool.size == 0:
            return offspring

        chosen = self.random_state.choice(parent_pool, size=guided_count, replace=parent_pool.size < guided_count)
        guided = self.state.X[np.asarray(chosen, dtype=int)]
        guided = polynomial_mutation(
            guided,
            self.xl,
            self.xu,
            max(5.0, self.mutation_eta * 0.5),
            max(self.mutation_rate, 1.0 / max(self.n_var, 1)),
            self.random_state,
            strength=1.35,
        )
        offspring[:guided_count] = guided
        return offspring

    def guided_candidates(self) -> np.ndarray:
        """
        EN:
        CM-MOEA uses diversity-biased offspring generation instead of extra injections.

        PL:
        CM-MOEA korzysta z roznorodnego tworzenia potomstwa zamiast dodatkowych wstrzykniec.
        """
        return np.empty((0, self.n_var), dtype=float)

    def environmental_selection(
        self,
        X: np.ndarray,
        F: np.ndarray,
        CV: np.ndarray,
        n_survive: int,
    ):
        """
        EN:
        Perform a two-level environmental selection with local species filtering
        followed by global epsilon-relaxed survivor selection.

        PL:
        Wykonuje dwuetapowa selekcje: lokalna w gatunkach, potem globalna z epsilon.
        """
        X = np.asarray(X, dtype=float)
        F = np.asarray(F, dtype=float)
        CV = np.asarray(CV, dtype=float).reshape(-1)
        n_points = X.shape[0]
        if n_points <= int(n_survive):
            return select_survivors_nsga2(X, F, CV, int(n_survive))

        epsilon_value = self._adaptive_epsilon(CV)
        feasible_ratio = float(np.mean(CV <= 1e-12))
        local_share = float(np.clip(1.0 - feasible_ratio, 0.3, 0.7))
        local_target = min(int(n_survive), max(1, int(round(n_survive * local_share))))

        n_species = min(max(2, int(np.sqrt(n_survive))), n_points)
        labels = self._species_labels(X, n_species)
        sizes = np.bincount(labels, minlength=n_species).astype(float)
        quotas = np.floor(local_target * sizes / max(float(np.sum(sizes)), 1.0)).astype(int)

        non_empty = np.flatnonzero(sizes > 0)
        for label in non_empty:
            if quotas[label] == 0 and np.sum(quotas) < local_target:
                quotas[label] = 1
        while np.sum(quotas) < local_target:
            label = int(non_empty[np.argmax(sizes[non_empty] - quotas[non_empty])])
            quotas[label] += 1
        while np.sum(quotas) > local_target:
            reducible = non_empty[quotas[non_empty] > 0]
            label = int(reducible[np.argmax(quotas[reducible])])
            quotas[label] -= 1

        local_indices: list[np.ndarray] = []
        for label in non_empty:
            members = np.flatnonzero(labels == label)
            quota = min(int(quotas[label]), members.size)
            if quota <= 0:
                continue
            order = self._selection_order(F[members], CV[members], epsilon_value)
            local_indices.append(members[order[:quota]])

        local_idx = (
            np.unique(np.concatenate(local_indices).astype(int))
            if local_indices
            else np.empty(0, dtype=int)
        )
        if local_idx.size > local_target:
            order = self._selection_order(F[local_idx], CV[local_idx], epsilon_value)
            local_idx = local_idx[order[:local_target]]

        selected_mask = np.zeros(n_points, dtype=bool)
        selected_mask[local_idx] = True
        remaining_idx = np.flatnonzero(~selected_mask)
        global_target = int(n_survive) - local_idx.size

        if global_target > 0:
            if remaining_idx.size == 0:
                global_idx = np.empty(0, dtype=int)
            else:
                order = self._selection_order(F[remaining_idx], CV[remaining_idx], epsilon_value)
                global_idx = remaining_idx[order[:global_target]]
            final_idx = np.concatenate([local_idx, global_idx]).astype(int)
        else:
            final_idx = local_idx.astype(int)

        if final_idx.size < int(n_survive):
            order = self._selection_order(F, CV, epsilon_value)
            filler = order[~np.isin(order, final_idx)]
            final_idx = np.concatenate([final_idx, filler[: int(n_survive) - final_idx.size]]).astype(int)
        elif final_idx.size > int(n_survive):
            order = self._selection_order(F[final_idx], CV[final_idx], epsilon_value)
            final_idx = final_idx[order[: int(n_survive)]]

        relaxed_cv = self._relaxed_cv(CV[final_idx], epsilon_value)
        rank, crowding = assign_rank_and_crowding(F[final_idx], relaxed_cv)
        return PopulationState(
            X=X[final_idx],
            F=F[final_idx],
            CV=CV[final_idx],
            rank=rank,
            crowding=crowding,
        )

    def build_archive(self, state):
        """
        EN:
        Maintain an archive that prefers nondominated solutions and resolves
        overflow by treating decision-space and objective-space crowding as a
        secondary bi-objective selection problem.

        PL:
        Utrzymuje archiwum preferujace niedominowane rozwiazania i przy nadmiarze
        rozstrzyga je przez crowding w przestrzeni decyzji i celow.
        """
        if self.archive is None:
            merged_X = state.X
            merged_F = state.F
            merged_CV = state.CV
        else:
            merged_X = np.vstack([self.archive.X, state.X])
            merged_F = np.vstack([self.archive.F, state.F])
            merged_CV = np.concatenate([self.archive.CV, state.CV])

        preselected = select_survivors_nsga2(
            merged_X,
            merged_F,
            merged_CV,
            min(merged_X.shape[0], max(self.archive_size * self.candidate_multiplier, self.archive_size)),
        )
        if preselected.X.shape[0] <= self.archive_size:
            return preselected

        decision_cd = self._decision_crowding(preselected.X)
        objective_cd = crowding_distance(preselected.F)
        decision_score = np.where(np.isfinite(decision_cd), decision_cd, 1e12)
        objective_score = np.where(np.isfinite(objective_cd), objective_cd, 1e12)

        diversity_objectives = np.column_stack([-decision_score, -objective_score])
        rank, crowding = assign_rank_and_crowding(
            diversity_objectives,
            np.zeros(preselected.X.shape[0], dtype=float),
        )
        order = stable_survivor_order(rank, crowding, np.zeros(preselected.X.shape[0], dtype=float))
        keep = order[: self.archive_size]
        return PopulationState(
            X=preselected.X[keep],
            F=preselected.F[keep],
            CV=preselected.CV[keep],
            rank=preselected.rank[keep],
            crowding=preselected.crowding[keep],
        )


def make_cm_moea(
    population_size: int = 100,
    archive_size: int = 100,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.1,
    guided_fraction: float = 0.2,
    candidate_multiplier: int = 5,
    seed: int = 1,
) -> CMMOEA:
    """
    EN:
    Create a CM-MOEA instance for the GUI registry.

    PL:
    Tworzy instancje CM-MOEA dla rejestru GUI.
    """
    return CMMOEA(
        population_size=population_size,
        archive_size=archive_size,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
        guided_fraction=guided_fraction,
        candidate_multiplier=candidate_multiplier,
        seed=seed,
    )


CM_MOEA_DEFINITION: Dict[str, Any] = {
    "label": "CM-MOEA",
    "factory": make_cm_moea,
    "form_fields": {
        "population_size": {"default": 100, "kind": "int", "minimum": 1},
        "archive_size": {"default": 100, "kind": "int", "minimum": 1},
        "crossover_rate": {"default": 0.9, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "mutation_rate": {"default": 0.1, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "guided_fraction": {"default": 0.2, "kind": "float", "minimum": 0.0, "maximum": 1.0},
        "candidate_multiplier": {"default": 5, "kind": "int", "minimum": 1},
        "seed": {"default": 1, "kind": "int", "minimum": 0},
    },
    "form_note": (
        "Own implementation based on the article. Uses adaptive epsilon handling, "
        "diversity-based mutation, two-level environmental selection and a "
        "decision/objective-space archive update."
    ),
}
