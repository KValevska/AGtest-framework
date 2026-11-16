from __future__ import annotations

import inspect

import numpy as np
from pymoo.problems import get_problem

from pymoo_gui.algorithms.article_algorithms_common import MOEADAlgorithm
from pymoo_gui.algorithms.eps_moea import EpsMOEA
from pymoo_gui.algorithms.gde3 import GDE3
from pymoo_gui.algorithms.moead_iepsilon import make_moead_iepsilon
from pymoo_gui.algorithms.research_common import PopulationState, assign_rank_and_crowding
from pymoo_gui.algorithms.rnsga3 import reference_directions_from_points
from pymoo_gui.algorithms.rvea import make_rvea
from pymoo_gui.algorithms.surrogate_common import Kriging
from pymoo_gui.algorithms.tea import _fit_models


def _state(X: np.ndarray, F: np.ndarray, CV: np.ndarray) -> PopulationState:
    rank, crowding = assign_rank_and_crowding(F, CV)
    return PopulationState(X, F, CV, rank, crowding)


def test_epsilon_moea_uses_population_and_archive_parents(monkeypatch) -> None:
    problem = get_problem("zdt1", n_var=4)
    algorithm = EpsMOEA(
        epsilons=np.array([0.05, 0.05]), steady_state=True,
        population_size=8, archive_size=8, mutation_rate=0.0,
    )
    algorithm.setup_rng(4)
    algorithm.initialize(problem)
    assert algorithm.state is not None
    algorithm.archive = _state(
        np.full((2, 4), 0.875),
        np.array([[0.1, 0.9], [0.9, 0.1]]),
        np.zeros(2),
    )
    captured = {}

    def fake_sbx(X, parent_pairs, *args, **kwargs):
        captured["parents"] = X.copy()
        return X[parent_pairs[:, 0]].copy()

    monkeypatch.setattr("pymoo_gui.algorithms.eps_moea.sbx_crossover", fake_sbx)
    algorithm.create_offspring()
    assert np.allclose(captured["parents"][1], 0.875)


def test_gde3_has_no_pymoo_sorting_dependency() -> None:
    source = inspect.getsource(inspect.getmodule(GDE3))
    assert "pymoo.util.nds" not in source
    assert "non_dominated_fronts" in source


def test_moead_external_archive_contains_only_nondominated_points() -> None:
    algorithm = MOEADAlgorithm(population_size=4, archive_size=4)
    X = np.arange(8, dtype=float).reshape(4, 2)
    F = np.array([[0.0, 1.0], [1.0, 0.0], [0.8, 0.8], [2.0, 2.0]])
    archive = algorithm.build_archive(_state(X, F, np.zeros(4)))
    np.testing.assert_allclose(archive.F, [[0.0, 1.0], [1.0, 0.0], [0.8, 0.8]])


def test_moead_global_mating_uses_global_replacement_set() -> None:
    problem = get_problem("zdt1", n_var=4)
    algorithm = MOEADAlgorithm(
        population_size=4,
        archive_size=4,
        n_neighbors=2,
        n_partitions=3,
        prob_neighbor_mating=0.0,
        max_replacements=4,
    )
    algorithm.setup_rng(3)
    algorithm.initialize(problem)
    comparisons = []
    algorithm.generate_child = lambda subproblem, pool: algorithm.state.X[[subproblem]].copy()
    algorithm.replacement_allowed = lambda *args: comparisons.append(args) or False

    algorithm.step()

    assert len(comparisons) == algorithm.population_size**2


def test_moead_iepsilon_initial_level_uses_descending_violation_order() -> None:
    problem = get_problem("tnk")
    algorithm = make_moead_iepsilon(problem, population_size=20, neighborhood_size=5)
    algorithm.maximum_generations = 20
    algorithm.setup_rng(9)
    algorithm.initialize(problem)
    ordered = np.sort(algorithm.state.CV)[::-1]
    theta = max(0, int(np.ceil(0.05 * len(ordered))) - 1)
    assert algorithm.initial_epsilon == ordered[theta]


def test_rnsga3_projects_shrunken_lattice_around_aspiration_point() -> None:
    unit_points = np.array([[0.2, 0.8]])
    simplex = np.array([[0.0, 1.0], [0.5, 0.5], [1.0, 0.0]])
    directions = reference_directions_from_points(unit_points, simplex, mu=0.2)
    np.testing.assert_allclose(np.sum(directions, axis=1), 1.0)
    np.testing.assert_allclose(np.mean(directions[:3], axis=0), unit_points[0], atol=1e-12)
    np.testing.assert_allclose(directions[-2:], np.eye(2))


def test_rvea_uses_actual_termination_horizon() -> None:
    problem = get_problem("zdt1", n_var=4)
    algorithm = make_rvea(problem, pop_size=8, n_partitions=7)
    algorithm.gui_minimize(problem=problem, termination=("n_gen", 3), seed=2)
    assert algorithm.maximum_generations == 3


def test_tea_uses_internal_dace_style_kriging() -> None:
    X = np.linspace(0.0, 1.0, 12)[:, None]
    Y = np.column_stack((X[:, 0], X[:, 0] ** 2))
    models = _fit_models(X, Y, seed=3)
    assert all(isinstance(model, Kriging) for model in models)

