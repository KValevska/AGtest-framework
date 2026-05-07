"""
EN: SPEA2-style genetic algorithm implementation and GUI factory definition.
"""

# ------------------------------------------------------------------------------------
# File: spea2.py
# Contents: SPEA2-compatible genetic algorithm class, tournament selection and GUI factory definition.
# What happens here: SPEA2 selection and survival behavior are configured for pymoo optimization runs.
# Role in the framework: supplies a strength-Pareto evolutionary algorithm for dissertation comparisons.
# Copyright 2015-2026 by Filip Rudziński
# Author: mgr inż. Kristina Valevska
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
    """
    EN:
    Parse a positive integer parameter for SPEA2 configuration.

    PL:
    Sprawdza, czy parametr SPEA2 jest dodatnia liczba calkowita.

    Raises:
        ValueError: EN: If the value cannot be parsed or is below 1.
                    PL: Gdy wartosc jest niepoprawna albo mniejsza od 1.
    """
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field_name}: {value!r}") from exc
    if parsed < 1:
        raise ValueError(f"{field_name} must be >= 1, got {parsed}")
    return parsed


def binary_tournament(pop, P, algorithm, **kwargs):
    """
    EN:
    Select parents with a binary tournament based on feasibility, dominance/rank and crowding.

    PL:
    Wybiera rodzicow do tworzenia nowych rozwiazan, porownujac pary kandydatow
    wedlug ograniczen, dominacji i roznorodnosci.

    Args:
        pop (Any): EN: pymoo population containing `F`, `CV`, rank and crowding data.
                   PL: Populacja algorytmu z wynikami i dodatkowymi ocenami.
        P (Any): EN: Tournament candidate index matrix.
                 PL: Pary indeksow osobnikow porownywanych w turnieju.
        algorithm (Any): EN: SPEA2 algorithm instance with tournament settings.
                         PL: Dzialajacy algorytm z ustawieniami turnieju.
        **kwargs (Any): EN: Compatibility arguments provided by pymoo selection.
                        PL: Dodatkowe dane przekazywane przez pymoo.

    Returns:
        np.ndarray: EN: Selected parent indices with shape expected by pymoo.
                    PL: Indeksy wybranych rodzicow.

    Raises:
        ValueError: EN: If tournament arity or tournament type is unsupported.
                    PL: Gdy typ turnieju nie jest obslugiwany.
    """
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
    """
    EN:
    Survival operator wrapper using nondominated rank and crowding distance.

    PL:
    Operator wyboru osobnikow, ktory zostawia lepsze i bardziej zroznicowane
    rozwiazania do nastepnej generacji.
    """

    def __init__(self, nds=None, crowding_func: str = "cd"):
        """
        EN:
        Initialize rank-and-crowding survival with the requested crowding metric.

        PL:
        Ustawia sposob oceny roznorodnosci osobnikow przy wyborze do kolejnej generacji.
        """
        super().__init__(nds, crowding_func)


class SPEA2(GeneticAlgorithm):
    """
    EN:
    pymoo-compatible SPEA2-style genetic algorithm using tournament selection and rank-crowding survival.

    PL:
    Algorytm ewolucyjny SPEA2, ktory porownuje rozwiazania wedlug jakosci i
    roznorodnosci, aby znalezc front Pareto.
    """

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
        """
        EN:
        Configure the genetic operators and default multiobjective termination for SPEA2.

        PL:
        Ustawia populacje, selekcje, krzyzowanie, mutacje i domyslne zasady pracy algorytmu.

        Args:
            pop_size (int): EN: Number of individuals in the population.
                            PL: Liczba rozwiazan w populacji.
            sampling (Any): EN: Initial population sampler.
                            PL: Sposob tworzenia pierwszej populacji.
            selection (Any): EN: Parent selection operator.
                             PL: Sposob wyboru rodzicow.
            crossover (Any): EN: Crossover operator.
                             PL: Operator laczenia rodzicow.
            mutation (Any): EN: Mutation operator.
                            PL: Operator losowych zmian.
            survival (Any): EN: Survival operator.
                            PL: Sposob wyboru rozwiazan do nastepnej generacji.
            output (Any): EN: pymoo display output object.
                          PL: Obiekt odpowiedzialny za tekstowe informacje pymoo.
            **kwargs (Any): EN: Additional `GeneticAlgorithm` options.
                            PL: Dodatkowe ustawienia algorytmu.
        """
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
        """
        EN:
        Update the current optimum using feasible rank-zero solutions or the least infeasible fallback.

        PL:
        Aktualizuje najlepsze znane rozwiazania; jesli wszystkie lamia ograniczenia,
        wybiera to z najmniejszym naruszeniem.
        """
        if not has_feasible(self.pop):
            self.opt = self.pop[[np.argmin(self.pop.get("CV"))]]
        else:
            self.opt = self.pop[self.pop.get("rank") == 0]


parse_doc_string(SPEA2.__init__)


def make_spea2(pop_size: int = 100) -> SPEA2:
    """
    EN:
    Create a configured SPEA2 algorithm for the GUI registry.

    PL:
    Tworzy gotowy algorytm SPEA2 z podanym rozmiarem populacji.

    Args:
        pop_size (int): EN: Number of individuals in the population.
                        PL: Liczba rozwiazan w populacji.

    Returns:
        SPEA2: EN: Configured algorithm instance.
               PL: Gotowy algorytm do uruchomienia.

    Raises:
        ValueError: EN: If `pop_size` is not a positive integer.
                    PL: Gdy rozmiar populacji jest niepoprawny.
    """
    return SPEA2(pop_size=_parse_positive_int(pop_size, "pop_size"))


SPEA2_DEFINITION: Dict[str, Any] = {
    "label": "SPEA2",
    "factory": make_spea2,
    "form_note": "Formularz pokazuje tylko parametry przekazywane bezposrednio do factory algorytmu.",
}
