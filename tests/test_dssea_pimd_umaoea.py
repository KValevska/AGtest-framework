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
from pymoo_gui.algorithms.dssea import epsilon_spea2_fitness, make_dssea
from pymoo_gui.algorithms.pimd import estimate_pf_shape, make_pimd
from pymoo_gui.algorithms.umaoea import make_umaoea, merge_sequence, reference_weights


@pytest.mark.parametrize("key", ["dssea", "pimd", "umaoea"])
def test_new_algorithm_is_registered_as_standalone(key: str) -> None:
    entry = ALGORITHMS[key]
    assert entry["implementation_type"] == "adapted_port"
    assert entry["reference"]
    assert entry["verified_against"]


@pytest.mark.parametrize("key", ["dssea", "pimd", "umaoea"])
def test_new_algorithm_does_not_import_ready_algorithm_package(key: str) -> None:
    path = Path(inspect.getsourcefile(ALGORITHMS[key]["factory"]))
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    assert not any(
        name.startswith("pymoo.algorithms") or name == "platypus" or name.startswith("platypus.")
        for name in imported
    )


def test_dssea_epsilon_fitness_prefers_feasibility() -> None:
    objectives = np.array([[10.0, 10.0], [0.0, 0.0]])
    violations = np.array([0.0, 1.0])
    fitness = epsilon_spea2_fitness(objectives, violations, epsilon=0.0)
    assert fitness[0] < fitness[1]


def test_dssea_runtime_includes_aldva_evaluations() -> None:
    algorithm = make_dssea(population_size=8, n_sel=1, n_per=2, seed=3)
    generations = []
    result = minimize(
        get_problem("tnk"),
        algorithm,
        ("n_gen", 2),
        seed=3,
        verbose=False,
        callback=lambda current: generations.append(current.n_gen),
    )

    assert result.F.shape == (8, 2)
    assert algorithm.evaluator.n_eval == 8 + 2 * 1 * 2 + 2 * 8
    assert algorithm.variable_ranks.shape == (2,)
    assert generations == [1, 2]


def test_pimd_shape_estimate_and_runtime() -> None:
    curve = np.column_stack((np.linspace(0.0, 1.0, 30), np.linspace(1.0, 0.0, 30)))
    assert np.isfinite(estimate_pf_shape(curve))
    algorithm = make_pimd(population_size=8, wmax=2, eta=2, seed=5)
    result = minimize(
        get_problem("zdt1", n_var=5), algorithm, ("n_gen", 2), seed=5, verbose=False
    )

    assert result.X.shape == (8, 5)
    assert result.F.shape == (8, 2)
    assert algorithm.evaluator.n_eval <= 8 + 2 * 2


def test_pimd_rejects_constrained_problem_before_run() -> None:
    with pytest.raises(AlgorithmProblemCompatibilityError, match="only unconstrained"):
        validate_algorithm_problem(ALGORITHMS["pimd"], get_problem("tnk"))
    with pytest.raises(AlgorithmProblemCompatibilityError, match="only unconstrained"):
        validate_algorithm_problem(ALGORITHMS["umaoea"], get_problem("tnk"))


def test_umaoea_reference_weights_merge_and_runtime() -> None:
    rng = np.random.default_rng(7)
    weights = reference_weights(8, 3, rng, pool_size=100)
    sequence = merge_sequence(8, 2)
    assert weights.shape == (8, 3)
    assert np.all(weights > 0.0)
    np.testing.assert_array_equal(np.sort(sequence), np.arange(8))

    algorithm = make_umaoea(population_size=8, block=2, reference_pool=100, seed=7)
    generations = []
    result = minimize(
        get_problem("dtlz2", n_var=7, n_obj=3),
        algorithm,
        ("n_gen", 2),
        seed=7,
        verbose=False,
        callback=lambda current: generations.append(current.n_gen),
    )
    assert result.X.shape == (8, 7)
    assert result.F.shape == (8, 3)
    assert algorithm.archive is not None
    assert algorithm.evaluator.n_eval >= 2 * algorithm.population_size
    assert generations == [1, 2]


def test_new_algorithms_are_reproducible_for_short_runs() -> None:
    problem = get_problem("dtlz2", n_var=7, n_obj=3)
    first = make_umaoea(population_size=8, block=2, reference_pool=100, seed=11)
    second = make_umaoea(population_size=8, block=2, reference_pool=100, seed=11)
    first_result = minimize(problem, first, ("n_gen", 1), seed=11, verbose=False)
    second_result = minimize(problem, second, ("n_gen", 1), seed=11, verbose=False)
    np.testing.assert_allclose(first_result.X, second_result.X)
    np.testing.assert_allclose(first_result.F, second_result.F)
