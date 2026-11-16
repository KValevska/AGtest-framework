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
    make_generation_callback,
    minimize,
    validate_algorithm_problem,
)
from pymoo_gui.algorithms.cmoea_cd import constraint_pareto_mask, make_cmoea_cd
from pymoo_gui.algorithms.cmobr import epsilon_relaxation, make_cmobr, relative_front_change
from pymoo_gui.problems import PROBLEMS


@pytest.mark.parametrize("key", ["cmoea_cd", "cmobr"])
def test_algorithm_is_registered_with_header_and_without_ready_algorithm_imports(key: str) -> None:
    entry = ALGORITHMS[key]
    assert entry["reference"] and entry["requires_constraints"] is True
    path = Path(inspect.getsourcefile(entry["factory"]))
    text = path.read_text(encoding="utf-8")
    assert "Author: Kristina Valevska, MSc Eng." in text
    tree = ast.parse(text)
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    assert not any(module.startswith("pymoo.algorithms") for module in imports)


def test_constraint_pareto_relation_preserves_objective_incomparable_points() -> None:
    F = np.array([[0.0, 2.0], [2.0, 0.0], [3.0, 3.0]])
    CV = np.array([1.0, 0.0, 0.0])
    np.testing.assert_array_equal(constraint_pareto_mask(F, CV, constrained=True), [True, True, False])
    np.testing.assert_array_equal(constraint_pareto_mask(F, CV, constrained=False), [True, True, False])


def test_cmoea_cd_runtime_archives_and_callback() -> None:
    problem = get_problem("tnk")
    algorithm = make_cmoea_cd(pop_size=12, e1=1, e2=2, seed=7)
    generations = []
    result = minimize(problem, algorithm, ("n_gen", 2), seed=7, callback=lambda current: generations.append(current.n_gen))
    assert result.F.shape == (12, 2)
    assert algorithm.evaluator.n_eval == 36
    assert generations == [1, 2]
    assert algorithm.fa is not None and len(algorithm.fa.X) == 4
    assert algorithm.da is not None and len(algorithm.da.X) == 4
    assert algorithm.fea is not None and len(algorithm.fea.X) == 12


def test_cmobr_push_pull_transition_and_evaluation_accounting() -> None:
    problem = get_problem("tnk")
    algorithm = make_cmobr(pop_size=12, stagnation_window=2, change_threshold=1e9, seed=5)
    result = minimize(problem, algorithm, ("n_gen", 3), seed=5)
    assert result.F.shape == (12, 2)
    assert algorithm.stage == "pull"
    assert algorithm.population2 is not None
    assert algorithm.evaluator.n_eval == 60
    assert algorithm.archive is not None and len(algorithm.archive.X) == 12


def test_cmobr_c1dtlz3_callback_exposes_full_three_objective_population() -> None:
    problem = PROBLEMS["c1dtlz3"]["factory"]()
    algorithm = make_cmobr(pop_size=12, seed=5)
    payloads = []
    callback = make_generation_callback(payloads.append, problem, algorithm_key="cmobr")

    minimize(problem, algorithm, ("n_gen", 2), seed=5, callback=callback)

    assert len(payloads) == 2
    for payload in payloads:
        population = payload["population_F"]
        assert population.shape == (12, 3)
        assert np.isfinite(population).all()
        assert payload["diagnostics"] == []


def test_cmobr_helpers() -> None:
    history = [np.array([1.0, 2.0]), np.array([0.9, 2.2]), np.array([0.8, 2.0])]
    assert relative_front_change(history, 2) == pytest.approx(0.2)
    assert epsilon_relaxation(1.0, 1.0, 0.5, 0.2) == pytest.approx(0.95)
    assert epsilon_relaxation(1.0, 1.0, 1.0, 0.9) == pytest.approx(0.0)


@pytest.mark.parametrize("key", ["cmoea_cd", "cmobr"])
def test_algorithms_require_constraints(key: str) -> None:
    with pytest.raises(AlgorithmProblemCompatibilityError, match="requires a benchmark"):
        validate_algorithm_problem(ALGORITHMS[key], get_problem("zdt1"))


@pytest.mark.parametrize("factory,kwargs", [(make_cmoea_cd, {"e1": 3, "e2": 3}), (make_cmobr, {"stagnation_window": 2})])
def test_short_runs_are_reproducible(factory, kwargs) -> None:
    problem = get_problem("tnk")
    first = factory(pop_size=12, seed=11, **kwargs)
    second = factory(pop_size=12, seed=11, **kwargs)
    a = minimize(problem, first, ("n_gen", 2), seed=11)
    b = minimize(problem, second, ("n_gen", 2), seed=11)
    np.testing.assert_allclose(a.X, b.X)
    np.testing.assert_allclose(a.F, b.F)

