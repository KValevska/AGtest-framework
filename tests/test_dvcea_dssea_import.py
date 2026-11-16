from __future__ import annotations

import ast
import inspect
from pathlib import Path

import numpy as np
import pytest
from pymoo.problems import get_problem

from pymoo_gui.algorithms import (
    ALGORITHMS,
    AlgorithmProblemCompatibilityError,
    minimize,
    validate_algorithm_problem,
)
from pymoo_gui.algorithms.dvcea import improved_epsilon_survival, kmeans_centroids, make_dvcea


def test_dvcea_is_registered_and_dssea_is_not_duplicated() -> None:
    assert ALGORITHMS["dvcea"]["label"] == "DVCEA"
    assert [key for key in ALGORITHMS if key == "dssea"] == ["dssea"]
    assert ALGORITHMS["dvcea"]["requires_constraints"] is True
    assert ALGORITHMS["dssea"]["requires_constraints"] is True


@pytest.mark.parametrize("key", ["dvcea", "dssea"])
def test_modules_have_project_header_and_no_ready_algorithm_import(key: str) -> None:
    path = Path(inspect.getsourcefile(ALGORITHMS[key]["factory"]))
    source = path.read_text(encoding="utf-8")
    assert "Author: Kristina Valevska, MSc Eng." in source
    tree = ast.parse(source)
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    assert not any(module.startswith("pymoo.algorithms") for module in imports)


def test_kmeans_centroids_is_deterministic_and_dimensionally_correct() -> None:
    X = np.arange(60, dtype=float).reshape(10, 6)
    a = kmeans_centroids(X, 5, np.random.default_rng(4))
    b = kmeans_centroids(X, 5, np.random.default_rng(4))
    assert a.shape == (5, 6)
    np.testing.assert_allclose(a, b)


def test_improved_survival_prioritizes_epsilon_feasible_pool() -> None:
    X = np.arange(12, dtype=float).reshape(4, 3)
    F = np.array([[5.0, 5.0], [4.0, 4.0], [0.0, 0.0], [1.0, 1.0]])
    CV = np.array([0.0, 0.05, 1.0, 2.0])
    state, fitness = improved_epsilon_survival(X, F, CV, count=2, epsilon=0.1)
    assert np.all(state.CV <= 0.1)
    assert fitness.shape == (2,)


def test_dvcea_runtime_classification_cost_two_stages_and_callback() -> None:
    problem = get_problem("tnk")
    algorithm = make_dvcea(pop_size=10, seed=7)
    generations = []
    result = minimize(problem, algorithm, ("n_gen", 2), seed=7, callback=lambda current: generations.append(current.n_gen))
    assert result.F.shape == (10, 2)
    assert algorithm.evaluator.n_eval == 10 + 20 * problem.n_var + 2 * 10 * 2
    assert generations == [1, 2]
    variables = np.sort(np.concatenate((algorithm.fea_variables, algorithm.infea_variables)))
    np.testing.assert_array_equal(variables, np.arange(problem.n_var))


def test_dvcea_requires_constrained_problem() -> None:
    with pytest.raises(AlgorithmProblemCompatibilityError, match="requires a benchmark"):
        validate_algorithm_problem(ALGORITHMS["dvcea"], get_problem("zdt1"))


def test_dvcea_short_run_is_reproducible() -> None:
    problem = get_problem("tnk")
    first, second = make_dvcea(pop_size=10, seed=11), make_dvcea(pop_size=10, seed=11)
    a = minimize(problem, first, ("n_gen", 2), seed=11)
    b = minimize(problem, second, ("n_gen", 2), seed=11)
    np.testing.assert_allclose(a.X, b.X)
    np.testing.assert_allclose(a.F, b.F)

