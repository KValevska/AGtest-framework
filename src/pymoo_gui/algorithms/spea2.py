# SPEA2-style genetic algorithm implementation and GUI factory definition.

# ------------------------------------------------------------------------------------
# Module: spea2.py
# Summary: SPEA2-compatible genetic algorithm class, tournament selection and GUI factory definition.
# Implementation: SPEA2 selection and survival behavior are configured for pymoo optimization runs.
# Responsibility: supplies a strength-Pareto evolutionary algorithm for dissertation comparisons.
# Author: Kristina Valevska, MSc Eng.
# ------------------------------------------------------------------------------------
from __future__ import annotations

from typing import Any, Dict

import numpy as np
from pymoo.algorithms.base.genetic import GeneticAlgorithm
from pymoo.docs import parse_doc_string
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.selection.tournament import TournamentSelection, compare
from pymoo.operators.survival.rank_and_crowding import RankAndCrowding
from pymoo.termination.default import DefaultMultiObjectiveTermination
from pymoo.util.display.multi import MultiObjectiveOutput
from pymoo.util.dominator import Dominator
from pymoo.util.misc import has_feasible


def _parse_positive_int(value: Any, field_name: str) -> int:
    # Parse a positive integer parameter for SPEA2 configuration.
    # Raises:
    # ValueError: If the value cannot be parsed or is below 1.
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def binary_tournament(pop, P, algorithm, **kwargs):
    # Select parents with a binary tournament based on feasibility, dominance/rank and crowding.
    # Args:
    # pop (Any): pymoo population containing `F`, `CV`, rank and crowding data.
    # P (Any): Tournament candidate index matrix.
    # algorithm (Any): SPEA2 algorithm instance with tournament settings.
    # **kwargs (Any): Compatibility arguments provided by pymoo selection.
    # Returns:
    # np.ndarray: Selected parent indices with shape expected by pymoo.
    # Raises:
    n_tournaments, n_parents = P.shape

    if n_parents != 2:
        raise ValueError("Only implemented for binary tournament!")

    tournament_type = algorithm.tournament_type
    selected = np.full(n_tournaments, np.nan)

    for i in range(n_tournaments):
        a, b = P[i, 0], P[i, 1]
        a_cv, a_f, b_cv, b_f = pop[a].CV[0], pop[a].F, pop[b].CV[0], pop[b].F
        rank_a, cd_a = pop[a].get("rank", "crowding")
        rank_b, cd_b = pop[b].get("rank", "crowding")

        if a_cv > 0.0 or b_cv > 0.0:
            selected[i] = compare(
                a,
                a_cv,
                b,
                b_cv,
                method="smaller_is_better",
                return_random_if_equal=True,
                random_state=algorithm.random_state,
            )
        else:
            if tournament_type == "comp_by_dom_and_crowding":
                relation = Dominator.get_relation(a_f, b_f)
                if relation == 1:
                    selected[i] = a
                elif relation == -1:
                    selected[i] = b
            elif tournament_type == "comp_by_rank_and_crowding":
                selected[i] = compare(a, rank_a, b, rank_b, method="smaller_is_better")
            else:
                raise ValueError(f"Unknown tournament type: {tournament_type}")

            if np.isnan(selected[i]):
                selected[i] = compare(
                    a,
                    cd_a,
                    b,
                    cd_b,
                    method="larger_is_better",
                    return_random_if_equal=True,
                    random_state=algorithm.random_state,
                )

    return selected[:, None].astype(int, copy=False)


class RankAndCrowdingSurvival(RankAndCrowding):
    # Survival operator wrapper using nondominated rank and crowding distance.

    def __init__(self, nds=None, crowding_func: str = "cd"):
        # Initialize rank-and-crowding survival with the requested crowding metric.
        super().__init__(nds, crowding_func)


class SPEA2(GeneticAlgorithm):
    # pymoo-compatible SPEA2-style genetic algorithm using tournament selection and rank-crowding survival.
    # roznorodnosci, aby znalezc front Pareto.

    def __init__(
        self,
        pop_size=100,
        sampling=FloatRandomSampling(),
        selection=TournamentSelection(func_comp=binary_tournament),
        crossover=SBX(eta=15, prob=0.9),
        mutation=PM(eta=20),
        survival=RankAndCrowdingSurvival(),
        output=MultiObjectiveOutput(),
        **kwargs,
    ):
        # Configure the genetic operators and default multiobjective termination for SPEA2.
        # Args:
        # pop_size (int): Number of individuals in the population.
        # sampling (Any): Initial population sampler.
        # crossover (Any): Crossover operator.
        # mutation (Any): Mutation operator.
        # output (Any): pymoo display output object.
        super().__init__(
            pop_size=pop_size,
            sampling=sampling,
            selection=selection,
            crossover=crossover,
            mutation=mutation,
            survival=survival,
            output=output,
            advance_after_initial_infill=True,
            **kwargs,
        )

        self.termination = DefaultMultiObjectiveTermination()
        self.tournament_type = "comp_by_dom_and_crowding"

    def _set_optimum(self, **kwargs):
        # Update the current optimum using feasible rank-zero solutions or the least infeasible fallback.
        if not has_feasible(self.pop):
            self.opt = self.pop[[np.argmin(self.pop.get("CV"))]]
        else:
            self.opt = self.pop[self.pop.get("rank") == 0]


parse_doc_string(SPEA2.__init__)


def make_spea2(pop_size: int = 100) -> SPEA2:
    # Create a configured SPEA2 algorithm for the GUI registry.
    # Args:
    # pop_size (int): Number of individuals in the population.
    # Returns:
    # SPEA2: Configured algorithm instance.
    # Raises:
    return SPEA2(pop_size=_parse_positive_int(pop_size, "pop_size"))


SPEA2_DEFINITION: Dict[str, Any] = {
    "label": "SPEA2",
    "factory": make_spea2,
    "form_note": "Formularz pokazuje tylko parametry przekazywane bezposrednio do factory algorytmu.",
}
SPEA2_DEFINITION["form_note"] = "The form shows only the parameters passed directly to the algorithm factory."
